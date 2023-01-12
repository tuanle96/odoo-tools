import functools
import odoorpc
import paramiko
import psycopg2


class Odoo(object):
    def __init__(self, odoo_config: dict, database_config: dict, *args, **kw) -> None:
        # odoo config and init odoo connection
        # database config and init database connection
        self.odoo_host = odoo_config.get('host')
        self.odoo_port = odoo_config.get('port')
        self.odoo_user = odoo_config.get('user')
        self.odoo_password = odoo_config.get('password')
        self.odoo_version = odoo_config.get('version')
        self.odoo_database = odoo_config.get('database_name')

        self.database_host = database_config.get('host')
        self.database_port = database_config.get('port')
        self.database_user = database_config.get('user')
        self.database_password = database_config.get('password')
        self.database_name = database_config.get('name')

        self.ssh_tunnel = database_config.get('ssh_tunnel', False)
        self.ssh_host = database_config.get('ssh_host')
        self.ssh_port = database_config.get('ssh_port')
        self.ssh_user = database_config.get('ssh_user')
        self.ssh_password = database_config.get('ssh_password')
        self.ssh_is_key = database_config.get('ssh_is_key', False)
        self.ssh_private_key = database_config.get('ssh_private_key')

        self.odoo = self._get_odoo_instance()
        self.database = self._get_database_instance()

    def _get_odoo_instance(self):
        print('Connecting to Odoo %s' % self.odoo_host)
        odoo = odoorpc.ODOO(self.odoo_host, port=self.odoo_port,
                            protocol='jsonrpc+ssl', version=self.odoo_version)
        odoo.login(self.odoo_database, self.odoo_user, self.odoo_password)
        return odoo

    def _get_database_instance(self):
        print('Connecting to database %s' % self.database_name)
        try:
            database = psycopg2.connect(
                host=self.database_host,
                port=self.database_port,
                user=self.database_user,
                password=self.database_password,
                database=self.database_name
            )
        except psycopg2.OperationalError:
            if self.ssh_tunnel:
                self._ssh_tunnel()
                database = self._get_database_instance()
            else:
                raise
        return database

    def _ssh_tunnel(self):
        print('Connecting to SSH tunnel %s' % self.ssh_host)
        if self.ssh_is_key:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=self.ssh_host,
                port=self.ssh_port,
                username=self.ssh_user,
                key_filename=self.ssh_private_key
            )
        else:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=self.ssh_host,
                port=self.ssh_port,
                username=self.ssh_user,
                password=self.ssh_password
            )
        ssh.get_transport().set_keepalive(30)
        self.database_host = 'localhost'
        self.database_port = ssh.get_transport().local_bind_port

    @functools.lru_cache(maxsize=1000)
    def get_field_attributes(self, model, field_name):
        # field_attributes = self.odoo.env[model].fields_get([field_name])
        # if not field_attributes:
        #     raise Exception('Field %s not found in model %s' %
        #                     (field_name, model))
        # print(field_attributes.get(field_name))
        # return field_attributes.get(field_name)
        records = self.odoo.env['ir.model.fields'].search_read(
            [('model', '=', model), ('name', '=', field_name)], fields=['relation', 'relation_table', 'column1', 'column2', 'relation_field', 'store', 'ttype'], limit=1)

        if len(records) == 0:
            return {}

        relation_table = records[0].get('relation_table')
        relation_model = records[0].get('relation')
        field_type = records[0].get('ttype')

        if field_type == 'one2many':
            relation_table = relation_model.replace('.', '_')

        return {
            'type': field_type,
            'store': records[0].get('store'),
            # as res_model in attributes of field (many2one, one2many, many2many)
            'relation': relation_model,
            # it's relation attribute in many2many field.
            'relation_table': relation_table,
            'column1': records[0].get('column1'),
            'column2': records[0].get('column2'),
            # it's inverse_name attribute in one2many field.
            'relation_field': records[0].get('relation_field')
        }

    def get_field_type(self, model, field_name):
        print(f'... Getting field type for {model}.{field_name}')
        return self.get_field_attributes(model, field_name).get('type')

    def get_field_is_stored(self, model, field_name):
        print(f'... Getting field is stored for {model}.{field_name}')
        return self.get_field_attributes(model, field_name).get('store')

    def get_field_relation_table(self, model, field_name):
        print(f'... Getting field relation table for {model}.{field_name}')
        return self.get_field_attributes(model, field_name).get('relation_table')

    def get_field_relation_field(self, model, field_name):
        print(f'... Getting field relation field for {model}.{field_name}')
        return self.get_field_attributes(model, field_name).get('relation_field')

    def get_field_relation_model(self, model, field_name):
        print(f'... Getting field relation model for {model}.{field_name}')
        return self.get_field_attributes(model, field_name).get('relation')

    def get_field_relation_col1(self, model, field_name):
        print(f'... Getting field relation col1 for {model}.{field_name}')
        return self.get_field_attributes(model, field_name).get('column1')

    def get_field_relation_col2(self, model, field_name):
        print(f'... Getting field relation col2 for {model}.{field_name}')
        return self.get_field_attributes(model, field_name).get('column2')

    def get_record(self, model, record_id, fields=None):
        print('...Getting record %s from model %s with fields %s' %
              (record_id, model, fields))
        fields = ['id'] if fields is None else fields
        try:
            record = self.odoo.env[model].with_context(
                active_test=False).search_read([('id', '=', record_id)], fields)
        except odoorpc.error.RPCError as e:
            print('Error getting record %s from model %s with fields %s and error: %s' % (
                record_id, model, fields, e))
            return None
        return None if not record else record[0]

    def get_count(self, model, record_id):
        print('...Getting count from model %s' % model)
        return self.odoo.env[model].with_context(active_test=False).search_count([('id', '=', record_id)])
