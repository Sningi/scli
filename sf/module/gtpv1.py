import click
from sys import exit

from base import cli,sprint
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *


def gtpv1_op(ctx, args, incomplete):
    comp = [('show', 'show config'),
              ('enable', 'enable feature'),
              ('disable', 'disble feature'),
              ('set', 'set timeout')]
    return [c for c in comp if c[0].startswith(incomplete)]


gtpv1_cfg_field = [("cdr_mode","cdr_mode"),
    ("ggsn_bear_uinfo_timeout","ggsn_bear_uinfo_timeout"),
    ("gtpu_bear_enable","gtpu_bear_enable"),
    ("cdr_enable","gtpv1_cdr_enable"),
    ("cdr_timeout","gtpv1_cdr_timeout"),
    ("decode","gtpv1_enable"),
    ("ggsn_enable","gtpv1_ggsn_enable"),
    ("assoc_timeout","gtpv1_sig_timeout"),
    ("learn_flag","learn_enable_flag"),
                  ]
gtpv1_cfg_dict = dict(gtpv1_cfg_field)


def cfg_field(ctx, args, incomplete):
    if args[-1] == "set":
        return [i for i in gtpv1_cfg_field if i[0].startswith(incomplete) and "timeout" in i[0] or 'mode' in i[0]]
    elif args[-1] in ["enable", "disable"]:
        return [i for i in gtpv1_cfg_field if i[0].startswith(incomplete) and "timeout" not in i[0]]
    elif args[-1] == "show":
        return [i for i in gtpv1_cfg_field if i[0].startswith(incomplete)]


def cfg_value(ctx, args, incomplete):
    field = [('1-1200', 'timeout value')]
    return [c for c in field if c[0].startswith(incomplete)]


@cli.command()  # @cli, not @click!
@click.argument("op", type=click.STRING, autocompletion=gtpv1_op)
@click.argument("field", type=click.STRING, autocompletion=cfg_field, required=False)
@click.argument("value", type=click.STRING, autocompletion=cfg_value, required=False)
def gtpv1_cfg(op, field=None, value=None):
    if op == 'show':
        data = hp.cpu_get('gtpv1/config')
        if field:
            field = gtpv1_cfg_dict[field]
        sprint(gen_table(data, filter=field))
    elif op == 'enable' or op == 'disable':
        if not field or field not in gtpv1_cfg_dict:
            sprint("{0} field is none".format(op))
            exit()
        op_data = [{"op": "replace",
                    "path": "/"+gtpv1_cfg_dict[field],
                    "value":SWITCH[op]}]
        data = hp.cpu_patch('gtpv1/config', op_data)
        sprint(gen_table(data, tab="code"))
    elif op == "set":
        op_data = [{"op": "replace",
                    "path": "/"+gtpv1_cfg_dict[field],
                    "value":value}]
        data = hp.cpu_patch('gtpv1/config', op_data)
        sprint(gen_table(data, tab="code"))


def gtpv1_stat_operation(ctx, args, incomplete):
    comp = [('show', 'show stat'),
              ('clean', 'clean stat')]
    return [c for c in comp if c[0].startswith(incomplete)]


def gtpv1_stat_filter(ctx, args, incomplete):
    comp = [('ggsn_bear', 'ggsn_bear stat'),
              ('gtpu_bear', 'gtpu_bear stat'),
              ('pdp', 'pdp stat'),
              ('refill', 'refill stat'),
              ('node', 'hash node stat')]
    return [c for c in comp if c[0].startswith(incomplete)]


@cli.command()
@click.argument("op", type=click.STRING, autocompletion=gtpv1_stat_operation)
@click.argument("filter", type=click.STRING, autocompletion=gtpv1_stat_filter, required=False)
def gtpv1_stat(op, filter):
    if 'show'.startswith(op):
        data = hp.cpu_get('gtpv1/stat')
        sprint(gen_table(data, tab="count", filter=filter))
    elif 'clean'.startswith(op):
        data = hp.cpu_patch('gtpv1/stat', general_clean_data)
        sprint(gen_table(data, tab="result"))

sf_gtpv1_finish = ''
