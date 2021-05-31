class Request:
    def __init__(self, url_params, body, headers=None):
        """
        :param url_params: dict like object with url params
        :param body: dict like object with body content
        :param headers: dict like object with http headers, key is a stings and value is a string
        """
        self.data = body
        self.GET = url_params
        self.headers = headers or {}
