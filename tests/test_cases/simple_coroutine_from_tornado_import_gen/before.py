"""
A simple coroutine.
"""
from tornado import gen


@gen.coroutine
def call_api():
    response = yield fetch()
    if response.status != 200:
        raise BadStatusError()
    raise gen.Return(response.data)
