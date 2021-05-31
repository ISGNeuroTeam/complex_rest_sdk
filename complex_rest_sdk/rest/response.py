from core.server import status


class Response:
    def __init__(self, data, status=status.HTTP_200_OK, headers=None):
        """
        :param load: python dictionary with default python types
        :param st: http status code
        """
        self.data = data
        self.status = status
        self.headers = headers or {}
