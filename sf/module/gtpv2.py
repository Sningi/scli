from sys import exit
from click import argument,option,STRING,Choice

from common.base import cli,sprint, get_args
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *

gtpv2_cfg_field = [('decode', 'gtpv2_enable'),
                  ('cache', 'gtpv2_cache_enable'),
                  ('cdr', 'gtpv2_cdr_enable'),
                  ('gtpu_bear', 'gtpu_bear_enable'),
                  ('sgw_bear', 'sgw_bear_uinfo_enable'),
                  ('cdr_mode', 'cdr_mode'),
                  ('g06_dev_id', 'g06_dev_id'),
                  ('cdr_timeout', 'gtpv2_cdr_timeout'),
                  ('sig_timeout', 'gtpv2_sig_timeout'),
                  ('sig_timeout_mul', 'gtpv2_sig_timeout_mul'),
                  ('sgw_bear_uinfo_timeout', 'sgw_bear_uinfo_timeout'),
                  ]
gtpv2_cfg_dict = dict(gtpv2_cfg_field)


def cfg_field(ctx, args, incomplete):
    args = get_args(args)
    if "set" in args:
        return [i for i in gtpv2_cfg_field if i[0].startswith(incomplete) and "timeout" in i[0] or 'mode' in i[0] or 'dev_id' in i[0]]
    elif "enable" in args or "disable" in args:
        return [i for i in gtpv2_cfg_field if i[0].startswith(incomplete) and "timeout" not in i[0] and 'mode' not in i[0] and 'dev_id' not in i[0]]
    elif "show" in args:
        return [i for i in gtpv2_cfg_field if i[0].startswith(incomplete)]


def cfg_value(ctx, args, incomplete):
    field = [('1-1200', 'timeout value')]
    return [c for c in field if c[0].startswith(incomplete)]


@cli.command()  # @cli, not @click!
@argument("op", type=Choice(['show','enable','disable','set']),default='show')
@argument("field", type=STRING, autocompletion=cfg_field, required=False)
@argument("value", type=STRING, autocompletion=cfg_value, required=False)
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

@cli.command()
@argument("op", type=Choice(['show','clean']),default='show')
@option('--filter','-f', type=Choice(['sgw', 'bear','node','refill','cache']), default=None, required=False)
def gtpv2_stat(op, filter):
    if 'show'.startswith(op):
        data = hp.cpu_get('gtpv2/stat')
        sprint(gen_table(data, tab="count", filter=filter))
    elif 'clean'.startswith(op):
        data = hp.cpu_patch('gtpv2/stat', general_clean_data)
        sprint(gen_table(data, tab="result"))

sf_gtpv2_finish = ''
