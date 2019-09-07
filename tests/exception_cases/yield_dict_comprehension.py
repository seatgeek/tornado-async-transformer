"""
Yielding a dict of futures
(https://www.tornadoweb.org/en/branch3.2/releases/v3.2.0.html#tornado-gen)
added in tornado 3.2 is unsupported by the codemod. This file has not been
modified. Manually update to supported syntax before running again.
"""
from tornado import gen


@gen.coroutine
def get_users_by_id(user_ids):
    users = yield {user_id: fetch(user_ids) for user_id in user_ids}
    raise gen.Return(users)
