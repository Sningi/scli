import asyncio
from json import loads
from os import getgid
from click import argument, STRING
from sys import exit

from common.base import cli, sprint, get_args
from utils.http_helper import hp
from utils.tools import *


def sw_intf_op(ctx, args, incomplete):
    comp = [('show', 'show feature'),
            ('clean', 'clean stat'),
            ('set', 'set feature'),
            ('enable', 'enable featrue'),
            ('disable', 'disable feature'),
            ('bind', 'bind acl'),
            ('unbind', 'unbind acl'), ]
    return [c for c in comp if c[0].startswith(incomplete)]


show_comp = {'statistics': ('statistics', 'port stat'),
             'configuration': ('configuration', 'port  config'),
             'status': ('status', 'port status')}

speed_comp = {'speed_1G': ('speed_1G', '1000'),
              'speed_10G': ('speed_10G', '10000'),
              'speed_40G': ('speed_40G', '40000'),
              "speed_100G": ('speed_100G', '100000'),
              'speed_100G_FEC': ('speed_100G_FEC', '100001')}

feature_comp = {
    'rx': ('rx', 'port rx on'),
    'loopback': ('loopback', 'port loopback'),
    'force_tx': ('force_tx', 'port force_tx')}


def sw_intf_filter(ctx, args, incomplete):
    args = get_args(args)
    if "show" in args:
        comp = show_comp
    elif "set" in args:
        comp = speed_comp
    elif "enable" in args or "disable" in args:
        comp = feature_comp
    elif "bind" in args:
        hp = get_hp(dev='switch')
        data = hp.sw_get("acls")
        comp = []
        for one in data:
            comp += [(acl.split("/")[-1], "acl existed") for acl in one[2]]
        return [c for c in comp if c[0].startswith(incomplete)]
    else:
        comp = []
    return [comp[c] for c in comp if comp[c][0].startswith(incomplete)]


def sw_intfs(ctx, args, incomplete):
    args = get_args(args)
    intfs = set()
    try:
        if "clean" in args:
            return [("all", "clean all")]
        hp = get_hp(dev='switch')
        data = hp.sw_get("interfaces")
        for d in data:
            if isinstance(d[2], list):
                for item in d[2]:
                    intfs.add(item.split('/')[-1])
            elif isinstance(d[2],str):
                data = loads(d[2])
                if isinstance(data, list):
                    for item in data:
                        intfs.add(item.split('/')[-1])
        return [i for i in intfs if incomplete in i]

    except Exception as e:
        return []

sw_intf_expect = {
    "statistics": [
        "rx_mbps",
        "rx_kpps",
        "rx_packets",
        "rx_bytes",
        # "rx_dropped",
        "tx_mbps",
        "tx_kpps",
        "tx_packets",
        "tx_bytes",
        # "tx_dropped"
    ],
    "status": [
        "connector",
        "link_state",
        "support_speeds"
    ],
    "configuration": [
        "speed",
        "mtu",
        "enable",
        'iacl_name',
        "transceiver_mode",
    ]
}


@cli.command()
@argument("op", type=STRING, autocompletion=sw_intf_op)
@argument("intf", type=STRING, autocompletion=sw_intfs)
@argument("filter", type=STRING, autocompletion=sw_intf_filter, required=False)
def intf_sw(op, intf, filter):
    restid = gen_intfs_sw(intf)
    if not restid and op != "clean":
        sprint("PORT INDEX ERROR")
        exit()
    if op == 'show':
        for sw in hp.sws:
            data = []
            for idx in restid:
                surl = 'interfaces/{0}'.format(idx)
                if not filter:
                    filter = 'statistics'
                tasks = [hp.loop.create_task(sw.get(surl))]
                wait_task = asyncio.wait(tasks)
                hp.loop.run_until_complete(wait_task)
                data += hp.data_from_tasks(tasks)
            tb = gen_table_sw(data, sw_intf_expect, tab=sw.addr, filter=filter, portid=restid)
            sprint(tb)
    elif op == 'set':
        """
        {"op": "add", "path": "/configuration/speed", "value": "10000"},
        """
        data = []
        op_data = [{"op": "add", "path": "/configuration/speed",
                    "value": speed_comp[filter][-1]}]
        for idx in restid:
            temp = hp.sw_patch('interfaces/{0}'.format(idx), op_data)
            for i in temp:
                i[1] += " "+idx
                i[1] = i[1].split(".")[-1]
                data.append(i)
        sprint(gen_table(data, tab="port"))
    elif op == "enable":
        data = []
        op_data = [
            {"op": "add", "path": "/configuration/transceiver_mode", "value": filter}]
        for idx in restid:
            temp = hp.sw_patch('interfaces/{0}'.format(idx), op_data)
            for i in temp:
                i[1] += " "+idx
                i[1] = i[1].split(".")[-1]
                data.append(i)
        sprint(gen_table(data, tab="port"))
    elif op == "disable":
        data = []
        op_data = [
            {"op": "add", "path": "/configuration/transceiver_mode", "value": "rx"}]
        for idx in restid:
            temp = hp.sw_patch('interfaces/{0}'.format(idx), op_data)
            for i in temp:
                i[1] += " "+idx
                i[1] = i[1].split(".")[-1]
                data.append(i)
        sprint(gen_table(data, tab="port"))
    elif op == 'clean':
        op_data = [{"op": "remove", "path": "/statistics"}]
        data = hp.sw_patch('interfaces', op_data)
        sprint(gen_table(data, tab="all"))
    elif op == 'bind':
        '''
        {"op": "add", "path": "/configuration/iacl_name", "value": "acl1"}
        '''
        data = []
        op_data = [
            {"op": "add", "path": "/configuration/iacl_name", "value": filter}]
        for idx in restid:
            temp = hp.sw_patch('interfaces/{0}'.format(idx), op_data)
            for i in temp:
                i[1] += " "+idx
                i[1] = i[1].split(".")[-1]
                data.append(i)
        sprint(gen_table(data, tab="bind"))
    elif op == "unbind":
        data = []
        op_data = [
            {"op": "remove", "path": "/configuration/iacl_name"}]
        for idx in restid:
            temp = hp.sw_patch('interfaces/{0}'.format(idx), op_data)
            for i in temp:
                i[1] += " "+idx
                i[1] = i[1].split(".")[-1]
                data.append(i)
        sprint(gen_table(data, tab="bind"))


@cli.command()
def policies():
    data = hp.sw_get('forward_policies/group_2')
    sprint(str(gen_table(data, tab="bind")))


sw_intf_finish = ''
