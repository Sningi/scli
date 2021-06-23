from click import argument,option, STRING,Choice
from sys import exit

from common.base import cli, sprint
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *

gtpu_cfg_field = [('gtpu_decode', 'gtpu_bear_dec_enable'),
                  ('gtpu_inner_decode', 'gtpu_inner_decode'),
                  ('device_number', 'device_number'),
                  ('bear_timeout_mul', 'gtpu_bear_tab_timeout_mul'),
                  ('bear_timeout_sec', 'gtpu_bear_tab_timeout_sec'),
                  ('split_number', 'split_number')]
gtpu_cfg_dict = dict(gtpu_cfg_field)


def cfg_field(ctx, args, incomplete):
    from click import __version__
    if __version__.startswith('8.'):
        from click.parser import split_arg_string
        import os
        args = split_arg_string(os.environ["COMP_WORDS"])
    if "set" in args:
        return [i for i in gtpu_cfg_field if i[0].startswith(incomplete) and ("timeout" in i[0] or "num" in i[0])]
    elif "enable" in args or "disable" in args:
        return [i for i in gtpu_cfg_field if i[0].startswith(incomplete) and "decode" in i[0]]
    elif "show" in args:
        return [i for i in gtpu_cfg_field if i[0].startswith(incomplete)]


def cfg_value(ctx, args, incomplete):
    field = [('1-1200', 'timeout value')]
    return [c for c in field if c[0].startswith(incomplete)]


@cli.command()  # @cli, not @click!
@argument("op", type=Choice(['show','enable','disable','set']),default='show')
@argument("field", type=STRING, autocompletion=cfg_field, required=False)
@argument("value", type=STRING, autocompletion=cfg_value, required=False)
def gtpu_cfg(op, field=None, value=None):
    if op == 'show':
        data = hp.cpu_get('gtpu/config')
        if field:
            field = gtpu_cfg_dict[field]
        sprint(gen_table(data, filter=field))
    elif op == 'enable' or op == 'disable':
        if not field or field not in gtpu_cfg_dict:
            sprint("{0} field is none".format(op))
            exit()
        op_data = [{"op": "replace",
                    "path": "/"+gtpu_cfg_dict[field],
                    "value":SWITCH[op]}]
        data = hp.cpu_patch('gtpu/config', op_data)
        sprint(gen_table(data, tab="code"))
    elif op == "set":
        op_data = [{"op": "replace",
                    "path": "/"+gtpu_cfg_dict[field],
                    "value":int(value)}]
        data = hp.cpu_patch('gtpu/config', op_data)
        sprint(gen_table(data, tab="code"))

@cli.command()
@argument("op", type=Choice(['show','clean']),default='show')
@option('--filter','-f', type=Choice(['s1', 'n3','bear','none','gn']), default='none', required=False)
def gtpu_stat(op, filter):
    if op == 'show':
        data = hp.cpu_get('gtpu/stat')
        if filter == "none":
            filter = None
        sprint(gen_table(data, tab="count", filter=filter))
    elif op == 'clean':
        data = hp.cpu_patch('gtpu/stat', general_clean_data)
        sprint(gen_table(data, tab="code"))


sf_gtpu_finish = ''
