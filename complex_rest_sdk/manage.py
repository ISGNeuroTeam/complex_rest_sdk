import sys
import importlib

from pathlib import Path
from commands.basecommand import CommandError

BASE_DIR = Path(__file__).resolve().parent

if BASE_DIR not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def main():
    """Run administrative commands."""

    try:
        try:
            command = sys.argv[1]
        except IndexError:
            raise CommandError('Missing command name')
        module = importlib.import_module(f'commands.{command}')
    except ImportError:
        raise CommandError('Command not found')

    command = module.Command()
    command.run_from_argv(sys.argv)


if __name__ == '__main__':
    main()
