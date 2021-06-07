from importlib import import_module
from core.settings import PLUGIN_DEV_DIR
from .basecommand import BaseCommand, CommandError

from jinja2 import Template


class Command(BaseCommand):
    """
    Management utility to create plugins
    """
    help = 'Creates plugin template.'

    def add_arguments(self, parser):
        parser.add_argument(
            'plugin_name',
            help='Plugin name',
        )

    @staticmethod
    def validate_name(name):
        """
        Validates plugin name name, raises CommandError if plugin name is invalid
        """
        if name is None:
            raise CommandError('you must provide a name')
        # Check it's a valid directory name.
        if not name.isidentifier():
            raise CommandError(
                f'{name} is not a valid plugin name. Please make sure the' 
                'name is a valid identifier.'
            )
        # Check it cannot be imported.
        try:
            import_module(name)
        except ImportError:
            pass
        else:
            raise CommandError(
                f'{name} conflicts with the name of an existing Python '
                'module and cannot be used as a plugin name. Please try '
                'another name.'
            )
        invalid_names = ['rest_auth', 'django', 'djangorestframework']
        if name in invalid_names:
            raise CommandError('Ivalid name. Please try another name.')

    def handle(self, *args, **options):
        plugin_name = options['plugin_name']

        self.validate_name(plugin_name)
        context = {'plugin_name': plugin_name}

        # directory with plugin template
        plugin_template_dir = self.BASE_DIR / 'core' / 'templates' / 'plugin_template'

        # directory with rendered plugins
        plugin_dev_dir = PLUGIN_DEV_DIR
        plugin_dev_dir.mkdir(exist_ok=True)

        self.render_dir(plugin_template_dir, plugin_dev_dir / plugin_name, context)

        print(f'Plugin with name {plugin_name} created')

    def render_dir(self, template_directory_path, plugin_directory_path, context):
        print(f'Create directory {str(template_directory_path)}')
        # create directory plugin_directory_path
        plugin_directory_path.mkdir()

        # iterate through template directory and call render function for all files and directories
        for child in template_directory_path.iterdir():
            rendered_name = Template(str(child.name)).render(context) + ''
            if child.is_dir():
                self.render_dir(
                    template_directory_path / str(child.name),
                    plugin_directory_path / rendered_name,
                    context
                )
            else:
                self.render_file(
                    template_directory_path / str(child.name),
                    plugin_directory_path / rendered_name,
                    context
                )

    @staticmethod
    def render_file(template_file, rendered_file, context):
        print(f'Create file {str(rendered_file)}')
        rendered_file.write_text(Template(template_file.read_text()).render(context))



