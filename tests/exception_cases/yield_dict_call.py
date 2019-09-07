"""
Yielding a dict of futures
(https://www.tornadoweb.org/en/branch3.2/releases/v3.2.0.html#tornado-gen)
added in tornado 3.2 is unsupported by the codemod. This file has not been
modified. Manually update to supported syntax before running again.
"""
from tornado import gen


@gen.coroutine
def get_user_friends_and_relatives(user_id):
    users = yield dict(
        friends=fetch("/friends", user_id), relatives=fetch("/relatives", user_id)
    )
    raise gen.Return(users)
