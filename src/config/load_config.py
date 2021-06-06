from configparser import ConfigParser


def get_config_map(filename):
    config_map = {}
    config = ConfigParser()
    config.read(filename, encoding='UTF-8')
    config_map["url_array"] = \
        config.get("setting", "url_array").split(",")
    config_map["area_array"] = \
        config.get("setting", "area_array").split(",")
    return config_map
