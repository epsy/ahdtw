class AdditionAwaitable:
    def __init__(self, *args):
        self.args = args

    def __await__(self):
        result = yield ('add', *self.args)
        return result


async def add(*args):
    result = await AdditionAwaitable(*args)
    return result
