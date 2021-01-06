import click

from base import cli, clean_data
from utils.http_helper import hp
from utils.tools import gen_table, gen_table_intf_cpu, INTF_CPU_MAP,INTF_CPU_MAP_REST

def cpu_intf_op(ctx, args, incomplete):
    comp = [('show', 'show stat'),
              ('clean', 'clean stat')]
    return [c for c in comp if incomplete in c[0]]


def cpu_intf_filter(ctx, args, incomplete):
    comp = [('port_list', ''),
              ('ingress_config', ''),
              ('tcp_reass_config', ''),
              ('ip_reass_config', ''),
              ('deduplication_enable', '')]
    return [c for c in comp if c[0].startswith(incomplete)]


def cpu_intfs(ctx, args, incomplete):
    intfs = set()
    try:
        data = hp.cpu_get("interfaces/config")
        for d in data:
            if isinstance(d[2],dict):
                for item in d[2]:
                    intfs.add(item)
        return [i for i in intfs if incomplete in i]
        
    except Exception as e:
        click.echo("\ngetcpu interface error:{0}".format(e))
        exit()

@cli.command()
@click.argument("op", type=click.STRING, autocompletion=cpu_intf_op)
@click.argument("intf", type=click.STRING, autocompletion=cpu_intfs)
@click.argument("filter", type=click.STRING, autocompletion=cpu_intf_filter)
def intf_stat_cpu(op, intf, filter=None):
    restid = []
    if "-" in intf:
        intfs = intf.split("-")
        if len(intfs)<2 or intfs[0] not in INTF_CPU_MAP or intfs[-1] not in INTF_CPU_MAP:
            click.echo("PORT INDEX ERROR")
            exit()
        for i in range(INTF_CPU_MAP[intfs[0]], INTF_CPU_MAP[intfs[-1]]+1):
            restid.append(INTF_CPU_MAP_REST[i])
    elif ',' in intf:
        intfs = intf.split(",")
        for i in intfs:
            if i in INTF_CPU_MAP:
                restid.append(i)
    elif intf in INTF_CPU_MAP:
        restid.append(intf)
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
        data = hp.cpu_patch('interfaces/config/', clean_data)
        click.echo(gen_table(data, tab="code"))