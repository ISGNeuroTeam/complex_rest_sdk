import sys
import unittest

from core.settings import PLUGIN_DEV_DIR
from .basecommand import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'plugin_name',
            help='plugin name for testing',
        )
        parser.add_argument(
            'test_path', nargs='?', default=None,
            help='Path to test class or test method. Example:  test_example.TestExample.test_hello'
        )

    def handle(self, *args, **options):
        sys.path.insert(0, str(PLUGIN_DEV_DIR))
        plugin_name = options['plugin_name']
        test_path = options['test_path']
        if not test_path:
            testsuite = unittest.TestLoader().discover(PLUGIN_DEV_DIR / plugin_name / 'tests')
        else:
            testsuite = unittest.TestLoader().loadTestsFromName(f'{plugin_name}.tests.{test_path}')

        unittest.TextTestRunner(verbosity=1).run(testsuite)




