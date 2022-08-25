import ast
from io import BytesIO
import subprocess
import sys
import tempfile
import tokenize
from typing import Optional, Sequence

from .project_types import CompileError, CompileSuccess


def validate_comments(code: str) -> Sequence[CompileError]:
    """Determines whether the given source code contains any Pyright-disabling comments

    Parameters
    ----------
    code : str
        Python source code to validate

    Returns
    -------
    Sequence[CompileError]
        a nonempty sequence of validation errors, or an empty one if validation succeeds
    """

    def token_to_error(token: tuple[int, str, object, object, object]) -> Optional[CompileError]:
        token_type, token_value, _, _, _ = token

        if token_type != tokenize.COMMENT:
            return None
        else:
            trimmed_text = token_value.replace(' ', '')

            if trimmed_text.startswith('#type:ignore'):
                return CompileError.TypeIgnoreError

            elif trimmed_text.startswith('#pyright:ignore'):
                return CompileError.PyrightIgnoreError

            else:
                return None

    tokens = tokenize.tokenize(BytesIO(code.encode('utf8')).readline)
    errors = [token_to_error(token) for token in tokens]
    errors = list(set(error for error in errors if error))

    return errors


def validate_comments_from_path(path: str) -> Sequence[CompileError]:
    """Determines whether the source code in the given path contains any Pyright-disabling comments

    Parameters
    ----------
    path : str
        Path to source file to validate

    Returns
    -------
    Sequence[CompileError]
        a nonempty sequence of validation errors, or an empty one if validation succeeds
    """

    with open(path, 'r') as f:
        code = f.read()

    return validate_comments(code)


def execute_python(src_path: str, python_path: str) -> None:
    """Runs the source code in the given path using the specified Python interpreter

    Parameters
    ----------
    src_path : str
        Path to source file to validate
    python_path : str
        Path to Python executable
    """

    subprocess.run([python_path, src_path], text=True)


def execute_pyright(path: str, pyright_path: str) -> tuple[subprocess.CompletedProcess[str], bool]:
    """Runs Pyright and returns both the execution result and whether
        the program passes Pyright type checking

    Parameters
    ----------
    path : str
        Path to source file to validate
    pyright_path : str
        Path to Pyright executable

    Returns
    -------
    subprocess.CompletedProcess[str]
        Result of internal call to `subprocess.run`
    bool
        True if code passes type checking, False otherwise
    """

    result = subprocess.run(
        [pyright_path, '--warnings', path], capture_output=True, text=True)

    return (result, result.returncode == 0)


def validate_pyright_from_path(path: str, pyright_path: str) -> Optional[CompileSuccess]:
    """Determines whether the source code in the given path is Pyright strict mode-compliant

    Parameters
    ----------
    path : str
        Path to source file to validate
    pyright_path : str
        Path to Pyright executable

    Returns
    -------
    Optional[CompileSuccess]
        CompileSuccess if compliant, or None otherwise
    """

    with open(path, 'r') as f:
        augmented_code = '# pyright: strict\n' + f.read()

    temp_src_file = tempfile.NamedTemporaryFile(
        suffix='.py')  # Suffix needed to be seen by Pyright

    # typer.echo(f'Created temporary file at {temp_src_file.name}')

    with open(temp_src_file.name, 'w') as f:
        f.write(augmented_code)

    _, pyright_verdict = execute_pyright(temp_src_file.name, pyright_path)

    result = CompileSuccess() if pyright_verdict else None

    return result


def validate_any_from_path(path: str) -> Optional[CompileSuccess]:
    """Determines whether the source code in the given path is free from `Any` annotation

    Parameters
    ----------
    path : str
        Path to source file to validate

    Returns
    -------
    Optional[CompileSuccess]
        CompileSuccess if code is free from `Any`, or None otherwise
    """

    def token_to_error(token: tuple[int, str, object, object, object]) -> Optional[CompileError]:
        token_type, token_value, _, _, _ = token

        if token_type != tokenize.COMMENT:
            return None
        else:
            trimmed_text = token_value.replace(' ', '')

            if trimmed_text.startswith('#type:') and 'Any' in trimmed_text:
                return CompileError.AnyAnnotationError

            else:
                return None

    def has_any_annotation(code: str):
        tree = ast.parse(code)

        for node in ast.walk(tree):
            # Side-effect: Disallows classes to be called `Any`
            if isinstance(node, ast.Name) and node.id == 'Any':
                return True

    with open(path, 'r') as f:
        code = f.read()

    tokens = tokenize.tokenize(BytesIO(code.encode('utf8')).readline)
    comment_errors = [token_to_error(token) for token in tokens]
    comment_errors = [error for error in comment_errors if error is not None]
    has_ast_errors = has_any_annotation(code)

    result = None if comment_errors or has_ast_errors else CompileSuccess()

    return result


def validate_iteration_from_path(path: str) -> Optional[CompileSuccess]:
    """Determines whether the source code in the given path is free from `for` and `while` loops

    Parameters
    ----------
    path : str
        Path to source file to validate

    Returns
    -------
    Optional[CompileSuccess]
        CompileSuccess if code is free from `for` and `while` loops, or None otherwise
    """

    def has_iteration_construct(code: str):
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.For) or isinstance(node, ast.While):
                return True

    with open(path, 'r') as f:
        code = f.read()

    result = None if has_iteration_construct(code) else CompileSuccess()

    return result


def process_main(path: str, pyright_path: str, python_path: str, forbid_iteration: bool = False):
    """Determines whether the source code in the given path is both Pyright
       strict mode-compliant and contains no Pyright-disabling constructs

    Parameters
    ----------
    path : str
        Path to source file to validate
    pyright_path : str
        Path to Pyright executable file
    python_path : str
        Path to Python executable file
    forbid_iteration : bool
        Determines whether `for` and `while` constructs are disallowed
    """

    comment_errors = validate_comments_from_path(path)
    if comment_errors:
        sys.exit('Error: Pyright-disabling comment in code; kindly remove this')

    pyright_result = validate_pyright_from_path(path, pyright_path)
    if pyright_result is None:
        sys.exit(
            'Error: Type error detected by Pyright; kindly check Pyright feedback locally')

    any_result = validate_any_from_path(path)
    if any_result is None:
        sys.exit(
            'Error: Remove all `Any` annotations')

    if forbid_iteration:
        iteration_result = validate_iteration_from_path(path)
        if iteration_result is None:
            sys.exit('Error: Remove all `for` and `while` loops')

    execute_python(path, python_path)


def main(path: str, pyright: str = 'pyright', python: str = 'python3', forbid_iteration: bool = False):
    process_main(path, pyright, python, forbid_iteration)
