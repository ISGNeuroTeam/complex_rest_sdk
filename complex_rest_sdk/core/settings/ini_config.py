def merge_ini_config_with_defaults(config, default_config):
    """
    Merge ini config with default config
    :param config: config
    :param default_config: dict with default config
    :return:
    Merged dictionary config
    """
    config = dict(config)
    for key in default_config.keys():
        default_config[key].update(config.get(key, {}))
    return default_config
