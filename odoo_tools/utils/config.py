import configparser
import json


def convert_to_dict(config):
    cfg = configparser.ConfigParser()

    cfg.read(config)

    # Convert the config parser object to a dictionary
    config_dict = {section: dict(cfg.items(section))
                   for section in cfg.sections()}

    # Convert the dictionary to a JSON string
    json_str = json.dumps(config_dict)

    return json_str

def get_database_config(config):
    pass


def get_odoo_config(config):
    pass
