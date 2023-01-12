# Odoo tools

This repository contains a set of tools to help you develop Odoo server.

## Install

Install the latest version of Odoo tools:

```bash

wget -O- https://raw.githubusercontent.com/tuanle96/odoo-tools/{released_version}/install | bash

```

## Usage

All commands are available in the `odoo_tools` command.

```bash

odoo_tools help

```

## All commands

All commands are available in the `odoo_tools` command with below table:

| Command | Description | Example |
| --- | --- | --- |
| `odoo_tools help` | Show help | `odoo_tools help` |
| `odoo_tools sync` | Sync exists record from source to destination | `odoo_tools sync --source-config /path/to/your/source/config.cfg --target-config /path/to/your/target/config.cfg --source-model your_model_source_name --source-table your_table_source_name --source-record-id your_record_source_id --target-model your_model_target_name --target-table your_table_target_name --source-fields /path/to/your/fields/source.cfg --target-fields /path/to/your/fields/target.cfg` |
| `odoo_tools module install` | Install Odoo module | `odoo_tools module install -c odoo.cfg --addons-path /path/to/extra/addons/modules --module your_module_name` |
| `odoo_tools module upgrade` | Upgrade Odoo module | `odoo_tools module upgrade -c odoo.cfg --addons-path /path/to/extra/addons/modules --module your_module_name` |
| `odoo_tools module uninstall` | Show Odoo tools version | `odoo_tools module uninstall` |
| `odoo_tools module list` | Show all modules in Odoo | `odoo_tools module list -c odoo.cfg` |
| `odoo_tools module info` | Show all info of module | `odoo_tools module info -m helpdesk` |
| `odoo_tools module search` | Search all modules by name | `odoo_tools module search -s helpdesk` |
| `odoo_tools module create` | Create a module scaffold | `odoo_tools module create` |
| `odoo_tools module test` | Run test for a module | `odoo_tools module test -c odoo.cfg --addons-path /path/to/extra/addons/modules --module your_module_name` |
| `odoo_tools module pull` | Pull module from git registry of odoo server | `odoo_tools module pull -c odoo.cfg` |
| `odoo_tools odoo info` | Show Odoo's server info | `odoo_tools odoo info` |
| `odoo_tools odoo shell` | Run Odoo's shell | `odoo_tools odoo shell -c odoo.cfg` |
| `odoo_tools database info` | Show Odoo's server info | `odoo_tools database info` |
| `odoo_tools database list` | Show Odoo's database list | `odoo_tools database list` |
| `odoo_tools database backup` | Backup Odoo's database | `odoo_tools database backup -db odoo_database_name` |
| `odoo_tools database restore` | Restore Odoo's database | `odoo_tools database restore -db odoo_database_name` |
| `odoo_tools database delete` | Delete Odoo's database | `odoo_tools database delete -d odoo_database_name` |
