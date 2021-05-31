import sys
from importlib import import_module
from .basecommand import BaseCommand, CommandError
from rest.dev_server import PluginDevServer
from rest.exceptions import InvalidPlugin


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'plugin_name',
            help='Plugin name',
        )
        parser.add_argument(
            '--port', dest='port',
            help='server port',
            default=8080
        )

    def handle(self, *args, **options):
        plugin_name = options['plugin_name']

        # plugin dir to sys path
        sys.path.insert(1, str(self.PLUGIN_DEV_DIR / plugin_name))

        # plugin virtual environment
        self.add_plugins_env_dirs_to_sys_path(plugin_name)
        self.run_server(plugin_name, options['port'])

    @staticmethod
    def get_plugin_paths(plugin_name):
        """
        Reads plugin urls.py and returns urlpatterns variable
        :return:
        list of paths
        """
        try:
            urls = import_module(f'{plugin_name}.urls')
        except ImportError:
            raise InvalidPlugin('Can\'t import urls.py from plugin directory')
        try:
            urlpatterns = urls.urlpatterns
        except AttributeError as e:
            raise InvalidPlugin('urlpatterns variable not found in urls.py') from e
        return urlpatterns

    def add_plugins_env_dirs_to_sys_path(self, plugin_name):
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

        venv_dir = self.PLUGIN_DEV_DIR / plugin_name / 'venv'
        if venv_dir.exists():
            sys.path.extend(
                list(
                    map(
                        lambda x: str(venv_dir / x),
                        venv_relative_dirs_list
                    )
                )
            )

    def get_plugin_api_version(self, plugin_name):
        """
        Reads plugin setup.py
        :param plugin_name:
        :return:
        api version
        """

        setup_file  = self.PLUGIN_DEV_DIR / plugin_name / 'setup.py'
        try:
            with setup_file.open('r') as f:
                for line in f:
                    if '__api_version__' in line:
                        return line.partition('=')[2].strip().strip('"')
        except OSError:
            raise InvalidPlugin('Not found __api_version__ in setup.py. Did you create setup.py?')

        return '1'

    def run_server(self, plugin_name, port):
        paths = self.get_plugin_paths(plugin_name)
        api_version = self.get_plugin_api_version(plugin_name)
        server = PluginDevServer(plugin_name, api_version, paths, 'localhost', port)
        server.run()

