"""
A simple coroutine that contains a nested coroutine.
"""
from tornado import gen


@gen.coroutine
def call_api():
    @gen.coroutine
    def nested_callback(response):
        if response.status != 200:
            raise gen.Return(response)

        body = yield response.json()
        if body["api-update-available"]:
            print("note: update api")
        raise gen.Return(response)

    response = yield fetch(middleware=nested_callback)
    if response.status != 200:
        raise BadStatusError()
    raise gen.Return(response.data)
