import asyncio
import click

from base import cli
from utils.http_helper import hp
from utils.tools import gen_table, gen_table_sw, INTF_MAP, INTF_MAP_REST


def sw_intf_op(ctx, args, incomplete):
    comp = [('show', 'show feature'),
            ('clean', 'clean stat'),
            ('set', 'set feature'),
            ('enable', 'enable featrue'),
            ('disable', 'disable feature')]
    return [c for c in comp if incomplete in c[0]]


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
    if args[-2] == "show":
        comp = show_comp
    elif args[-2] == "set":
        comp = speed_comp
    elif args[-2] in ("enable", "disable"):
        comp = feature_comp
    else:
        comp = []
    return [comp[c] for c in comp if comp[c][0].startswith(incomplete)]


def sw_intfs(ctx, args, incomplete):
    intfs = set()
    try:
        if args[-1] == "clean":
            return [("all", "clean all")]
        data = hp.sw_get("interfaces")
        for d in data:
            if isinstance(d[2], list):
                for item in d[2]:
                    intfs.add(item.split('/')[-1])
        # .append(("all", "all port"))
        return [i for i in intfs if incomplete in i]

    except Exception as e:
        click.echo("\nget sw interface error:{0}".format(e))
        exit()

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
        "transceiver_mode",
    ]
}

@cli.command()
@click.argument("op", type=click.STRING, autocompletion=sw_intf_op)
@click.argument("intf", type=click.STRING, autocompletion=sw_intfs)
@click.argument("filter", type=click.STRING, autocompletion=sw_intf_filter, required=False)
def intf_sw(op, intf, filter=None):
    restid = []
    if "-" in intf:
        intfs = intf.split("-")
        if len(intfs) < 2 or intfs[0] not in INTF_MAP or intfs[-1] not in INTF_MAP:
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
    if not restid and op != "clean":
        click.echo("PORT INDEX ERROR")
        exit()
    if op == 'show':
        for sw in hp.sws:
            data = []
            for idx in restid:
                surl = 'interfaces/{0}'.format(idx)
                if filter:
                    surl += "?keys={}".format(filter)
                tasks = [hp.loop.create_task(sw.get(surl))]
                wait_task = asyncio.wait(tasks)
                hp.loop.run_until_complete(wait_task)
                data += hp.data_from_tasks(tasks)
            tb = gen_table_sw(data, sw_intf_expect,tab=sw.addr, filter=filter)
            click.echo(click.style(str(tb), fg='green',))
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
        click.echo(gen_table(data, tab="port"))
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
        click.echo(gen_table(data, tab="port"))
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
        click.echo(gen_table(data, tab="port"))
    elif op == 'clean':
        op_data = [{"op": "remove", "path": "/statistics"}]
        data = hp.sw_patch('interfaces', op_data)
        click.echo(gen_table(data, tab="all"))


sw_intf_finish = ''
