import click

from base import cli
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import *

def cpu_intf_op(ctx, args, incomplete):
    comp = [('show', 'show stat'),
              ('clean', 'clean stat'),
              ('set', 'set config')]
    return [c for c in comp if incomplete in c[0]]


def cpu_intf_filter(ctx, args, incomplete):
    comp = [('port_list', ''),
              ('ingress_config', ''),
              ('tcp_reass_config', ''),
              ('ip_reass_config', ''),
              ('deduplication_enable', '')]
    return [c for c in comp if c[0].startswith(incomplete)]


def cpu_intfs(ctx, args, incomplete):
    try:
        intfs = get_intfs_from_rest()
        return [i for i in intfs if incomplete in i]
        
    except Exception as e:
        click.echo("\ngetcpu interface error:{0}".format(e))
        exit()

@cli.command()
@click.argument("op", type=click.STRING, autocompletion=cpu_intf_op)
@click.argument("intf", type=click.STRING, autocompletion=cpu_intfs)
@click.argument("filter", type=click.STRING, autocompletion=cpu_intf_filter)
@click.argument("value", type=click.STRING, autocompletion=cpu_intf_filter, required=False)
def intf_cpu(op, intf, filter=None, value=None):
    restid = gen_intfs_cpu(intf)
    if not restid:
        click.echo("PORT INDEX ERROR")
        exit()
    if op == 'show':
        for cpu in hp.cpus:
            data = []
            for idx in restid:
                surl = 'interfaces/config/{0}'.format(idx)
                temp = [cpu.get(surl)]
                for i in temp:
                    data.append(i)
            tb = gen_table_intf_cpu(data, cpu.addr, filter=filter)
            click.echo(click.style(str(tb), fg='green'))
    elif op == 'clean':
        data = hp.cpu_patch('interfaces/config', general_clean_data)
        click.echo(gen_table(data, tab="code"))
    elif op == "set":
        plist = gen_intfs_sw(value)
        op_data = []
        for idx in restid:
            cfg = {"op": "replace", "path": "/{0}/{1}".format(idx,filter), "value": plist}
            op_data.append(cfg)
        data = hp.cpu_patch('interfaces/config', op_data)
        click.echo(gen_table(data, tab="code"))
