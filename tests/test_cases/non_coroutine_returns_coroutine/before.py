"""
A non-coroutine function that returns a coroutine.
"""
from tornado import gen


def make_simple_fetch(url: str):
    @gen.coroutine
    def my_simple_fetch(body):
        response = yield fetch(url, body)
        raise gen.Return(response.body)

    return my_simple_fetch

