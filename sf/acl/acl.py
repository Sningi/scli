import click

from base import cli
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table

def acl_imsi_operation(ctx, args, incomplete):
    op = [('show', 'show acl'),
              ('create', 'create acl'), 
              ('delete', 'delete acl')]
    return [c for c in op if c[0].startswith(incomplete)]

def config_field(ctx, args, incomplete):
    field = [  ('acl_imsi_decode', 'acl_imsi_decode_enable'),
                ('acl_imsi_decode_upproto', 'acl_imsi_decode_upproto_enable'),
                ('ngap_decode', 'ngap_decode_enable'),
                ('ngap_skip_paging', 'ngap_decode_skip_paging_enable'),
                ('ngap_cdr', 'ngap_cdr_enable'),
                ('nas_decrypt', 'ngap_nas_decrypt_enable'),
                ('nas_decrypted_output', 'ngap_nas_decrypted_output_enable'),

                ('ngap_cdr_timeout', 'ngap_imsi_timeout_cycle'),
                ('ngap_cdr_timeout', 'ngap_cdr_timeout'),
                ('ngap_small_cdr_timeout', 'ngap_small_cdr_timeout'),
                ('ngap_handover_cdr_timeout', 'ngap_handover_cdr_timeout'),]
    return [i for i in field if incomplete in i[0]]

def config_value(ctx, args, incomplete):
    colors = [('enable', 'enable feature'),
              ('disable', 'set config')]
    return [c for c in colors if c[0].startswith(incomplete)]

@cli.command()# @cli, not @click!
@click.argument("op", type=click.STRING, autocompletion=acl_imsi_operation)
@click.argument("field", type=click.STRING, autocompletion=config_field, required=False)
@click.argument("value", type=click.STRING, autocompletion=config_value, required=False)
def acl(op, field=None, value =None):
    if op == 'show':
        data = hp.cpu_get('acl/config/group_1')
        print(gen_table(data,))
    elif op == 'enable' or op == 'disable':
        if not field:
            print("{0} field is none".format(op))
            exit()
        op_data = []
        data = hp.cpu_put('acl_imsi/stat', )
        print(gen_table(data, tab="code"))


# def acl_imsi_stat_operation(ctx, args, incomplete):
#     colors = [('show', 'show stat'),
#               ('clean', 'clean stat')]
#     return [c for c in colors if incomplete in c[0]]


# def acl_imsi_stat_filter(ctx, args, incomplete):
#     colors = [('chunk', 'chunk stat'),
#               ('error', 'error stat'),
#               ('total', 'total stat')]
#     return [c for c in colors if incomplete in c[0]]


# @cli.command()
# @click.argument("op", type=click.STRING, autocompletion=acl_imsi_stat_operation)
# @click.argument("filter", type=click.STRING, autocompletion=acl_imsi_stat_filter, required=False)
# def acl_imsi_stat(op, filter):
#     if op == 'show':
#         data = hp.cpu_get('acl_imsi/stat')
#         print(gen_table(data, tab="count", filter=filter))
#     elif op == 'clean':
#         data = hp.cpu_patch('acl_imsi/stat', general_clean_data)
#         print(gen_table(data, tab="code"))
