"""
A tornado gen_test using @tornado.testing.gen_test decorator.
"""

import tornado

from my_app import make_application


class TestMyTornadoApp(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_application()

    @tornado.testing.gen_test
    async def test_ping_route(self):
        response = await self.fetch("/ping")
        assert response.body == b"pong"
