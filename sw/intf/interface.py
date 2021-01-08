import click

from base import cli
from utils.http_helper import hp
from utils.tools import gen_table, gen_table_intf, INTF_MAP,INTF_MAP_REST

def sw_intf_op(ctx, args, incomplete):
    comp = [('show', 'show stat'),
              ('clean', 'clean stat')]
    return [c for c in comp if incomplete in c[0]]


def sw_intf_filter(ctx, args, incomplete):
    comp = [('statistics', 'chunk stat'),
              ('configuration', 'error stat'),
              ('status', 'total stat')]
    return [c for c in comp if incomplete in c[0]]


def sw_intfs(ctx, args, incomplete):
    intfs = set()
    try:
        data = hp.sw_get("interfaces")
        for d in data:
            if isinstance(d[2],list):
                for item in d[2]:
                    intfs.add(item.split('/')[-1])
        return [i for i in intfs if incomplete in i]#.append(("all", "all port"))
        
    except Exception as e:
        click.echo("\nget sw interface error:{0}".format(e))
        exit()

@cli.command()
@click.argument("op", type=click.STRING, autocompletion=sw_intf_op)
@click.argument("intf", type=click.STRING, autocompletion=sw_intfs)
@click.argument("filter", type=click.STRING, autocompletion=sw_intf_filter)
def intf_stat_sw(op, intf, filter=None):
    restid = []
    if "-" in intf:
        intfs = intf.split("-")
        if len(intfs)<2 or intfs[0] not in INTF_MAP or intfs[-1] not in INTF_MAP:
            click.echo("PORT INDEX ERROR")
            exit()
        for i in range(INTF_MAP[intfs[0]], INTF_MAP[intfs[-1]]+1):
            restid.append(INTF_MAP_REST[i])
    elif ',' in intf:
        intfs = intf.split(",")
        for i in intfs:
            if i in INTF_MAP:
                restid.append(i)
    elif intf in INTF_MAP:
        restid.append(intf)
    if not restid:
        click.echo("PORT INDEX ERROR")
        exit()
    if op == 'show':
        for sw in hp.sws:
            data = []
            for idx in restid:
                surl = 'interfaces/{0}'.format(idx)
                if filter:
                    surl += "?keys={}".format(filter)
                temp = [sw.get(surl)]
                for i in temp:
                    data.append(i)
            tb = gen_table_intf(data, tab=sw.addr, filter=filter)
            click.echo(click.style(str(tb), fg='green',))
    elif op == 'clean':
        for idx in restid:
            op_data = [{"op": "remove", "path": "/statistics"}]
            data = hp.sw_patch('interfaces/{0}'.format(idx),op_data)
            click.echo(gen_table(data, tab=idx))
