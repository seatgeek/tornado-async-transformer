"""
A simple coroutine.
"""
from tornado import gen


async def call_api():
    response = await fetch()
    if response.status != 200:
        raise BadStatusError()
    return response.data
