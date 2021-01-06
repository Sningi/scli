import click
from json import dumps

from base import cli, clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *

def sctp_operation(ctx, args, incomplete):
    colors = [('show', 'show config'),
              ('enable', 'enable feature'), 
              ('disable', 'disble feature'),
              ('timeout', 'set timeout')]
    return [c for c in colors if incomplete in c[0]]

sctp_cfg_field = [  ('sctp_decode', 'sctp_decode_enable'),
            ('sctp_decode_upproto', 'sctp_decode_upproto_enable'),
            ('ngap_decode', 'ngap_decode_enable'),
            ('ngap_skip_paging', 'ngap_decode_skip_paging_enable'),
            ('ngap_cdr', 'ngap_cdr_enable'),
            ('nas_decrypt', 'ngap_nas_decrypt_enable'),
            ('nas_decrypted_output', 'ngap_nas_decrypted_output_enable'),

            ('ngap_cdr_timeout', 'ngap_imsi_timeout_cycle'),
            ('ngap_cdr_timeout', 'ngap_cdr_timeout'),
            ('ngap_small_cdr_timeout', 'ngap_small_cdr_timeout'),
            ('ngap_handover_cdr_timeout', 'ngap_handover_cdr_timeout')]
sctp_cfg_dict = dict(sctp_cfg_field)


def cfg_field(ctx, args, incomplete):
    if args[-1] == "timeout":
        return [i for i in sctp_cfg_field if incomplete in i[0] and "timeout" in i[0]]
    elif args[-1] in ["enable", "disable"]:
        return [i for i in sctp_cfg_field if incomplete in i[0] and "timeout" not in i[0]]
    elif args[-1] == "show":
        return [i for i in sctp_cfg_field if incomplete in i[0]]


def cfg_value(ctx, args, incomplete):
    field = [('1-1200', 'timeout value')]
    return [c for c in field if c[0].startswith(incomplete)]

@cli.command()# @cli, not @click!
@click.argument("op", type=click.STRING, autocompletion=sctp_operation)
@click.argument("field", type=click.STRING, autocompletion=cfg_field, required=False)
@click.argument("value", type=click.STRING, autocompletion=cfg_value, required=False)
def sctp_config(op, field=None, value =None):
    if op == 'show':
        data = hp.cpu_get('sctp/config')
        if field:
            field = sctp_cfg_dict[field]
        print(gen_table(data, filter=field))
    elif op == 'enable' or op == 'disable':
        if not field or field not in sctp_cfg_dict:
            print("{0} field is none".format(op))
            exit()
        op_data = [{"op":"replace",
                    "path":"/"+sctp_cfg_dict[field],
                    "value":SWITCH[op]}]
        data = hp.cpu_patch('sctp/config', op_data)
        print(gen_table(data, tab="code"))
    elif op == "timeout":

        op_data = [{"op":"replace",
            "path":"/"+sctp_cfg_dict[field],
            "value":value}]
        data = hp.cpu_patch('sctp/config', op_data)
        print(gen_table(data, tab="code"))

def sctp_stat_operation(ctx, args, incomplete):
    colors = [('show', 'show stat'),
              ('clean', 'clean stat')]
    return [c for c in colors if incomplete in c[0]]


def sctp_stat_filter(ctx, args, incomplete):
    colors = [('chunk', 'chunk stat'),
              ('error', 'error stat'),
              ('total', 'total stat')]
    return [c for c in colors if incomplete in c[0]]


@cli.command()
@click.argument("op", type=click.STRING, autocompletion=sctp_stat_operation)
@click.argument("filter", type=click.STRING, autocompletion=sctp_stat_filter, required=False)
def sctp_stat(op, filter):
    if op == 'show':
        data = hp.cpu_get('sctp/stat')
        print(gen_table(data, tab="count", filter=filter))
    elif op == 'clean':
        data = hp.cpu_patch('sctp/stat', clean_data)
        print(gen_table(data, tab="code"))