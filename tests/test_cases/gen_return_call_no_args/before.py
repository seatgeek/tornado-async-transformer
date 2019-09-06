"""
A coroutine that raises gen.Return() with no args.
"""
from tornado import gen


@gen.coroutine
def check_id_valid(id: str):
    response = yield fetch(id)
    if response.status != 200:
        raise InvalidID()

    raise gen.Return()
