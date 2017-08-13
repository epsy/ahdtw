class Promise:
    def __init__(self):
        self.success = None
        self.result = None

    def set_success(self, value):
        self.success = True
        self.result = value
        return self

    def set_exception(self, exc):
        self.success = False
        self.result = exc
        return self

    def __await__(self):
        return (yield self)


cache = {}


async def fib(n):
    if n in cache:
        return cache[n]
    if n < 2:
        return n
    result = await add_coro(fib(n - 2)) + await add_coro(fib(n - 1))
    cache[n] = result
    return result


coros = []


def add_coro(coro):
    kickoff_promise = Promise().set_success(None)
    result_promise = Promise()
    coros.append((coro, kickoff_promise, result_promise))
    return result_promise


def run(initial_coro):
    final_result = add_coro(initial_coro)
    while final_result.success is None:
        for i, (coro, awaited_promise, result_promise) in enumerate(coros):
            if awaited_promise.success is not None:
                coros.pop(i)
                break
        else:
            raise RuntimeException("Deadlock!")
        try:
            if awaited_promise.success:
                new_promise = coro.send(awaited_promise.result)
            else:
                new_promise = coro.throw(awaited_promise.result)
        except StopIteration as e:
            result_promise.set_success(e.value)
        except BaseException as e:
            result_promise.set_exception(e)
        else:
            coros.append((coro, new_promise, result_promise))
    if final_result.success:
        return final_result.result
    else:
        raise final_result.result
