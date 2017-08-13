class AdditionAwaitable:
    def __init__(self, *args):
        self.args = args

    def __await__(self):
        result = yield ('add', *self.args)
        return result


async def add(*args):
    result = await AdditionAwaitable(*args)
    return result


def run(coro):
    result = None
    while True:
        try:
            msg = coro.send(result)
        except StopIteration as e:
            return e
        action, *args = msg
        if action == 'add':
            result = sum(args)
        else:
            coro.throw(ValueError(action))
