import click

from base import cli, SF_PRINT
from utils.http_helper import hp
from utils.tools import *

def action_op(ctx, args, incomplete):
    op = [  ('show', 'show action'),
            ('create', 'create action'), 
            ('delete', 'delete action')]
    return [c for c in op if c[0].startswith(incomplete)]

def action_idx(ctx, args, incomplete):
    try:
        idxs = get_existed_action()
        if args[-1] in ["show", "delete"]:
            comp = idxs 
            if args[-1] == "show":
                comp.append("all")
            return [i for i in comp if incomplete in i]
        elif args[-1] in ["create"]:
            return [str(i) for i in range(1,129) if str(i).startswith(incomplete) and str(i) not in idxs]
    except Exception as e:
        SF_PRINT("\ngetcpu interface error:{0}".format(e))
        exit()

def action_type(ctx, args, incomplete):
    if args[-2] in ("delete, show"):
        return []
    else:
        types = [
                #('forward', 'forward interface'),  now not support
                #('load_balance', 'load_balance interfaces'), now not support
                ('no_basis_action', 'when has sw ignore basis action')]
        return [c for c in types if c[0].startswith(incomplete)]

def target_intf(ctx, args, incomplete):
    intfs = set()
    data = hp.sw_get("interfaces")
    for d in data:
        if isinstance(d[2],list):
            for item in d[2]:
                intfs.add(item.split('/')[-1])
    return [i for i in intfs if incomplete in i]

@cli.command()# @cli, not @click!
@click.argument("op", type=click.STRING, autocompletion=action_op)
@click.argument("idx", type=click.STRING, autocompletion=action_idx, required=False)
@click.argument("type", type=click.STRING, autocompletion=action_type, required=False)
@click.argument("intf", type=click.STRING, autocompletion=target_intf, required=False)
def action(op, idx=None, type=None, intf=None):
    if op == 'show':
        if type or intf:
            SF_PRINT("Invalid values input!!")
            return
        url = "actions"
        if idx and idx == "all":
            url += "?depth=3".format(idx)
        elif idx and idx.isdigit():
            url += "/{0}".format(idx)
        data = hp.cpu_get(url)
        field_names = ["code",  "ipaddr", "body"]
        SF_PRINT(str(create_custiom_table(data,field_names)))
    elif op == 'create':
        restid = []
        if "-" in intf:
            intfs = intf.split("-")
            intfs = [ int(i) for i in intfs]
            if len(intfs)<2 or int(intfs[0]) not in INTF_MAP_REST or intfs[-1] not in INTF_MAP_REST:
                SF_PRINT("PORT INDEX ERROR")
                return 
            for i in intfs:
                restid.append(INTF_MAP_REST[i])
        elif ',' in intf:
            intfs = intf.split(",")
            intfs = [ int(i) for i in intfs]
            for i in intfs:
                if i in INTF_MAP_REST:
                    restid.append(INTF_MAP_REST[i])
        elif intf.isdigit() and int(intf) in INTF_MAP_REST:
            intf = int(intf)
            print(intf)
            restid.append(INTF_MAP_REST[intf])
        if not restid:
            SF_PRINT("PORT INDEX ERROR")
            return
        data = {str(idx):{
                        "basis_actions":
                        {
                            "type": type,
                        },
                        "additional_actions": {
                            "add_cpu_vlan": {
                                "switch": 1,
                                "cpu_vlan_interfaces":restid,
                                "cpu_vlan_load_balance_mode":"outer_src_dst_ip",
                                "cpu_vlan_load_balance_weight":""  
                                }
                            }
                    }
                }
        data = hp.cpu_post('actions', data)
        field_names = ["code",  "ipaddr", "body"]
        SF_PRINT(str(create_custiom_table(data,field_names)))
    elif op == 'delete':
        if type or intf:
            SF_PRINT("Invalid values input!!")
            return
        field_names = ["code",  "ipaddr", "body"]
        if idx.isdigit():
            data = hp.cpu_delete('actions/{0}'.format(idx))
        else:
            SF_PRINT("Invalid values input!!")
            return
        SF_PRINT(str(create_custiom_table(data,field_names)))
