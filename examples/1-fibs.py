def recur_fib(n):
    if n < 2:
        return n
    return recur_fib(n-1) + recur_fib(n-2)

def iter_fib(n):
    n_2 = 0
    n_1 = 1
    for _ in range(n - 1):
        n_2, n_1 = n_1, n_2+n_1
    return n_1
