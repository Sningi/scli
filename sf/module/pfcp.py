from click import argument,option,STRING,Choice
from sys import exit

from common.base import cli,sprint, get_args
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *


pfcp_cfg_field = [ ("bear","pfcp_send_bear_switch"),
                    ("learn","pfcp_element_study_switch"),
                    ("decode","pfcp_decode_switch"),
                    ("assoc_n2","pfcp_assoc_n2_switch")]
pfcp_cfg_dict = dict(pfcp_cfg_field)


def cfg_field(ctx, args, incomplete):
    args = get_args(args)
    if "enable" in args or "disable" in args:
        return [i for i in pfcp_cfg_field if i[0].startswith(incomplete)]
    elif "show" in args:
        return [i for i in pfcp_cfg_field if i[0].startswith(incomplete)]


def cfg_value(ctx, args, incomplete):
    field = [('1-1200', 'timeout value')]
    return [c for c in field if c[0].startswith(incomplete)]


@cli.command()  # @cli, not @click!
@argument("op", type=Choice(['show','enable','disable']),default='show')
@argument("field", type=STRING, autocompletion=cfg_field, required=False)
@argument("value", type=STRING, autocompletion=cfg_value, required=False)
def pfcp_cfg(op, field=None, value=None):
    if op == 'show':
        data = hp.cpu_get('pfcp/config')
        if field:
            field = pfcp_cfg_dict[field]
        sprint(gen_table(data, filter=field))
    elif op == 'enable' or op == 'disable':
        if not field or field not in pfcp_cfg_dict:
            sprint("{0} field is none".format(op))
            exit()
        op_data = [{"op": "replace",
                    "path": "/"+pfcp_cfg_dict[field],
                    "value":SWITCH[op]}]
        data = hp.cpu_patch('pfcp/config', op_data)
        sprint(gen_table(data, tab="code"))

@cli.command()
@argument("op", type=Choice(['show','clean']),default='show')
@option('--filter','-f', type=Choice(['smf', 'upf','count','failed']), default=None, required=False)
def pfcp_stat(op, filter):
    if 'show'.startswith(op):
        data = hp.cpu_get('pfcp/stat')
        sprint(gen_table(data, tab="count", filter=filter))
    elif 'clean'.startswith(op):
        data = hp.cpu_patch('pfcp/stat', general_clean_data)
        sprint(gen_table(data, tab="result"))

sf_pfcp_finish = ''
