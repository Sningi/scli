from sys import exit
from click import argument, option, STRING, Choice

from common.base import cli, sprint, get_args
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *

http2_cfg_field = [('http2_decode', 'enable'),
                   ('n11_decode', 'enable_N11_decode'),
                   ('nx_cache','enable_Nx_cache'),
                   ('nx_cache_limit','Nx_cache_limit'),
                   ('n11_timeout', 'N11_table_time'),
                   ('stream_timeout', 'stream_time'),
                   ('connect_timeout', 'connect_time')]
http2_cfg_dict = dict(http2_cfg_field)


def cfg_field(ctx, args, incomplete):
    args = get_args(args)
    if "set" in args:
        return [i for i in http2_cfg_field if incomplete in i[0] and "timeout" in i[0] or "limit" in i[0]]
    elif "enable" in args or "disable" in args:
        return [i for i in http2_cfg_field if incomplete in i[0] and "timeout" not in i[0]]
    elif "show" in args:
        return [i for i in http2_cfg_field if incomplete in i[0]]


def cfg_value(ctx, args, incomplete):
    field = [('1-1200', 'timeout value')]
    return [c for c in field if c[0].startswith(incomplete)]


@cli.command()  # @cli, not @click!
@argument("op", type=Choice(['show','enable','disable','set']),default='show')
@argument("field", type=STRING, autocompletion=cfg_field, required=False)
@argument("value", type=STRING, autocompletion=cfg_value, required=False)
def http2_cfg(op, field=None, value=None):
    if op == 'show':
        data = hp.cpu_get('http2/config')
        if field:
            field = http2_cfg_dict[field]
        sprint(gen_table(data, filter=field))
    elif op == 'enable' or op == 'disable':
        if not field or field not in http2_cfg_dict:
            sprint("{0} field is none".format(op))
            exit()
        op_data = [{"op": "replace",
                    "path": "/"+http2_cfg_dict[field],
                    "value":SWITCH[op]}]
        data = hp.cpu_patch('http2/config', op_data)
        sprint(gen_table(data, tab="code"))
    elif op == "timeout":

        op_data = [{"op": "replace",
                    "path": "/"+http2_cfg_dict[field],
                    "value":int(value)}]
        data = hp.cpu_patch('http2/config', op_data)
        sprint(gen_table(data, tab="code"))
    elif op == "set":
        op_data = [{"op": "replace",
                    "path": "/"+http2_cfg_dict[field],
                    "value":int(value)}]
        data = hp.cpu_patch('http2/config', op_data)
        sprint(gen_table(data, tab="code"))

@cli.command()
@argument("op", type=Choice(['show','clean']),default='show')
@option('--filter','-f', type=Choice(['h2', 'n11','cache']), default=None, required=False)
def http2_stat(op, filter):
    if op == 'show':
        data = hp.cpu_get('http2/stat')
        data = [[d[0], d[1], d[2]["stat"]] if isinstance(
            d[2], dict) else [d[0], d[1], d[2]] for d in data]
        if filter == "all":
            filter = None
        sprint(gen_table(data, tab="count", filter=filter))
    elif op == 'clean':
        data = hp.cpu_patch('http2/stat', general_clean_data)
        sprint(gen_table(data, tab="code"))


sf_http2_finish = ''
