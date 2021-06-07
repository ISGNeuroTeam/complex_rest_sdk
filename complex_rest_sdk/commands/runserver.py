import logging
from .basecommand import BaseCommand, CommandError
from rest.dev_server import PluginDevServer


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--port', dest='port',
            help='server port',
            default=8080
        )
        parser.add_argument(
            '--debug', dest='debug', action='store_true',
            help='bottle debug regime', default=True
        )

    def handle(self, *args, **options):
        self.create_dev_logger()
        self.run_server(options['port'], options['debug'])

    @staticmethod
    def create_dev_logger():
        """
        Configure logging module
        """
        logging.basicConfig(
            level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s'
        )

    @staticmethod
    def run_server(port, debug):
        server = PluginDevServer('localhost', port, debug=debug)
        server.run()

