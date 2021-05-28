from core.server import Server

from bottle import request as bottle_request, Response as BottleResponse

from .request import Request


class PluginDevServer(Server):
    def __init__(self, plugin_name, api_version, paths, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._plugin_name = plugin_name
        self._api_version = api_version
        self._make_routes(paths)

    def _make_routes(self, paths):
        """
        Makes bottle routes from paths objects
        :param paths: list of paths objects
        """
        for path in paths:
            # make bottle route for each http method
            abs_url_pattern = self._get_absolute_url_pattern(path.pattern)
            for http_method in path.view.http_method_names:
                callback = self._get_bottle_handler_from_view(path.view, http_method)
                self.add_route(abs_url_pattern, http_method, callback)

    def _get_absolute_url_pattern(self, url_pattern):
        """
        Returns string /<plugin_name>/<api_version>/url_pattern
        """
        return f'/{self._plugin_name}/v{self._api_version}/{url_pattern}'

    def _get_bottle_handler_from_view(self, view, http_method):
        def _bottle_handler(*args):
            # make request object from bottle request object
            request = Request(bottle_request.GET, bottle_request.json)

            # calling view method
            view_obj = view()
            view_handler = getattr(view_obj, http_method)
            response = view_handler(request, *args)
            print(response.data)
            # return bottle response
            return self._normal_response(response.data, status=response.status)
        return _bottle_handler


