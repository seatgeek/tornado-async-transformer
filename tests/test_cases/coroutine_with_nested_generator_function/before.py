"""
A coroutine with a nested, non-coroutine generator function.
"""
from typing import List

from tornado import gen


@gen.coroutine
def save_users(users):
    def build_user_ids(users):
        for user in users:
            yield "{}-{}".format(user.first_name, user.last_name)

    for user_id in build_user_ids(users):
        yield fetch("POST", user_id)
