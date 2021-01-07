import click

from base import cli, clean_data
from utils.http_helper import hp
from utils.tools import *

def action_op(ctx, args, incomplete):
    op = [('show', 'show action'),
            ('create', 'create action'), 
            ('delete', 'delete action'),
            ('set', 'modify action'),              ]
    return [c for c in op if c[0].startswith(incomplete)]

def action_idx(ctx, args, incomplete):
    try:
        idxs = get_existed_action()
        if args[-1] in ["show", "delete",'set']:
            return [i for i in idxs if incomplete in i]
        elif args[-1] in ["create"]:
            return [str(i) for i in range(1,129) if str(i).startswith(incomplete) and str(i) not in idxs]
    except Exception as e:
        click.echo("\ngetcpu interface error:{0}".format(e))
        exit()

def config_value(ctx, args, incomplete):
    colors = [('enable', 'enable feature'),
              ('disable', 'set config')]
    return [c for c in colors if c[0].startswith(incomplete)]

def action_type(ctx, args, incomplete):
    if args[-2] in ("delete, show"):
        return [("press_enter",),("push_enter",),]
    else:
        click.echo("error")
        types = [('forward', 'forward interface'),
                ('load_balance', 'load_balance interfaces')]
        return [c for c in types if c[0].startswith(incomplete)]

def target_intf(ctx, args, incomplete):
    intfs = get_intfs_from_rest()
    return [i for i in intfs if incomplete in i]

@cli.command()# @cli, not @click!
@click.argument("op", type=click.STRING, autocompletion=action_op)
@click.argument("idx", type=click.STRING, autocompletion=action_idx, required=False)
@click.argument("type", type=click.STRING, autocompletion=action_type, required=False)
@click.argument("intf", type=click.STRING, autocompletion=target_intf, required=False)
def action(op, idx=None, type=None, intf=None):
    if op == 'show':
        url = "actions"
        if idx:
            url += "/{0}".format(idx)
        data = hp.cpu_get(url)
        print(data)
        print(gen_table(data,))
    elif op == 'create':
        data = {str(idx):{
                        "basis_actions":
                        {
                            "type": type,
                            "interfaces": [intf],
                            "load_balance_weight": "", 
                            "load_balance_mode": ""
                        }
                    }
                }
        data = hp.cpu_post('actions', data)
        print(gen_table(data))
    elif op == 'delete':
        data = hp.cpu_delete('actions/{0}'.format(idx))
        print(gen_table(data))