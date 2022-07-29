# pyright-strict-runner

[![Tests Status](https://github.com/jfmcoronel/pyright-strict-runner/workflows/Tests/badge.svg?branch=main&event=push)](https://github.com/jfmcoronel/pyright-strict-runner/actions?query=workflow%3ATests+branch%3Amain+event%3Apush)
[![Code Coverage](coverage.svg)](https://github.com/jfmcoronel/pyright-strict-runner/actions?query=workflow%3ATests+branch%3Amain+event%3Apush)

`pyright-strict-runner` executes only Pyright strict mode-compliant Python scripts to be executed. Scripts with Pyright-disabling comments are also denied execution.

## Dependencies

https://github.com/microsoft/pyright

## Installation

```
pip install git+https://github.com/jfmcoronel/pyright-strict-runner
```

## Usage

```
python -m pyright-strict-runner <path-to-py-file-to-run>
```

## Limitations

Pyright-disabling comments in imported source files are not checked.
