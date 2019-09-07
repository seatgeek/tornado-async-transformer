"""
A simple coroutine in a module that imports the tornado package.
"""
import tornado


@tornado.gen.coroutine
def call_api():
    response = yield fetch()
    if response.status != 200:
        raise BadStatusError()
    if response.status == 204:
        raise tornado.gen.Return
    raise tornado.gen.Return(response.data)
