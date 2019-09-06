"""
A non-coroutine function that returns a coroutine.
"""
from tornado import gen


def make_simple_fetch(url: str):
    async def my_simple_fetch(body):
        response = await fetch(url, body)
        return response.body

    return my_simple_fetch

