"""
A simple coroutine in a module that imports the tornado package.
"""
import tornado


async def call_api():
    response = await fetch()
    if response.status != 200:
        raise BadStatusError()
    return response.data
