"""
A coroutine that returns a dict that spanning multiple lines.
"""
from tornado import gen

async def fetch_user(id):
    response = await fetch(id)
    return {
        'user': response.user,
        'source': 'user-api'
    }
