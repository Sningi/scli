from sys import argv, exit
from click import argument, option, STRING, Choice

from common.base import cli,sprint, get_args
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *


def sctp_operation(ctx, args, incomplete):
    comp = [('show', 'show config'),
              ('enable', 'enable feature'),
              ('disable', 'disble feature'),
              ('set', 'set timeout')]
    return [c for c in comp if c[0].startswith(incomplete)]


sctp_cfg_field = [('sctp_decode', 'sctp_decode_enable'),
                    ('sctp_decode_upproto', 'sctp_decode_upproto_enable'),
                    ('ngap_decode', 'ngap_decode_enable'),
                    ('ngap_skip_paging', 'ngap_decode_skip_paging_enable'),
                    ('ngap_cdr', 'ngap_cdr_enable'),
                    ('nas_decrypt', 'ngap_nas_decrypt_enable'),
                    ('nas_decrypted_output', 'ngap_nas_decrypted_output_enable'),
                    ('learn_ip', 'learn_ip'),
                    ('ngap_imsi_timeout', 'ngap_imsi_timeout_cycle'),
                    ('ngap_cdr_timeout', 'ngap_cdr_timeout'),
                    ('ngap_small_cdr_timeout', 'ngap_small_cdr_timeout'),
                    ('ngap_handover_cdr_timeout', 'ngap_handover_cdr_timeout'),
                    ("sctp_frag_assemble", "sctp_frag_assemble"),
                    ("s1ap_decode_enable", "s1ap_decode_enable"),
                    ("s1ap_decode_skip_paging_enable", "s1ap_decode_skip_paging_enable"),
                    ("s1ap_cdr_enable", "s1ap_cdr_enable"),
                    ("s1ap_cdr_output_enable", "s1ap_cdr_output_enable"),
                    ("s1ap_nas_decrypt_enable", "s1ap_nas_decrypt_enable"),
                    ("s1ap_nas_decrypted_output_enable", "s1ap_nas_decrypted_output_enable"),
                    ("s1ap_learn_lte_enable", "s1ap_learn_lte_enable"),
                    ("s1ap_cdr_timeout", "s1ap_cdr_timeout"),
                    ("s1ap_small_cdr_timeout", "s1ap_small_cdr_timeout"),
                    ("s1ap_handover_cdr_timeout", "s1ap_handover_cdr_timeout"),
                    ("s1ap_cdr_multi", "s1ap_cdr_multi"),
                    ("s1ap_imsi_timeout_cycle", "s1ap_imsi_timeout_cycle"),
                    ("sctp_n2_n4_n11_assoc_switch", 'sctp_n2_n4_n11_assoc_switch'),
                    ("diameter_decode_enable", "diameter_decode_enable"),
                    ("s6a_cdr_proc_enable", "s6a_cdr_proc_enable"),
                    ("s6a_cdr_timeout", "s6a_cdr_timeout"),
                    ("s6a_auth_ass_timeout", "s6a_auth_ass_timeout"),
                    ("s6a_create_imsi_vector_open", "s6a_create_imsi_vector_open"),
                  ]
sctp_cfg_dict = dict(sctp_cfg_field)


def cfg_field(ctx, args, incomplete):
    args = get_args(args)
    if "set" in args:
        return [i for i in sctp_cfg_field if i[0].startswith(incomplete)]# and "timeout" in i[0] or 'mul' in i[0] or 'swit' in i[0]]
    elif "enable" in args or "disable" in args:
        return [i for i in sctp_cfg_field if i[0].startswith(incomplete) and "timeout" not in i[0]]
    elif "show" in args:
        return [i for i in sctp_cfg_field if i[0].startswith(incomplete)]


def cfg_value(ctx, args, incomplete):
    field = [('1-1200', 'timeout value')]
    return [c for c in field if c[0].startswith(incomplete)]


