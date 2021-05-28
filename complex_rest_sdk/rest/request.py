class Request:
    def __init__(self, url_params, body):
        """
        :param url_params: dict like object with url params
        :param body: dict like object with body content
        """
        self.data = body
        self.GET = url_params
