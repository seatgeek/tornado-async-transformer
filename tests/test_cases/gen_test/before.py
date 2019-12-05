"""
A tornado gen_test using @gen_test decorator.
"""

from tornado.testing import gen_test, AsyncHTTPTestCase

from my_app import make_application


class TestMyTornadoApp(AsyncHTTPTestCase):
    def get_app(self):
        return make_application()

    @gen_test
    def test_ping_route(self):
        response = yield self.fetch("/ping")
        assert response.body == b"pong"
