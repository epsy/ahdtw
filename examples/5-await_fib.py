class AdditionAwaitable:
    def __init__(self, *args):
        self.args = args

    def __await__(self):
        result = yield ('add', *self.args)
        return result


async def add(*args):
    result = await AdditionAwaitable(*args)
    return result


cache = {}


async def fib(n):
    if n in cache:
        return cache[n]
    if n < 2:
        return n
    result = await AdditionAwaitable(await fib(n - 2), await fib(n - 1))
    cache[n] = result
    return result


def run(coro):
    result = None
    while True:
        try:
            msg = coro.send(result)
        except StopIteration as e:
            return e.value
        action, *args = msg
        else:
            coro.throw(ValueError(action))
