"""
gen.Task (https://www.tornadoweb.org/en/branch2.4/gen.html#tornado.gen.Task)
from tornado 2.4.1 is unsupported by this codemod. This file has not been modified.
Manually update to supported syntax before running again.
"""
import time
from tornado import gen
from tornado.ioloop import IOLoop


@gen.coroutine
def ping():
    yield gen.Task(IOLoop.instance().add_timeout, time.time() + 1.5)
    raise gen.Return("pong")
