import asyncio
import click

from base import cli
from utils.http_helper import hp
from utils.tools import gen_table, gen_table_sw, INTF_MAP, INTF_MAP_REST


def sw_acl_op(ctx, args, incomplete):
    comp = [('show', 'show aco'),
            ('create', 'create acl'),
            ('delete', 'deletw acl')]
    return [c for c in comp if c[0].startswith(incomplete)]


def sw_acl_group(ctx, args, incomplete):
    if "show".startswith(args[-1]) or "delete".startswith(args[-1]):
        data = hp.sw_get("acls")
        comp = []
        for one in data:
            comp += [(acl.split("/")[-1], "acl existed") for acl in one[2]]
    elif "create":
        comp = ["acl_{0}".format(idx) for idx in range(1, 11)]
    return [c for c in comp if c[0].startswith(incomplete)]


def sw_acl_idx(ctx, args, incomplete):
    if "show".startswith(args[-2]) or "delete".startswith(args[-2]):
        data = hp.sw_get("acls/{0}".format(args[-1]))
        comp = []
        for one in data:
            comp += [(aid.split("/")[-1], "acl id")
                     for aid in one[2][args[-1]]['acl_entries']]
            comp.append(("all","all acl"))
    elif "create":
        comp = ["acl_{0}".format(idx) for idx in range(1, 11)]
    return [c for c in comp if c[0].startswith(incomplete)]


show_comp = {'statistics': ('statistics', 'port stat'),
             'configuration': ('configuration', 'port  config'),
             'status': ('status', 'port status')}


def sw_acl_filter(ctx, args, incomplete):
    if args[-3] == "show":
        comp = show_comp
    elif args[-2] == "set":
        comp = speed_comp
    elif args[-2] in ("enable", "disable"):
        comp = feature_comp
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
@click.argument("op", type=click.STRING, autocompletion=sw_acl_op)
@click.argument("group", type=click.STRING, autocompletion=sw_acl_group, required=False)
@click.argument("idx", type=click.STRING, autocompletion=sw_acl_idx,required= False)
@click.argument("filter", type=click.STRING, autocompletion=sw_acl_filter,required= False)
def acl_sw(op, group, idx, filter):
    if 'show'.startswith(op):
        if not filter:
            filter = "configuration"
        url = "acls/{0}/acl_entries".format(group)
        if idx and idx !="all":
            url += "/"+idx
        url += "?depth=1"
        data = hp.sw_get(url)
        tb = gen_table_sw(data, sw_acl_expect,tab="id", filter=filter)
        click.echo(click.style(str(tb), fg='green',))
    elif 'create'.startswith(op):
        op_data = {
            "test": {"configuration": {"comment": "", "acl_type": "ip"}, "acl_entries": {
                "10": {"configuration":
                       {"ace_type": "ipv4", "src_ip": "1.1.1.1", "dst_ip": "1.1.1.1",
                        "action": "forward", "evif_name": "10", "en_count": "true"
                        }
                       }
            }
            }
        }
        data = hp.sw_post('acls', op_data)
        click.echo(gen_table(data, tab="port"))
    elif op == "delete":
        data = []
        op_data = [
            {"op": "add", "path": "/configuration/transceiver_mode", "value": idx}]
        for idx in restid:
            temp = hp.sw_patch('interfaces/{0}'.format(idx), op_data)
            for i in temp:
                i[1] += " "+idx
                i[1] = i[1].split(".")[-1]
                data.append(i)
        click.echo(gen_table(data, tab="port"))


sw_acl_finish = ''
