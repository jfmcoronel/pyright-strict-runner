from typing import Any

def fib(n):  # type: (Any) -> Any
    if n <= 1:
        return n

    return fib(n - 2) + fib(n - 1)
