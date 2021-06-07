import json
from rest.dev_server import PluginDevServer
from rest.response import Response


class ClientHandler:
    def __init__(self):
        self.server = PluginDevServer('localhost', 80)
        self.status = None
        self.headers = None

    def start_response(self, status, headers):
        self.status = status
        self.headers = headers

    def __call__(self, environ):
        response = self.server.wsgi(environ, self.start_response)

        status = int(self.status.split(' ')[0])
        headers = dict(self.headers)
        binary = b''.join([chunk for chunk in response])
        data = json.loads(binary)
        return Response(data, status, headers)
