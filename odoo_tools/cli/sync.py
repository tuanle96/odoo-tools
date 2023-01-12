import argparse
import os
import sys

import psycopg2

from odoo_tools.tools.json import pretty_print_json
from odoo_tools.cli import Command
from odoo_tools.tools import config
from odoo_tools.models.odoo import Odoo

OPTIONAL_FIELD_ATTRIBUTES = ['relation_table', 'force_create']
REQUIRED_FIELD_ATTRIBUTES = ['name', 'type', 'value', 'store']

# odoo_tools sync --source-config /Volumes/Data/Works/Voltrans/saleshub-database-migration/odoo_tools/config-source.cfg --target-config /Volumes/Data/Works/Voltrans/saleshub-database-migration/odoo_tools/config-target.cfg --source-model res.users --source-table res_users --source-record-id 3 --target-model res.users --target-table res_users --source-fields /Volumes/Data/Works/Voltrans/saleshub-database-migration/odoo_tools/fields-source.cfg --target-fields /Volumes/Data/Works/Voltrans/saleshub-database-migration/odoo_tools/fields-target.cfg


class Sync(Command):
    """Sync a record from a source database to a destination database (default command)"""

    def __init__(self):
        super(Sync, self).__init__()

        self.source_instance = None
        self.target_instance = None

    def sync_record(self, new_values, model, table, target_record_id=None):
        print(f'Updating values to target table {table} and model {model}...')
        pretty_print_json(new_values)

        """
    
            structure of data

            data = {
                'id': {
                    'name': 'id',
                    'type': 'integer',
                    'value': 1
                },
                'name': {
                    'name': 'name',
                    'type': 'char',
                    'value': 'test'
                },
                'company_ids': {
                    'name': 'company_ids',
                    'type': 'many2many',
                    'value': [1, 2, 3]
                },
                'partner_id': {
                    'name': 'partner_id',
                    'type': 'many2one',
                    'value': 1
                }
            """

        try:

            self.target_instance.database.autocommit = False
            cursor = self.target_instance.database.cursor()

            # build sql query base on data params, model and table
            # after that execute query in transaction mode
            sql_query = 'UPDATE {table} SET '.format(table=table)
            for field in new_values:
                # check if field is stored in data, if not, skip it
                if 'store' not in new_values[field] or not new_values[field]['store']:
                    continue

                """
                boolean
                monetary
                datetime
                many2many
                many2one
                selection
                integer
                html
                many2one_reference
                text
                one2many
                reference
                binary
                float
                date
                char
                """

                if new_values[field]['type'] == 'boolean':
                    sql_query += '{field} = {value}, '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'monetary':
                    sql_query += '{field} = {value}, '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'datetime':
                    sql_query += '{field} = \'{value}\', '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'many2many':
                    # if type of field is many2many, we need to delete all records in relation table, after that insert new records
                    relation_table = new_values[field]['relation_table']
                    column1 = new_values[field]['relation_col1']
                    column2 = new_values[field]['relation_col2']

                    # delete all records in relation table
                    sql_query_delete = 'DELETE FROM {relation_table} WHERE {field} = {id}'.format(
                        relation_table=relation_table, field=column1, id=new_values['id']['value'])

                    print(f'SQL Query: {sql_query_delete}')
                    print('----------------------------------------')

                    cursor.execute(sql_query_delete)

                    # and insert new records in relation table
                    # build bulk insert query in loop
                    # and execute it after loop
                    for relation_id in new_values[field]['value']:
                        sql_query_insert = 'INSERT INTO {relation_table} ({field1}, {field2}) VALUES ({id}, {relation_id})'.format(
                            relation_table=relation_table, field1=column1, field2=column2, id=new_values['id']['value'], relation_id=relation_id)

                        print(f'SQL Query: {sql_query_insert}')
                        print('----------------------------------------')

                        cursor.execute(sql_query_insert)
                elif new_values[field]['type'] == 'many2one':
                    sql_query += '{field} = {value}, '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'selection':
                    sql_query += '{field} = \'{value}\', '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'integer':
                    sql_query += '{field} = {value}, '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'html':
                    sql_query += '{field} = \'{value}\', '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'many2one_reference':
                    sql_query += '{field} = \'{value}\', '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'text':
                    sql_query += '{field} = \'{value}\', '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'one2many':
                    relation_table = new_values[field]['relation_table']
                    relation_field = new_values[field]['relation_field']

                    # get all records of relation_table that relation_field equal new_values['id']['value']
                    sql_query_select = 'SELECT id FROM {relation_table} WHERE {relation_field} = {id}'.format(
                        relation_table=relation_table, relation_field=relation_field, id=new_values['id']['value'])

                    print(f'SQL Query: {sql_query_select}')
                    print('----------------------------------------')

                    cursor.execute(sql_query_select)
                    result = cursor.fetchall()[0]

                    # update null value into relation table on column relation_field
                    sql_query_update = 'UPDATE {relation_table} SET {relation_field} = NULL WHERE id = {relation_id}'.format(
                        relation_table=relation_table, relation_field=relation_field, relation_id=result[0])

                    print(f'SQL Query: {sql_query_update}')
                    print('----------------------------------------')

                    cursor.execute(sql_query_update)

                    # update value into relation table on column relation_field
                    for relation_id in new_values[field]['value']:
                        sql_query_update = 'UPDATE {relation_table} SET {relation_field} = {id} WHERE id = {relation_id}'.format(
                            relation_table=relation_table, relation_field=relation_field, id=new_values['id']['value'], relation_id=relation_id)

                        print(f'SQL Query: {sql_query_update}')
                        print('----------------------------------------')

                        cursor.execute(sql_query_update)

                elif new_values[field]['type'] == 'reference':
                    sql_query += '{field} = \'{value}\', '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'binary':
                    sql_query += '{field} = \'{value}\', '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'float':
                    sql_query += '{field} = {value}, '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'date':
                    sql_query += '{field} = \'{value}\', '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                elif new_values[field]['type'] == 'char':
                    sql_query += '{field} = \'{value}\', '.format(
                        field=new_values[field]['name'], value=new_values[field]['value'])
                else:
                    raise Exception('Field type %s not supported' %
                                    new_values[field]['type'])

            sql_query = sql_query[:-2]
            sql_query += ' WHERE id = {id}'.format(
                id=new_values['id']['value'])

            print(f'SQL Query: {sql_query}')
            print('----------------------------------------')
            cursor.execute(sql_query)
            self.target_instance.database.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(
                "Error in transaction Reverting all other operations of a transction ", error)
            self.target_instance.database.rollback()
        finally:
            if self.target_instance.database is not None:
                cursor.close()
                self.target_instance.database.close()
                print('Database connection closed.')

    def generate_params(self, source_model, source_table, source_fields, target_model, target_table, target_fields):
        fields_list = {}
        source_fields_list = list(source_fields.keys())
        target_fields_list = list(target_fields.keys())

        # add id field to the list if it's not in the list
        if 'id' not in source_fields_list:
            source_fields_list.append('id')

        if 'id' not in target_fields_list:
            target_fields_list.append('id')

        # only keep fields that are in both source and target
        final_fields_list = list(
            set(source_fields_list).intersection(target_fields_list))

        # các giá trị mặc định phải có ở các fields.
        for field in final_fields_list:
            fields_list[field] = {
                'source': {},
                'target': {}
            }

            # mặc định sẽ gán toàn bộ các giá trị required vào
            # tuỳ theo trong config có hay không thì sẽ được override lại.
            for field_attr in REQUIRED_FIELD_ATTRIBUTES:
                if field_attr == 'name':
                    fields_list[field]['source']['name'] = field
                    fields_list[field]['target']['name'] = field
                elif field_attr == 'type':
                    fields_list[field]['source']['type'] = self.source_instance.get_field_type(
                        source_model, field)
                    fields_list[field]['target']['type'] = self.target_instance.get_field_type(
                        target_model, field)
                elif field_attr == 'store':
                    fields_list[field]['source']['store'] = self.source_instance.get_field_is_stored(
                        source_model, field)
                    fields_list[field]['target']['store'] = self.target_instance.get_field_is_stored(
                        target_model, field)

        # và từ file config sẽ override lại giá trị mặc định
        for field_name in source_fields.keys():
            # if field has items, then override the default value
            if not source_fields.get(field_name, {}):
                continue

            for field_attribute, field_attribute_value in source_fields.get(field_name, {}).items():
                fields_list[field]['source'][field_attribute] = field_attribute_value

        # và từ file config sẽ override lại giá trị mặc định
        for field_name in target_fields.keys():
            # if field has items, then override the default value
            if not target_fields.get(field_name, {}):
                continue

            for field_attribute, field_attribute_value in target_fields.get(field_name, {}).items():
                fields_list[field]['target'][field_attribute] = field_attribute_value

        # xử lý các field quan hệ
        for field in fields_list:
            if fields_list[field]['source']['type'] not in ['many2one', 'one2many', 'many2many']:
                continue

            relation_table = self.source_instance.get_field_relation_table(
                source_model, field)
            relation_model = self.source_instance.get_field_relation_model(
                source_model, field)
            relation_field = self.source_instance.get_field_relation_field(
                source_model, field)
            relation_field_col1 = self.source_instance.get_field_relation_col1(
                source_model, field)
            relation_field_col2 = self.source_instance.get_field_relation_col2(
                source_model, field)

            # nếu là many2one thì chỉ cần lấy id của record đó
            if fields_list[field]['source']['type'] == 'many2one':
                fields_list[field]['source'].update({
                    'relation_table': fields_list[field]['source'].get('relation_table') or relation_table,
                    'relation_model': fields_list[field]['source'].get('relation_model') or relation_model,
                })
            elif fields_list[field]['source']['type'] == 'one2many':
                fields_list[field]['source'].update({
                    'relation_table': fields_list[field]['source'].get('relation_table') or relation_table,
                    'relation_model': fields_list[field]['source'].get('relation_model') or relation_model,
                    'relation_field': fields_list[field]['source'].get('relation_field') or relation_field,
                })
            elif fields_list[field]['source']['type'] == 'many2many':
                fields_list[field]['source'].update({
                    'relation_table': relation_table,
                    'relation_model': relation_model,
                    'relation_col1': relation_field_col1,
                    'relation_col2': relation_field_col2,
                })

        # xử lý các field quan hệ
        for field in fields_list:
            if fields_list[field]['target']['type'] not in ['many2one', 'one2many', 'many2many']:
                continue

            relation_table = self.source_instance.get_field_relation_table(
                target_model, field)
            relation_model = self.source_instance.get_field_relation_model(
                target_model, field)
            relation_field = self.source_instance.get_field_relation_field(
                target_model, field)
            relation_field_col1 = self.source_instance.get_field_relation_col1(
                target_model, field)
            relation_field_col2 = self.source_instance.get_field_relation_col2(
                target_model, field)

            # nếu là many2one thì chỉ cần lấy id của record đó
            if fields_list[field]['target']['type'] == 'many2one':
                fields_list[field]['target'].update({
                    'relation_table': fields_list[field]['target'].get('relation_table') or relation_table,
                    'relation_model': fields_list[field]['target'].get('relation_model') or relation_model,
                })
            elif fields_list[field]['target']['type'] == 'one2many':
                fields_list[field]['target'].update({
                    'relation_table': fields_list[field]['target'].get('relation_table') or relation_table,
                    'relation_model': fields_list[field]['target'].get('relation_model') or relation_model,
                    'relation_field': fields_list[field]['target'].get('relation_field') or relation_field,
                })
            elif fields_list[field]['target']['type'] == 'many2many':
                fields_list[field]['target'].update({
                    'relation_table': relation_table,
                    'relation_model': relation_model,
                    'relation_col1': relation_field_col1,
                    'relation_col2': relation_field_col2,
                })

        return fields_list

    def generate_values(self, fields, source_record_id, source_table, source_model, target_table, target_model, target_record_id=None):
        source_record = self.source_instance.get_record(
            source_model, source_record_id, list(fields.keys()))
        if not source_record:
            raise Exception("Source record with id `%s` not found in model `%s" %
                            (source_record_id, source_model))

        target_record = {}
        if target_record_id:
            target_record = self.target_instance.get_record(
                target_model, target_record_id, list(fields.keys()))
            if not target_record:
                raise Exception("Target record with id `%s` not found in model `%s`" %
                                (target_record_id, target_model))

        """
            handle fields:
                - boolean
                - monetary
                - datetime
                - many2many
                - many2one
                - selection
                - integer
                - html
                - many2one_reference
                - text
                - one2many
                - reference
                - binary
                - float
                - date
                - char
        """

        # get all values of fields on source record
        for field in fields:

            field_type = fields[field]['source']['type']

            print('... field: %s' % field)
            print('... field_value %s' % source_record[field])

            if field_type == 'boolean':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'monetary':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'datetime':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'many2many':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'many2one':
                fields[field]['target']['value'] = source_record[field][0] if source_record[field] else None
            elif field_type == 'selection':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'integer':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'html':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'many2one_reference':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'text':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'one2many':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'reference':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'binary':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'float':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'date':
                fields[field]['target']['value'] = source_record[field]
            elif field_type == 'char':
                fields[field]['target']['value'] = source_record[field]
            else:
                raise Exception("Field type %s not supported" % field_type)

        # validate all relation fields on target table
        for field in fields:
            field_type = fields[field]['target']['type']
            force_create = fields[field]['target'].get('force_create', False)

            # if force create is True, then skip to validate this relational field
            # because we will create new record for this field
            if force_create:
                continue

            if field_type == 'many2one':
                relation_table = fields[field]['target'].get('relation_table')
                relation_model = fields[field]['target'].get('relation_model')
                relation_field = fields[field]['target'].get('relation_field')
                relation_id = fields[field]['target'].get('value')

                if relation_id:
                    relation_record = self.target_instance.get_count(
                        relation_model, relation_id)
                    if not relation_record:
                        raise Exception(
                            "Record %s not found in table %s" % (relation_id, relation_table))

            elif field_type == 'one2many':
                relation_table = fields[field]['target'].get('relation_table')
                relation_model = fields[field]['target'].get('relation_model')
                relation_field = fields[field]['target'].get('relation_field')
                relation_ids = fields[field]['target'].get('value')

                for relation_id in relation_ids:
                    relation_record = self.target_instance.get_count(
                        relation_model, relation_id)
                    if not relation_record:
                        raise Exception(
                            "Record %s not found in table %s" % (relation_id, relation_table))

            elif field_type == 'many2many':
                relation_table = fields[field]['target'].get('relation_table')
                relation_model = fields[field]['target'].get('relation_model')
                relation_col1 = fields[field]['target'].get('relation_col1')
                relation_col2 = fields[field]['target'].get('relation_col2')
                relation_ids = fields[field]['target'].get('value')

                for relation_id in relation_ids:
                    relation_record = self.target_instance.get_count(
                        relation_model, relation_id)
                    if not relation_record:
                        raise Exception(
                            "Record %s not found in table %s" % (relation_id, relation_table))

        # keep target values, remove source values
        new_values = {}
        for field in fields:
            new_values[field] = fields[field]['target']
        return new_values

    def run(self, cmdargs):
        parser = argparse.ArgumentParser(
            prog="%s sync" % sys.argv[0].split(os.path.sep)[-1],
            description=self.__doc__
        )
        parser.add_argument(
            '--source-config', help="Path of the odoo source configuration to sync", required=True)
        parser.add_argument(
            '--source-model', help="Source model", required=True)
        parser.add_argument(
            '--source-table', help="Source table", required=True)
        parser.add_argument('--source-record-id',
                            help="Source record id", required=True)
        parser.add_argument(
            '--target-config', help="Path of the odoo target configuration to sync", required=True)
        parser.add_argument(
            '--target-model', help="Target model", required=True)
        parser.add_argument(
            '--target-table', help="Target table", required=True)
        parser.add_argument('--target-record-id',
                            help="Target record id")
        parser.add_argument('--source-fields',
                            help="Source fields", required=True)
        parser.add_argument('--target-fields',
                            help="Target fields", required=True)
        parser.add_argument('--force-create',
                            help="Force create new record in destination database", default=False)

        if not cmdargs:
            sys.exit(parser.print_help())

        args = parser.parse_args(args=cmdargs)
        odoo_source_conf = config.parse_odoo_config(args.source_config)
        database_target_config = config.parse_database_config(
            args.target_config)

        odoo_target_conf = config.parse_odoo_config(args.target_config)
        database_target_config = config.parse_database_config(
            args.target_config)

        source_fields = config.parse_config(args.source_fields)
        target_fields = config.parse_config(args.target_fields)

        # odoo instance of source, include a odoo connection and a database connection
        self.source_instance = Odoo(
            odoo_config=odoo_source_conf, database_config=database_target_config)

        # odoo instance of target, include a odoo connection and a database connection
        self.target_instance = Odoo(
            odoo_config=odoo_target_conf, database_config=database_target_config)

        params = self.generate_params(source_model=args.source_model, source_table=args.source_table, source_fields=source_fields,
                                      target_model=args.target_model, target_table=args.target_table, target_fields=target_fields)
        new_values = self.generate_values(fields=params, source_model=args.source_model, source_table=args.source_table, source_record_id=args.source_record_id,
                                          target_model=args.target_model, target_table=args.target_table, target_record_id=args.target_record_id)
        self.sync_record(new_values=new_values, model=args.target_model,
                         table=args.target_table, target_record_id=args.target_record_id)
