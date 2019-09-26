from http.server import BaseHTTPRequestHandler
from exception_message_transformer import ExceptionMessageTransformer, TransformError
import json
import libcst


def transform(source: str) -> str:
    source_tree = libcst.parse_module(source)
    visited_tree = source_tree.visit(ExceptionMessageTransformer())
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
