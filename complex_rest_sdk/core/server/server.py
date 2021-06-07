from bottle import Bottle, request, response, HTTPError
from . error_rest_plugin import ErrorsRestPlugin
from . import status as http_status


class Server:
    def __init__(self, host, port, debug=False):
        """
        :param host: Host address
        :param port: Listening port
        :param workers: Number of processes to start
        """
        self._host = host
        self._port = port
        self._debug = debug

        self._app = Bottle()
        self._app.install(ErrorsRestPlugin())

    def _error_response(self, code, message):
        """
        Log errors and return error response to the client
        :param code: HTTP status code
        :param message: error message
        """
        self.log.warning(f'Response with error: {message}')
        raise HTTPError(
            status=code, body={'status': 'error', 'error_message': message}
        )

    def _normal_response(self, load=None, status=http_status.HTTP_200_OK, headers=None):
        """
        Makes ordinary json response with given load, status and headers
        :param load: dictionary for body content
        :param status: http status
        :param headers: dictionary with http headers
        """
        if not load:
            load = {}
        response.status = status
        response.content_type = 'application/json'
        if headers:
            for key, value in headers.items():
                response.set_header(key, value)
        return load

    def add_route(self, url_path, http_method, callback):
        """
        Adds bottle routes for url path and callback
        """
        self._app.route(url_path, method=http_method, callback=callback)

    def get_app(self):
        return self._app

    def wsgi(self, environ, start_response):
        """
        Calls bottle wsgi function
        """
        return self._app.wsgi(environ, start_response)

    def run(self):
        self._app.run(
            host=self._host, port=self._port, debug=self._debug,
        )
