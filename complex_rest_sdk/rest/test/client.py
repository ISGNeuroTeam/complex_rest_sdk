import json
import re

from io import BytesIO
from http import cookies
from urllib.parse import urlencode, urlparse, unquote_to_bytes

from rest.json import JSONEncoder
from rest.utils.encoding import force_bytes

from .client_handler import ClientHandler


JSON_CONTENT_TYPE_RE = re.compile(r'^application\/(.+\+)?json')


class FakePayload:
    """
    A wrapper around BytesIO that restricts what can be read since data from
    the network can't be sought and cannot be read outside of its content
    length. This makes sure that views can't do anything under the test client
    that wouldn't work in real life.
    """
    def __init__(self, content=None):
        self.__content = BytesIO()
        self.__len = 0
        self.read_started = False
        if content is not None:
            self.write(content)

    def __len__(self):
        return self.__len

    def read(self, num_bytes=None):
        if not self.read_started:
            self.__content.seek(0)
            self.read_started = True
        if num_bytes is None:
            num_bytes = self.__len or 0
        assert self.__len >= num_bytes, "Cannot read more than the available bytes from the HTTP incoming data."
        content = self.__content.read(num_bytes)
        self.__len -= num_bytes
        return content

    def write(self, content):
        if self.read_started:
            raise ValueError("Unable to write a payload after it's been read")
        content = force_bytes(content)
        self.__content.write(content)
        self.__len += len(content)


class APIClient:
    def __init__(self, raise_request_exception=True, **defaults):
        self.json_encoder = JSONEncoder
        self.defaults = defaults
        self.cookies = cookies.SimpleCookie()
        self.errors = BytesIO()

        self.handler = ClientHandler()
        self.raise_request_exception = raise_request_exception
        self.exc_info = None
        self.extra = None

    def _base_environ(self, **request):
        """
        The base environment for a request.
        """
        # This is a minimal valid WSGI environ dictionary, plus:
        # - HTTP_COOKIE: for cookie support,
        # - REMOTE_ADDR: often useful, see #8551.
        # See https://www.python.org/dev/peps/pep-3333/#environ-variables
        print(self.cookies.values())
        return {
            'HTTP_COOKIE': '; '.join(sorted(
                '%s=%s' % (morsel.key, morsel.coded_value)
                for morsel in self.cookies.values()
            )),
            'PATH_INFO': '/',
            'REMOTE_ADDR': '127.0.0.1',
            'REQUEST_METHOD': 'GET',
            'SCRIPT_NAME': '',
            'SERVER_NAME': 'testserver',
            'SERVER_PORT': '80',
            'SERVER_PROTOCOL': 'HTTP/1.1',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'http',
            'wsgi.input': FakePayload(b''),
            'wsgi.errors': self.errors,
            'wsgi.multiprocess': True,
            'wsgi.multithread': False,
            'wsgi.run_once': False,
            **self.defaults,
            **request,
        }

    def _get_path(self, parsed):
        path = parsed.path
        # If there are parameters, add them
        if parsed.params:
            path += ";" + parsed.params
        path = unquote_to_bytes(path)
        # Replace the behavior where non-ASCII values in the WSGI environ are
        # arbitrarily decoded with ISO-8859-1.
        # Refs comment in `get_bytes_from_wsgi()`.
        return path.decode('iso-8859-1')

    def _encode_data(self, data, content_type):
        """
        Return encoded JSON if data is a dict, list, or tuple and content_type
        is application/json.
        """
        should_encode = JSON_CONTENT_TYPE_RE.match(content_type) and isinstance(data, (dict, list, tuple))
        return json.dumps(data, cls=self.json_encoder) if should_encode else data

    def request(self, **request):
        """
        The master request method. Compose the environment dictionary and pass
        to the handler, return the result of the handler. Assume defaults for
        the query environment, which can be overridden using the arguments to
        the request.
        """
        environ = self._base_environ(**request)

        response = self.handler(environ)

        return response

    def get(self, path, data=None, **extra):
        r = {
            'QUERY_STRING': urlencode(data or {}, doseq=True),
        }
        if not data and '?' in path:
            # Fix to support old behavior where you have the arguments in the
            # url. See #1461.
            query_string = force_bytes(path.split('?')[1])
            query_string = query_string.decode('iso-8859-1')
            r['QUERY_STRING'] = query_string
        r.update(extra)
        return self.generic('GET', path, **r)

    def post(self, path, data, content_type, **extra):
        data = self._encode_data(data, content_type)
        return self.generic('POST', path, data, content_type, **extra)

    def put(self, path, data, content_type, **extra):
        data = self._encode_data(data, content_type)
        return self.generic('PUT', path, data, content_type, **extra)

    def patch(self, path, data, content_type, **extra):
        data = self._encode_data(data, content_type)
        return self.generic('PATCH', path, data, content_type, **extra)

    def delete(self, path, data=None, content_type='application/json', **extra):
        data = self._encode_data(data, content_type)
        return self.generic('DELETE', path, data, content_type, **extra)

    def options(self, path, data=None, content_type='application/json', **extra):
        data = self._encode_data(data, content_type)
        return self.generic('OPTIONS', path, data, content_type, **extra)

    def generic(self, method, path, data='',
                content_type='application/json', secure=False,
                **extra):
        """Construct an arbitrary HTTP request."""
        parsed = urlparse(str(path))  # path can be lazy
        data = force_bytes(data)
        r = {
            'PATH_INFO': self._get_path(parsed),
            'REQUEST_METHOD': method,
            'SERVER_PORT': '443' if secure else '80',
            'wsgi.url_scheme': 'https' if secure else 'http',
        }
        if data:
            r.update({
                'CONTENT_LENGTH': str(len(data)),
                'CONTENT_TYPE': content_type,
                'wsgi.input': FakePayload(data),
            })
        r.update(extra)
        # If QUERY_STRING is absent or empty, we want to extract it from the URL.
        if not r.get('QUERY_STRING'):
            # WSGI requires latin-1 encoded strings. See get_path_info().
            query_string = parsed[4].encode().decode('iso-8859-1')
            r['QUERY_STRING'] = query_string
        return self.request(**r)

