def fib(n):#     pyright:          ignore  
    if n <= 1:      #  pyright:          ignore   
        return n # pyright: ignore

    return fib(n - 2) + fib(n - 1) #pyright:ignore
