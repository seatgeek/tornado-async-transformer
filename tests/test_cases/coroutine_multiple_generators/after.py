"""
A few coroutines that have multiple decorators in addition to @gen.coroutine.
"""
from tornado import gen
from util.decorators import route, deprecated, log_args

@route("/user/:id")
async def user_page(id):
    user = await get_user(id)
    user_page = "<div>{}</div>".format(user.name)
    return user_page


@deprecated
@log_args
async def get_user(id):
    response = await fetch(id)
    return response.user
