import configparser

from pathlib import Path
from core.settings.ini_config import merge_ini_config_with_defaults

default_ini_config = {
    'logging': {
        'level': 'INFO'
    },
    'db_conf': {
        'host': 'localhost',
        'port': '5432',
        'database':  '{{plugin_name}}',
        'user': '{{plugin_name}}',
        'password': '{{plugin_name}}'
    }
}

config_parser = configparser.ConfigParser()

config_parser.read(Path(__file__).parent / '{{plugin_name}}.conf')

ini_config = merge_ini_config_with_defaults(config_parser, default_ini_config)
