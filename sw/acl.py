from click import argument, option, STRING, Choice

from common.base import cli, sprint, get_args
from utils.http_helper import get_hp, hp
from utils.tools import gen_table, gen_table_sw, INTF_MAP, INTF_MAP_REST

def sw_acl_group(ctx, args, incomplete):
    args = get_args(args)
    if "show" in args or "delete" in args or "add" in args:
        hp = get_hp('switch')
        data = hp.sw_get("acls")
        if not data:
            return []
        comp = []
        for one in data:
            comp += [(acl.split("/")[-1], "acl existed") for acl in one[2]]
        if "delete" in args:
            comp.append(("all", 'all'))
    elif "create":
        comp = ["group_{0}".format(idx) for idx in range(1, 11)]
    return [c for c in comp if c[0].startswith(incomplete)]


def sw_acl_idx(ctx, args, incomplete):
    if "show" in args or "delete" in args or "add" in args:
        hp = get_hp(dev='switch')
        data = hp.sw_get("acls/{0}".format(args[-1]))
        comp = []
        for one in data:
            if args[-1] in one[2]:
                comp += [(aid.split("/")[-1], "acl id")
                         for aid in one[2][args[-1]]['acl_entries']]
            comp.append(("all", "all acl"))
    elif "create":
        comp = [(str(idx), "acl id") for idx in range(1, 1900)]
    return [c for c in comp if c[0].startswith(incomplete)]


show_comp = {'statistics': ('statistics', 'port stat'),
             'configuration': ('configuration', 'port  config'),
             'status': ('status', 'port status')}


def sw_acl_filter(ctx, args, incomplete):
    if "show" in args:
        comp = show_comp
    elif "set" in args:
        comp = []
    else:
        comp = []
    return [comp[c] for c in comp if comp[c][0].startswith(incomplete)]


sw_acl_expect = {
    "statistics": [
        "hitcount"
    ],
    "status": [
        "applied_status"
    ],
    "configuration": [
        "ace_type",
        "action",
        "evif_name",
        "src_ip",
        'src_port',
        "dst_ip",
        'dst_port',
        'protocol',
        "outer_vlan",
        'vlanid',
        "vlan_cmd",
        "en_count",
        # "slice",
        # "delete_ipinip_tunnel",
        # "comment",
    ]
}


@cli.command()
@argument("op", type=Choice(['show','create','delete','add']),default='show')
@argument("group", type=STRING, autocompletion=sw_acl_group)
@argument("idx", type=STRING, autocompletion=sw_acl_idx, required=False)
@argument("filter", type=STRING, autocompletion=sw_acl_filter, required=False)
@option('--type', '-type', type=Choice(['ipv4', 'ipv6'], case_sensitive=False), default="ipv4", required=False)
@option('--vlan', '-vlan', type=STRING, required=False)
@option('--sip', type=STRING, required=False)
@option('--dip', type=STRING, required=False)
@option('--sport', type=STRING, required=False)
@option('--dport', type=STRING, required=False)
@option('--protocol', type=STRING, required=False)
@option('--vlanid', type=STRING, required=False)
@option('--vlan_cmd', type=STRING, required=False)
@option('--en_count', type=Choice(['ture', 'false']), required=False)
@option('--action', type=Choice(['forward', 'copy'], case_sensitive=False))
@option('--evif_name', type=STRING)
def acl_sw(op, group, idx, filter, type, vlan, sip, dip, sport, dport, protocol, action, evif_name, vlanid, vlan_cmd, en_count):
    if 'show'.startswith(op):
        if not filter:
            filter = "configuration"
        url = "acls/{0}/acl_entries".format(group)
        if idx and idx != "all":
            url += "/"+idx
        url += "?depth=1"
        data = hp.sw_get(url)
        tb = gen_table_sw(data, sw_acl_expect, tab="id", filter=filter)
        sprint(tb)
    elif 'create'.startswith(op):
        op_data = {
            group: {
                "configuration": {
                    "acl_type": "ip"
                },
                "acl_entries": {
                    idx: {
                        "configuration":
                        {
                            "ace_type": type,
                            "src_ip": sip,
                            "src_port": sport,
                            "dst_ip": dip,
                            "dst_port": dport,
                            "action": action,
                            "evif_name": evif_name,
                            'protocol': protocol,
                            'outer_vlan': vlan,
                            "en_count": en_count,
                            'vlanid': vlanid,
                            "vlan_cmd": vlan_cmd,
                        }
                    }
                }
            }
        }
        data = hp.sw_post('acls', op_data)
        sprint(gen_table(data, tab="port"))
    elif 'add'.startswith(op):
        op_data = {
                    idx: {
                        "configuration":
                        {
                            "ace_type": type,
                            "src_ip": sip,
                            "src_port": sport,
                            "dst_ip": dip,
                            "dst_port": dport,
                            "action": action,
                            "evif_name": evif_name,
                            'protocol': protocol,
                            'outer_vlan': vlan,
                            "en_count": en_count,
                            'vlanid': vlanid,
                            "vlan_cmd": vlan_cmd,
                        }
                    }
                }
        url = "acls/{0}/acl_entries".format(group)
        data = hp.sw_post(url, op_data)
        sprint(gen_table(data, tab="port"))
    elif op == "delete":
        if "all".startswith(group):
            data = hp.sw_delete("forward_policies")
        else:
            # sample as forward_policies
            data = hp.sw_delete("forward_policies/{0}".format(group))
        sprint(gen_table(data, tab="switch"))

sw_acl_finish = ''
