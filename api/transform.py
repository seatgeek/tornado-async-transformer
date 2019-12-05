"""
This file defines the REST api route for the zeit now demo site, as I
haven't been able to figure out how to nest in within the demo_site/
directory.
"""

from http.server import BaseHTTPRequestHandler
from tornado_async_transformer import TornadoAsyncTransformer, TransformError
import json
import libcst


def transform(source: str) -> str:
    source_tree = libcst.parse_module(source)
    visited_tree = source_tree.visit(TornadoAsyncTransformer())
    return visited_tree.code


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        request_raw = self.rfile.read(int(self.headers.get("Content-Length"))).decode()
        request_body = json.loads(request_raw)
        source = request_body["source"]

        try:
            transformed = transform(source)
        except Exception as e:
            transformed = repr(e)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"source": transformed}).encode())
