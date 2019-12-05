"""
A tornado gen_test using @testing.gen_test decorator.
"""

from tornado import testing

from my_app import make_application


class TestMyTornadoApp(testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_application()

    @testing.gen_test
    async def test_ping_route(self):
        response = await self.fetch("/ping")
        assert response.body == b"pong"
