from core.server import status


class Response:
    def __init__(self, data, status=status.HTTP_200_OK, headers=None):
        """
        :param data: python dictionary with default python types
        :param status: http status code
        """
        self.data = data
        try:
            self.status_code = int(status)
        except (ValueError, TypeError):
            raise TypeError('HTTP status code must be an integer.')
        self.headers = headers or {}
