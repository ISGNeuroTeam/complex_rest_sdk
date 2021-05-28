class APIView:
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    @classmethod
    def as_view(cls):
        return cls
