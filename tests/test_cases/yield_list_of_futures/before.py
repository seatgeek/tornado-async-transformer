"""
A coroutine that yields a list of yieldable objects.
See: https://www.tornadoweb.org/en/stable/gen.html.
"""
from tornado import gen


@gen.coroutine
def get_two_users(user_id_1, user_id_2):
    response_1, reponse_2 = yield [fetch(user_id_1), fetch(user_id_2)]
    raise gen.Return((response_1.user, response_2.user))
