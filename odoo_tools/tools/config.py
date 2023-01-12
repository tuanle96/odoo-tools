import configparser
import json


def parse_config(config):
    cfg = configparser.ConfigParser()

    cfg.read(config)

    # Convert the config parser object to a dictionary
    config_dict = {section: dict(cfg.items(section))
                   for section in cfg.sections()}

    return config_dict


def parse_odoo_config(config):
    cfg = parse_config(config)

    odoo_conf = cfg.get('odoo', {})
    odoo_host = odoo_conf.get('host')
    odoo_port = odoo_conf.get('port')
    odoo_user = odoo_conf.get('user')
    odoo_password = odoo_conf.get('password')
    odoo_version = odoo_conf.get('version')
    odoo_database = odoo_conf.get('database_name')
    return {
        'host': odoo_host,
        'port': int(odoo_port),
        'user': odoo_user,
        'password': odoo_password,
        'version': odoo_version,
        'database_name': odoo_database
    }


def parse_database_config(config):
    cfg = parse_config(config)

    database_conf = cfg.get('database', {})

    database_host = database_conf.get('host')
    database_port = database_conf.get('port')
    database_user = database_conf.get('user')
    database_password = database_conf.get('password')
    database_name = database_conf.get('name')

    ssh_tunnel = database_conf.get('ssh_tunnel', False)
    ssh_host = database_conf.get('ssh_host')
    ssh_port = database_conf.get('ssh_port')
    ssh_user = database_conf.get('ssh_user')
    ssh_password = database_conf.get('ssh_password')
    ssh_is_key = database_conf.get('ssh_is_key', False)
    ssh_private_key = database_conf.get('ssh_private_key')

    return {
        'host': database_host,
        'port': database_port,
        'user': database_user,
        'password': database_password,
        'name': database_name,
        'ssh_tunnel': ssh_tunnel,
        'ssh_host': ssh_host,
        'ssh_port': ssh_port,
        'ssh_user': ssh_user,
        'ssh_password': ssh_password,
        'ssh_is_key': ssh_is_key,
        'ssh_private_key': ssh_private_key
    }
