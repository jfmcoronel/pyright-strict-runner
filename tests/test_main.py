import os

import pytest

from pyright_strict_runner.main import (
    execute_python,
    process_main,
    validate_any_from_path,
    validate_comments_from_path,
    validate_pyright_from_path,
)
from pyright_strict_runner.project_types import CompileError, CompileSuccess

BASE_PATH = os.path.join('tests', 'examples')
PYRIGHT_PATH = 'pyright'


def get_path(path: str) -> str:
    return os.path.join(BASE_PATH, path)


def read_from_path(path: str) -> str:
    with open(get_path(path), 'r') as f:
        return f.read()


def test_cmdline():
    good = get_path('good.py')
    bad = get_path('bad.py')
    bad_type_ignore = get_path('bad_type_ignore.py')
    bad_pyright_ignore = get_path('bad_pyright_ignore.py')
    bad_any_annotation = get_path('bad_any_annotation.py')
    bad_any_comment = get_path('bad_any_comment.py')

    with pytest.raises(SystemExit):
        process_main(bad, 'pyright', 'python3')

    with pytest.raises(SystemExit):
        process_main(bad_type_ignore, 'pyright', 'python3')

    with pytest.raises(SystemExit):
        process_main(bad_pyright_ignore, 'pyright', 'python3')

    with pytest.raises(SystemExit):
        process_main(bad_any_annotation, 'pyright', 'python3')

    with pytest.raises(SystemExit):
        process_main(bad_any_comment, 'pyright', 'python3')

    assert process_main(good, 'pyright', 'python3') == None


def test_validate_comments():
    good = get_path('good.py')
    bad = get_path('bad.py')
    bad_type_ignore = get_path('bad_type_ignore.py')
    bad_pyright_ignore = get_path('bad_pyright_ignore.py')
    bad_any_annotation = get_path('bad_any_annotation.py')
    bad_any_comment = get_path('bad_any_comment.py')

    assert len(validate_comments_from_path(good)) == 0
    assert len(validate_comments_from_path(bad)) == 0
    assert len(validate_comments_from_path(bad_any_annotation)) == 0
    assert len(validate_comments_from_path(bad_any_comment)) == 0

    assert set(validate_comments_from_path(bad_type_ignore)) == set(
        [CompileError.TypeIgnoreError])
    assert set(validate_comments_from_path(bad_pyright_ignore)) == set(
        [CompileError.PyrightIgnoreError])


def test_validate_pyright_from_path():
    good = get_path('good.py')
    bad = get_path('bad.py')
    bad_type_ignore = get_path('bad_type_ignore.py')
    bad_pyright_ignore = get_path('bad_pyright_ignore.py')
    bad_any_annotation = get_path('bad_any_annotation.py')
    bad_any_comment = get_path('bad_any_comment.py')
    warning = get_path('warning.py')

    assert validate_pyright_from_path(good, PYRIGHT_PATH) == CompileSuccess()
    assert validate_pyright_from_path(
        bad_type_ignore, PYRIGHT_PATH) == CompileSuccess()
    assert validate_pyright_from_path(
        bad_pyright_ignore, PYRIGHT_PATH) == CompileSuccess()
    assert validate_pyright_from_path(
        bad_any_annotation, PYRIGHT_PATH) == CompileSuccess()
    assert validate_pyright_from_path(
        bad_any_comment, PYRIGHT_PATH) == CompileSuccess()

    assert validate_pyright_from_path(bad, PYRIGHT_PATH) == None
    assert validate_pyright_from_path(warning, PYRIGHT_PATH) == None


def test_validate_any_from_path():
    good = get_path('good.py')
    bad = get_path('bad.py')
    bad_type_ignore = get_path('bad_type_ignore.py')
    bad_pyright_ignore = get_path('bad_pyright_ignore.py')
    bad_any_annotation = get_path('bad_any_annotation.py')
    bad_any_comment = get_path('bad_any_comment.py')
    warning = get_path('warning.py')

    assert validate_any_from_path(good) == CompileSuccess()
    assert validate_any_from_path(bad_type_ignore) == CompileSuccess()
    assert validate_any_from_path(bad_pyright_ignore) == CompileSuccess()
    assert validate_any_from_path(bad) == CompileSuccess()
    assert validate_any_from_path(warning) == CompileSuccess()

    assert validate_any_from_path(bad_any_annotation) == None
    assert validate_any_from_path(bad_any_comment) == None


def test_execute_python(capfd: pytest.CaptureFixture[str]):
    printer = get_path('printer.py')

    execute_python(printer, 'python3')
    captured = capfd.readouterr()
    assert captured.out == 'hello 123\n'
