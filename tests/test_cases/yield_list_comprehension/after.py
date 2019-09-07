"""
A coroutine that yields a list comprehension that creates a list of yieldable objects.
See: https://www.tornadoweb.org/en/stable/gen.html.
"""
from tornado import gen
import asyncio


async def get_users(user_ids):
    users = await asyncio.gather(*[fetch(user_id) for user_id in user_ids])
    return users
