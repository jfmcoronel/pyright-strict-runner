def fib(n: int) -> int:
    unused = 0

    if n <= 1:
        return n

    return fib(n - 2) + fib(n - 1)
