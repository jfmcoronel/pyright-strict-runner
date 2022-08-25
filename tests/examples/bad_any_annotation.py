from typing import Any

def fib(n: Any) -> Any:
    if n <= 1:
        return n

    x: Any = n + "1"
    print(x)

    return fib(n - 2) + fib(n - 1)
