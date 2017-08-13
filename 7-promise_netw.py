import traceback
import collections
import socket
import select


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


async def echo_server(conn):
    text = await read(conn)
    while text.strip() != b'bye':
        print(f"Received: {text}")
        await write(conn, b'echo: ' + text)
        text = await read(conn)
    conn.close()


async def launch_server(func, port):
    sock = socket.socket(type=socket.SOCK_STREAM | socket.SOCK_NONBLOCK)
    sock.bind(('127.0.0.1', port))
    sock.listen()
    print(f"Listening on port {port}")
    while True:
        await readability(sock)
        conn, addr = sock.accept()
        print(f'Connected to {addr}')
        add_coro(func(conn))


coros = []
reads = collections.defaultdict(list)
writes = collections.defaultdict(list)


def add_coro(coro):
    kickoff_promise = Promise().set_success(None)
    result_promise = Promise()
    coros.append((coro, kickoff_promise, result_promise))
    return result_promise


def readability(fd):
    p = Promise()
    reads[fd].append(p)
    return p


def writability(fd):
    p = Promise()
    writes[fd].append(p)
    return p


async def read(f):
    await readability(f)
    return f.recv(4096)


async def write(f, s):
    await writability(f)
    return f.send(s)


def run(initial_coro):
    final_result = add_coro(initial_coro)
    while final_result.success is None:
        for i, (coro, awaited_promise, result_promise) in enumerate(coros):
            if awaited_promise.success is not None:
                coros.pop(i)
                break
        else:
            if reads or writes:
                check_socks(timeout=None)
                continue
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


def check_socks(timeout):
    rlist, wlist, _ = select.select(list(reads), list(writes), [], timeout)
    for fd in rlist:
        for p in reads.pop(fd):
            p.set_success(None)
    for fd in wlist:
        for p in writes.pop(fd):
            p.set_success(None)
