# pyright-strict-runner

`pyright-strict-runner` executes only Pyright strict mode-compliant Python scripts to be executed. Scripts with Pyright-disabling comments are also denied execution.

## Dependencies

https://github.com/microsoft/pyright

## Installation

```
pip install -e git+https://github.com/jfmcoronel/pyright-strict-runner
```

## Usage

```
python -m pyright-strict-runner <path-to-py-file-to-run>
```

## Limitations

Pyright-disabling comments in imported source files are not checked.
