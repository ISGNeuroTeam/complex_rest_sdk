from core.server import status


class Response:
    def __init__(self, data, st=status.HTTP_200_OK):
        """
        :param load: python dictionary with default python types
        :param st: http status code
        """
        self.data = data
        self.status = st
