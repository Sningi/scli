import click

from base import cli,sprint
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *


def gtpv2_op(ctx, args, incomplete):
    comp = [('show', 'show config'),
              ('enable', 'enable feature'),
              ('disable', 'disble feature'),
              ('set', 'set timeout')]
    return [c for c in comp if c[0].startswith(incomplete)]


gtpv2_cfg_field = [('gtpv2_decode', 'gtpv2_decode_enable'),
                  ('gtpv2_decode_upproto', 'gtpv2_decode_upproto_enable'),
                  ('gtpv2_cache', 'gtpv2_cache_enable'),
                  
                  ]
gtpv2_cfg_dict = dict(gtpv2_cfg_field)


def cfg_field(ctx, args, incomplete):
    if args[-1] == "set":
        return [i for i in gtpv2_cfg_field if i[0].startswith(incomplete) and "timeout" in i[0]]
    elif args[-1] in ["enable", "disable"]:
        return [i for i in gtpv2_cfg_field if i[0].startswith(incomplete) and "timeout" not in i[0]]
    elif args[-1] == "show":
        return [i for i in gtpv2_cfg_field if i[0].startswith(incomplete)]


def cfg_value(ctx, args, incomplete):
    field = [('1-1200', 'timeout value')]
    return [c for c in field if c[0].startswith(incomplete)]


@cli.command()  # @cli, not @click!
@click.argument("op", type=click.STRING, autocompletion=gtpv2_op)
@click.argument("field", type=click.STRING, autocompletion=cfg_field, required=False)
@click.argument("value", type=click.STRING, autocompletion=cfg_value, required=False)
def gtpv2_cfg(op, field=None, value=None):
    if op == 'show':
        data = hp.cpu_get('gtpv2/config')
        if field:
            field = gtpv2_cfg_dict[field]
        sprint(gen_table(data, filter=field))
    elif op == 'enable' or op == 'disable':
        if not field or field not in gtpv2_cfg_dict:
            sprint("{0} field is none".format(op))
            exit()
        op_data = [{"op": "replace",
                    "path": "/"+gtpv2_cfg_dict[field],
                    "value":SWITCH[op]}]
        data = hp.cpu_patch('gtpv2/config', op_data)
        sprint(gen_table(data, tab="code"))
    elif op == "set":
        op_data = [{"op": "replace",
                    "path": "/"+gtpv2_cfg_dict[field],
                    "value":value}]
        data = hp.cpu_patch('gtpv2/config', op_data)
        sprint(gen_table(data, tab="code"))


def gtpv2_stat_operation(ctx, args, incomplete):
    comp = [('show', 'show stat'),
              ('clean', 'clean stat')]
    return [c for c in comp if c[0].startswith(incomplete)]


def gtpv2_stat_filter(ctx, args, incomplete):
    comp = [('chunk', 'chunk stat'),
              ('error', 'error stat'),
              ('total', 'total stat')]
    return [c for c in comp if c[0].startswith(incomplete)]


@cli.command()
@click.argument("op", type=click.STRING, autocompletion=gtpv2_stat_operation)
@click.argument("filter", type=click.STRING, autocompletion=gtpv2_stat_filter, required=False)
def gtpv2_stat(op, filter):
    if 'show'.startswith(op):
        data = hp.cpu_get('gtpv2/stat')
        sprint(gen_table(data, tab="count", filter=filter))
    elif 'clean'.startswith(op):
        data = hp.cpu_patch('gtpv2/stat', general_clean_data)
        sprint(gen_table(data, tab="result"))

sf_gtpv2_finish = ''
