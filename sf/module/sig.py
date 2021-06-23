from sys import exit
from click import argument, option, STRING, Choice

from common.base import cli, sprint
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *

sig_cfg_field = [ ('sig_imsi_timeout_cycle', 'sig_imsi_timeout_cycle'),
                ]
sig_cfg_dict = dict(sig_cfg_field)


def cfg_field(ctx, args, incomplete):
    if "set" in args:
        return [i for i in sig_cfg_field if i[0].startswith(incomplete) and ("timeout" in i[0] or "num" in i[0])]


def cfg_value(ctx, args, incomplete):
    field = [('1-1200', 'timeout value')]
    return [c for c in field if c[0].startswith(incomplete)]


@cli.command()  # @cli, not @click!
@argument("op", type=Choice(['show','set']),default='show')
@argument("field", type=STRING, autocompletion=cfg_field, required=False)
@argument("value", type=STRING, autocompletion=cfg_value, required=False)
def sig_cfg(op, field=None, value=None):
    if op == 'show':
        data = hp.cpu_get('sig/config')
        if field:
            field = sig_cfg_dict[field]
        sprint(gen_table(data, filter=field))
    elif op == 'enable' or op == 'disable':
        if not field or field not in sig_cfg_dict:
            sprint("{0} field is none".format(op))
            exit()
        op_data = [{"op": "replace",
                    "path": "/"+sig_cfg_dict[field],
                    "value":SWITCH[op]}]
        data = hp.cpu_patch('sig/config', op_data)
        sprint(gen_table(data, tab="code"))
    elif op == "set":
        op_data = [{"op": "replace",
                    "path": "/"+sig_cfg_dict[field],
                    "value":int(value)}]
        data = hp.cpu_patch('sig/config', op_data)
        sprint(gen_table(data, tab="code"))

@cli.command()
@argument("op", type=Choice(['show','clean']),default='show')
@option('--filter','-f', type=Choice(['sig', 'imsi_info']), default=None, required=False)
def sig_stat(op, filter):
    if op == 'show':
        data = hp.cpu_get('sig/stat')
        if filter == "all":
            filter = None
        sprint(gen_table(data, tab="count", filter=filter))
    elif op == 'clean':
        data = hp.cpu_patch('sig/stat', general_clean_data)
        sprint(gen_table(data, tab="code"))


sf_sig_finish = ''
