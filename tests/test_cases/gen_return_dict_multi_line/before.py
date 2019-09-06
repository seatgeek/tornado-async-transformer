"""
A coroutine that returns a dict that spanning multiple lines.
"""
from tornado import gen

@gen.coroutine
def fetch_user(id):
    response = yield fetch(id)
    raise gen.Return({
        'user': response.user,
        'source': 'user-api'
    })
