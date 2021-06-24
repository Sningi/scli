from click import argument,STRING,Choice
from sys import exit

from common.base import cli, sprint, get_args
from utils.http_helper import hp, get_hp
from utils.tools import *
from utils.static_data import *

def action_idx(ctx, args, incomplete):
    args = get_args(args)
    try:
        idxs = get_existed_action()
        if  [char for char in ["show", "delete", "enable", "disable"] if char in args]:
            comp = idxs
            if "show" in args:
                comp.append("all")
            return [i for i in comp if i.startswith(incomplete)]
        elif "create" in args:
            return [str(i) for i in range(1, 129) if str(i).startswith(incomplete) and str(i) not in idxs]
    except Exception as e:
        sprint("\nget cpu action error:{0}".format(e))
        exit()


additional_cfg = [
    ("remove_tunnel_header_gtp", '...'),
    ("remove_tunnel_header_vlan", "..."),
    ("remove_tunnel_header_vxlan", "..."),
    ("remove_tunnel_header_gre", '...'),
    ("remove_tunnel_header_mpls", '...'),
    ("g33_pad", '...'),
]


def action_type(ctx, args, incomplete):
    args = get_args(args)
    types = set()
    if "show" in args:
        types = [
            ('basis_actions', 'when has sw ignore basis action'),
            ('additional_actions', 'when has sw ignore basis action')]
    elif "enable" in args or "disable" in args:
        return [c for c in additional_cfg if c[0].startswith(incomplete)]
    elif "create" in args:
        types = [
            ('forward', 'forward interface'),
            # ('load_balance', 'load_balance interfaces'), now not support
            ('no_basis_action', 'when has sw ignore basis action')]
    elif "delete" in args:
        pass
    return [c for c in types if c[0].startswith(incomplete)]


def target_intf(ctx, args, incomplete):
    args = get_args(args)
    comp = set()
    if "disable" in args or "enable" in args:
        pass
    elif "create" in args:
        if "no_basis_action" in args:
            hp = get_hp(dev='switch')
            data = hp.sw_get("interfaces")
            for d in data:
                if isinstance(d[2], list):
                    for item in d[2]:
                        comp.add(item.split('/')[-1])
        elif "forward" in args:
            for it in get_intfs_from_rest():
                comp.add(it)
    return [i for i in comp if i.startswith(incomplete)]


action_expect = {
    "basis_actions":[
        "type",
        "interfaces",
        "load_balance_weight",
        "load_balance_mode",
    ],
    "additional_actions": [
        # "add_cpu_vlan",
        "remove_tunnel_header_gre",
        "remove_tunnel_header_gtp",
        "g33_pad",
    ]
}

@cli.command()  # @cli, not @click!
@argument("op", type=Choice(['show','create','delete','enable','disable']),default='show')
@argument("idx", type=STRING, autocompletion=action_idx)
@argument("type", type=STRING, autocompletion=action_type,default="basis_actions", required=False)
@argument("intf", type=STRING, autocompletion=target_intf, required=False)
def action(op, idx=None, type=None, intf=None):
    if 'show'.startswith(op):
        if intf:
            sprint("Invalid values input!!")
            return
        url = "actions"
        if idx and idx == "all":
            url += "?depth=3".format(idx)
        elif idx and idx.isdigit():
            url += "/{0}".format(idx)
        data = hp.cpu_get(url)
        sprint(str(gen_table_sw(data, action_expect, filter=type)))
    elif 'create'.startswith(op):
        restid = gen_intfs_sw(intf)
        restid += gen_intfs_cpu(intf)
        if not restid:
            if not restid:
                sprint("PORT INDEX ERROR")
                exit()

        if "no_basis_action".startswith(type):
            data = {
                str(idx): {
                    "basis_actions":
                    {
                        "type": 'no_basis_action',
                    },
                    "additional_actions": {
                        "add_cpu_vlan": {
                            "switch": 1,
                            "cpu_vlan_interfaces": restid,
                            "cpu_vlan_load_balance_mode": "outer_src_dst_ip",
                            "cpu_vlan_load_balance_weight": ""
                        }
                    }
                }
            }
        elif "forward".startswith(type):
            data = {
                str(idx): {
                    "basis_actions":
                    {
                        "type": 'forward',
                        "interfaces": restid,
                        "load_balance_weight": "",
                        "load_balance_mode": "wrr"
                    }
                }
            }
        data = hp.cpu_post('actions', data)
        sprint(str(gen_table(data,)))
    elif op == 'delete':
        if intf:
            sprint("Invalid values input!!")
            return
        field_names = ["code",  "ipaddr", "body"]
        if idx.isdigit():
            data = hp.cpu_delete('actions/{0}'.format(idx))
        else:
            sprint("Invalid values input!!")
            return
        sprint(str(gen_table(data,)))
    elif op in ("disable", "enable"):
        patch_data = [{
            "op": "replace",
            "path": "/additional_actions",
            "value": {
                type: {
                    "switch": SWITCH[op]
                }
            }
        }
        ]
        data = hp.cpu_patch('actions/{0}'.format(idx), patch_data)
        sprint(gen_table(data))


sf_action_finish = ''
