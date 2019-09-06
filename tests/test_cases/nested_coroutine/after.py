"""
A simple coroutine that contains a nested coroutine.
"""
from tornado import gen


async def call_api():
    async def nested_callback(response):
        if response.status != 200:
            return response

        body = await response.json()
        if body["api-update-available"]:
            print("note: update api")
        return response

    response = await fetch(middleware=nested_callback)
    if response.status != 200:
        raise BadStatusError()
    return response.data
