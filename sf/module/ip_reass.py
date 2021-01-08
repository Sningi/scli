import click
from json import dumps

from base import cli
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *

def ipreass_operation(ctx, args, incomplete):
    colors = [('show', 'show config'),
              ('enable', 'enable feature'), 
              ('disable', 'disble feature'),
              ('timeout', 'set timeout')]
    return [c for c in colors if incomplete in c[0]]

ipreass_cfg_field = [  ('ipreass_decode', 'ipreass_decode_enable'),
                    ]
ipreass_cfg_dict = dict(ipreass_cfg_field)


def cfg_field(ctx, args, incomplete):
    if args[-1] == "timeout":
        return [i for i in ipreass_cfg_field if incomplete in i[0] and "timeout" in i[0]]
    elif args[-1] in ["enable", "disable"]:
        return [i for i in ipreass_cfg_field if incomplete in i[0] and "timeout" not in i[0]]
    elif args[-1] == "show":
        return [i for i in ipreass_cfg_field if incomplete in i[0]]


def cfg_value(ctx, args, incomplete):
    field = [('1-1200', 'timeout value')]
    return [c for c in field if c[0].startswith(incomplete)]

@cli.command()# @cli, not @click!
@click.argument("op", type=click.STRING, autocompletion=ipreass_operation)
@click.argument("field", type=click.STRING, autocompletion=cfg_field, required=False)
@click.argument("value", type=click.STRING, autocompletion=cfg_value, required=False)
def ipreass_config(op, field=None, value =None):
    if op == 'show':
        data = hp.cpu_get('ip_reass/config')
        if field:
            field = ipreass_cfg_dict[field]
        print(gen_table(data, filter=field))
    elif op == 'enable' or op == 'disable':
        if not field or field not in ipreass_cfg_dict:
            print("{0} field is none".format(op))
            exit()
        op_data = [{"op":"replace",
                    "path":"/"+ipreass_cfg_dict[field],
                    "value":SWITCH[op]}]
        data = hp.cpu_patch('ipreass/config', op_data)
        print(gen_table(data, tab="code"))
    elif op == "timeout":

        op_data = [{"op":"replace",
            "path":"/"+ipreass_cfg_dict[field],
            "value":value}]
        data = hp.cpu_patch('ipreass/config', op_data)
        print(gen_table(data, tab="code"))

def ipreass_stat_operation(ctx, args, incomplete):
    colors = [('show', 'show stat'),
              ('clean', 'clean stat')]
    return [c for c in colors if incomplete in c[0]]


def ipreass_stat_filter(ctx, args, incomplete):
    colors = [('pkt', 'chunk stat'),
              ('fail', 'error stat'),
              ('timer', 'total stat')]
    return [c for c in colors if incomplete in c[0]]


@cli.command()
@click.argument("op", type=click.STRING, autocompletion=ipreass_stat_operation)
@click.argument("filter", type=click.STRING, autocompletion=ipreass_stat_filter, required=False)
def ipreass_stat(op, filter):
    if op == 'show':
        data = hp.cpu_get('ip_reass/stat')
        print(gen_table(data, tab="count", filter=filter))
    elif op == 'clean':
        data = hp.cpu_patch('ipreass/stat', general_clean_data)
        print(gen_table(data, tab="code"))
