"""
A coroutine that raises gen.Return(None).
"""
from tornado import gen


async def check_id_valid(id: str):
    response = await fetch(id)
    if response.status != 200:
        raise InvalidID()

    return None
