"""
A few coroutines that have multiple decorators in addition to @gen.coroutine.
"""
from tornado import gen
from util.decorators import route, deprecated, log_args

@gen.coroutine
@route("/user/:id")
def user_page(id):
    user = yield get_user(id)
    user_page = "<div>{}</div>".format(user.name)
    raise gen.Return(user_page)


@deprecated
@gen.coroutine
@log_args
def get_user(id):
    response = yield fetch(id)
    raise gen.Return(response.user)
