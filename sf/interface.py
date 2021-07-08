from asyncio import wait
from sys import exit
from click import argument,Choice,STRING,option

from common.base import cli, sprint, get_args
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import *

def cpu_intf_filter(ctx, args, incomplete):
    comp = [('port_list', ''),
            ('ingress_config', ''),
            ('tcp_reass_config', ''),
            ('ip_reass_config', ''),
            ('deduplication_enable', ''),
            ('deduplication_config', ''),
            ]
    return [c for c in comp if c[0].startswith(incomplete)]


def cpu_intfs(ctx, args, incomplete):
    try:
        intfs = get_intfs_from_rest()
        return [i for i in intfs if incomplete in i]

    except Exception as e:
        sprint("\nget cpu interface error:{0}".format(e))
        exit()


def cpu_intf_field(ctx, args, incomplete):
    args = get_args(args)
    if 'ingress_config' in args:
        comp = [('default_action_id', ''),
                ('rule_to_action', ''),
                ('tuple_mode', ''), ]
    elif 'tcp_reass_config' in args:
        comp = []
    elif 'ip_reass_config' in args:
        comp = []
    elif 'deduplication_config' in args:
        comp = [
            # "deduplication_no_care_dscp",
            ("deduplication_no_care_interface",""),
            ("deduplication_no_care_ipid",""),
            ("deduplication_no_care_l2",""),
            ("deduplication_no_care_mac",""),
            ("deduplication_no_care_tcp_flag",""),
            ("deduplication_no_care_ttl",""),
            ("depth_bytes",""),
            ("depth_offset","")
        ]
    else:
        comp = []
    return [c for c in comp if c[0].startswith(incomplete)]


def cpu_intf_value(ctx, args, incomplete):
    comp = [('port_list', ''),
            ('ingress_config', ''),
            ('tcp_reass_config', ''),
            ('ip_reass_config', ''),
            ('deduplication_enable', ''),
            ('deduplication_config', '')
            ]
    return [c for c in comp if c[0].startswith(incomplete)]


sf_intf_expect = {
    "port_list": [
        'port_list'
    ],
    "deduplication_enable": [
        "deduplication_enable"
    ],
    "ingress_config": [
        "acl_rule_group",
        "default_action_id",
        'rule_to_action',
        "tuple_mode"
    ],
    "ip_reass_config": [
        "ip_reass_output_enable",
        "ip_reass_layers",
        "ip_reass_cosourcing_drop"
    ],
    "tcp_reass_config": [
        "inner_enable",
        "outer_enable"
    ],
    "deduplication_config": [
        "deduplication_no_care_dscp",
        "deduplication_no_care_interface",
        "deduplication_no_care_ipid",
        "deduplication_no_care_l2",
        "deduplication_no_care_mac",
        "deduplication_no_care_tcp_flag",
        "deduplication_no_care_ttl",
        # "depth_bytes",
        # "depth_offset"
    ]
}


@cli.command()
@argument("op", type=Choice(['show','clean','set','enable','disable']),default='show')
@argument("intf", type=STRING, autocompletion=cpu_intfs)
@argument("filter", type=STRING, autocompletion=cpu_intf_filter)
@argument("value", type=STRING, autocompletion=cpu_intf_field, required=False)
@argument("value2", type=STRING, autocompletion=cpu_intf_value, required=False)
@option('--device','-d', type=Choice(['orth','nf2000']),default='nf2000',required=False)
def intf(op, intf, device,filter=None, value=None, value2=None):
    restid = gen_intfs_cpu(intf)
    if not restid:
        sprint("PORT INDEX ERROR")
        exit()
    if op == 'show':
        for cpu in hp.cpus:
            data = []
            for idx in restid:
                surl = 'interfaces/config/{0}'.format(idx)
                tasks = [hp.loop.create_task(cpu.get(surl))]
                wait_task = wait(tasks)
                hp.loop.run_until_complete(wait_task)
                data += hp.data_from_tasks(tasks)
            tb = gen_table_sw(data, sf_intf_expect, cpu.addr, filter=filter)
            sprint(tb)
    elif op == 'clean':
        data = hp.cpu_patch('interfaces/config', general_clean_data)
        sprint(gen_table(data, tab="code"))
    elif op == "set":
        op_data = []
        if 'port_list'.startswith(filter):
            if device == 'orth':
                plist = [i for i in value.split(',')]
            else:
                plist = gen_intfs_sw(value)
            for idx in restid:
                cfg = {"op": "replace",
                       "path": "/{0}/{1}".format(idx, filter), "value": plist}
                op_data.append(cfg)
        elif 'ingress_config'.startswith(filter):
            data = None
            if 'default_action_id'.startswith(value):
                data = {'default_action_id': value2}
            elif "tuple_mode".startswith(value):
                data = {'tuple_mode': value2}
            elif 'rule_to_action'.startswith(value):
                data = {'rule_to_action': eval(value2)}
            if data:
                for idx in restid:
                    cfg = {"op": "replace",
                           "path": "/{0}/{1}".format(idx, filter), "value": data}
                    op_data.append(cfg)

        elif 'tcp_reass_config'.startswith(filter):
            for idx in restid:
                cfg = {"op": "replace",
                       "path": "/{0}/{1}".format(idx, filter), "value": value}
                op_data.append(cfg)
        elif 'ip_reass_config'.startswith(filter):
            for idx in restid:
                cfg = {"op": "replace",
                       "path": "/{0}/{1}".format(idx, filter), "value": value}
                op_data.append(cfg)
        elif 'deduplication_enable'.startswith(filter):
            for idx in restid:
                cfg = {"op": "replace",
                       "path": "/{0}/{1}".format(idx, filter), "value": value}
                op_data.append(cfg)
        elif 'deduplication_config'.startswith(filter):
            data = None
            if 'deduplication_no_care_l2'.startswith(value):
                data = {'deduplication_no_care_l2': value2}
            else:
                data = {value: value2}
            if data:
                for idx in restid:
                    cfg = {"op": "replace",
                           "path": "/{0}/{1}".format(idx, filter), "value": data}
                    op_data.append(cfg)
        data = hp.cpu_patch('interfaces/config', op_data)
        sprint(gen_table(data, tab="code"))


sf_intf_finish = ''
