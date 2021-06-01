import sys

from importlib import import_module
from pathlib import Path

from bottle import request as bottle_request

from core.server import Server
from rest.request import Request
from rest.exceptions import InvalidPlugin


class PluginDevServer(Server):
    def __init__(self, plugins_dir, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugins_dir = Path(plugins_dir)
        self._load_plugins()

    def _load_plugins(self):
        """
        Read plugin_dev directory, import urlpatterns from  urls.py for all plugin, make bottle routes
        """
        for p in self.plugins_dir.iterdir():
            if p.is_dir():
                plugin_name = p.name
                sys.path.insert(1, str(self.plugins_dir / plugin_name))
                self._add_plugins_env_dirs_to_sys_path(plugin_name)
                self._make_routes(plugin_name)

    def _add_plugins_env_dirs_to_sys_path(self, plugin_name):
        """
        Finds and adds all plugin virtual environment directories to sys.path
        """
        # virtual environment relative paths
        venv_relative_dirs_list = [
            f'lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages',
            f'lib/python{sys.version_info.major}{sys.version_info.minor}.zip',
            f'lib/python{sys.version_info.major}.{sys.version_info.minor}',
            f'lib/python{sys.version_info.major}.{sys.version_info.minor}/lib-dynload',
        ]

        venv_dir = self.plugins_dir / plugin_name / 'venv'
        if venv_dir.exists():
            sys.path.extend(
                list(
                    map(
                        lambda x: str(venv_dir / x),
                        venv_relative_dirs_list
                    )
                )
            )

    def _make_routes(self, plugin_name):
        """
        Makes bottle routes for plugin
        """
        paths = self._get_plugin_paths(plugin_name)
        for path in paths:
            # make bottle route for each http method
            abs_url_pattern = self._get_absolute_url_pattern(plugin_name, path.pattern)
            for http_method in path.view.http_method_names:
                callback = self._get_bottle_handler_from_view(path.view, http_method)
                self.add_route(abs_url_pattern, http_method, callback)

    @staticmethod
    def _get_plugin_paths(plugin_name):
        """
        Reads plugin urls.py and returns urlpatterns variable
        :return:
        list of paths
        """
        try:
            urls = import_module(f'{plugin_name}.urls')
        except ImportError as exc:
            if 'urls' in str(exc):
                raise InvalidPlugin('Can\'t import urls.py from plugin directory')
            else:
                raise exc

        try:
            urlpatterns = urls.urlpatterns
        except AttributeError as e:
            raise InvalidPlugin('urlpatterns variable not found in urls.py') from e
        return urlpatterns

    def _get_absolute_url_pattern(self, plugin_name, url_pattern):
        """
        Returns string /<plugin_name>/<api_version>/url_pattern
        """
        api_version = self._get_plugin_api_version(plugin_name)
        return f'/{plugin_name}/v{api_version}/{url_pattern}'

    def _get_plugin_api_version(self, plugin_name):
        """
        Reads plugin setup.py
        :param plugin_name:
        :return:
        api version
        """
        setup_file = self.plugins_dir / plugin_name / 'setup.py'
        try:
            with setup_file.open('r') as f:
                for line in f:
                    if '__api_version__' in line:
                        return line.partition('=')[2].strip().strip('"')
        except OSError:
            raise InvalidPlugin('Not found __api_version__ in setup.py. Did you create setup.py?')

        return '1'

    def _get_bottle_handler_from_view(self, view, http_method):
        def _bottle_handler(*args, **kwargs):
            # make request object from bottle request object
            request = Request(bottle_request.GET, bottle_request.json, bottle_request.headers)

            # calling view method
            view_obj = view()
            view_handler = getattr(view_obj, http_method)
            response = view_handler(request, *args, **kwargs)
            # return bottle response
            return self._normal_response(response.data, status=response.status, headers=response.headers)
        return _bottle_handler