@cli.command()  # @cli, not @click!
@argument("op", type=Choice(['show','enable','disable','set']),default='show')
@argument("field", type=STRING, autocompletion=cfg_field, required=False)
@argument("value", type=STRING, autocompletion=cfg_value, required=False)
def sctp_cfg(op, field=None, value=None):
    if op == 'show':
        data = hp.cpu_get('sctp/config')
        if field:
            field = sctp_cfg_dict[field]
        sprint(gen_table(data, filter=field))
    elif op == 'enable' or op == 'disable':
        if not field or field not in sctp_cfg_dict:
            sprint("{0} field is none".format(op))
            exit()
        op_data = [{"op": "replace",
                    "path": "/"+sctp_cfg_dict[field],
                    "value":SWITCH[op]}]
        data = hp.cpu_patch('sctp/config', op_data)
        sprint(gen_table(data, tab="code"))
    elif op == "set":
        op_data = [{"op": "replace",
                    "path": "/"+sctp_cfg_dict[field],
                    "value":value}]
        data = hp.cpu_patch('sctp/config', op_data)
        sprint(gen_table(data, tab="code"))

@cli.command()
@argument("op", type=Choice(['show','clean']),default='show')
@option('--filter','-f', type=Choice(['chunk', 'error','total']), default=None, required=False)
def sctp_stat(op, filter):
    if 'show'.startswith(op):
        data = hp.cpu_get('sctp/stat')
        sprint(gen_table(data, tab="count", filter=filter))
    elif 'clean'.startswith(op):
        data = hp.cpu_patch('sctp/stat', general_clean_data)
        sprint(gen_table(data, tab="result"))


ngap_type = {'small_cdr': ("small_cdr", 'ngap/small_cdr/stat'),
             'nas_dec': ('nas_dec', "ngap/nas_dec/stat"),
             'sig': ("sig", 'ngap/sig/stat'),
             'ngap': ("ngap", 'ngap/stat'),
             "sync": ("sync", 'sig/sync'),
             '5gs': ("5gs", 'sig/5gs_arch'),
             }


def ngap_type_comp(ctx, args, incomplete):
    return [ngap_type[key] for key in ngap_type if ngap_type[key][0].startswith(incomplete)]

@cli.command()
@argument("op", type=Choice(['show','clean']),default='show')
@argument("type", type=STRING, autocompletion=ngap_type_comp)
@option('--filter','-f', type=STRING, default=None, required=False)
def ngap_stat(op, type, filter):
    if op == 'show':
        if type == '5gip':
            data = hp.cpu_get('sctp/sig/udm')
            sprint(gen_table(data, tab="udm", filter=filter))
            data = hp.cpu_get('sctp/sig/udr')
            sprint(gen_table(data, tab="udr", filter=filter))
            data = hp.cpu_get('sctp/sig/nrf')
            sprint(gen_table(data, tab="nrf", filter=filter))
            data = hp.cpu_get('sctp/sig/pcf')
            sprint(gen_table(data, tab="pcf", filter=filter))
            data = hp.cpu_get('sctp/sig/nssf')
            sprint(gen_table(data, tab="nssf", filter=filter))
            data = hp.cpu_get('sctp/sig/af')
            sprint(gen_table(data, tab="af", filter=filter))
            data = hp.cpu_get('sctp/sig/amf_n11')
            sprint(gen_table(data, tab="amf_n11", filter=filter))
            data = hp.cpu_get('sctp/sig/amf_n2')
            sprint(gen_table(data, tab="amf_n2", filter=filter))
            data = hp.cpu_get('sctp/sig/smf_n11')
            sprint(gen_table(data, tab="smf_n11", filter=filter))
            data = hp.cpu_get('sctp/sig/ausf_n12')
            sprint(gen_table(data, tab="ausf_n12", filter=filter))
            data = hp.cpu_get('sctp/sig/amf_n12')
            sprint(gen_table(data, tab="amf_n12", filter=filter))
        else:
            data = hp.cpu_get('sctp/{0}'.format(ngap_type[type][1]))
            if type == '5gs':
                import json
                sprint(json.dumps(data,indent=2))
            else:
                sprint(gen_table(data, tab="count", filter=filter))
    elif op == 'clean':
        if type == '5gs':
            data = hp.cpu_delete('sctp/sig/5gs_arch')
        elif type == '5gip':
            data = hp.cpu_delete('sctp/sig/5g_ip')
        else:
            data = hp.cpu_patch('sctp/stat', general_clean_data)
        sprint(gen_table(data, tab="result"))


sf_sctp_finish = ''
