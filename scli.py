import json
import os
import click
from itertools import zip_longest

from config import Config
from base import cli
from utils.http_helper import hp
from utils.tools import *

from sf.acl import sf_acl_finish
from sf.action import sf_action_finish
from sf.interface import sf_intf_finish

from sw.interface import sw_intf_finish
from sw.acl import sw_acl_finish

# module
from sf.module.sctp import sf_sctp_finish
from sf.module.http2 import sf_http2_finish
from sf.module.gtpu import sf_gtpu_finish
from sf.module.gtpv2 import sf_gtpv2_finish
from sf.module.ip_reass import sf_ipreass_finish
from sf.module.sslcon import sf_sslcon_finish
from sw.module.sslcon import sw_sslcon_finsh

from syscfg import sf_sys_finish


def dev_op(ctx, args, incomplete):
    comp = [('show', 'show stat')]
    return [c for c in comp if incomplete in c[0]]


def dev_type(ctx, args, incomplete):
    comp = [('cpu', 'cpu ip'),
            ('switch', 'switch ip'),
            ('all', 'all ip')]
    return [c for c in comp if incomplete in c[0]]


@cli.command()
@click.argument("op", type=click.STRING, autocompletion=dev_op)
@click.argument("dev", type=click.STRING, autocompletion=dev_type)
def dev_ip(op, dev):
    data = []
    if op == "show":
        if dev == "all":
            field_names = ["index", "SWITCH", "CPU"]
            for index, group in enumerate(zip_longest(Config.cpu_addrs, Config.sw_addrs)):
                data.append([index + 1, group[0], group[1]])
            tb = create_custiom_table(data, field_names)
            click.echo(tb)
        elif dev == "cpu":
            field_names = ["index",  "CPU"]
            for index, group in enumerate(Config.cpu_addrs):
                data.append([index + 1, group])
            tb = create_custiom_table(data, field_names)
            click.echo(tb)
        elif dev == "switch":
            field_names = ["index",  "SWITCH"]
            for index, group in enumerate(Config.sw_addrs):
                data.append([index + 1, group])
            tb = create_custiom_table(data, field_names)
            click.echo(tb)


@cli.command()
@click.argument("dev", type=click.STRING, autocompletion=dev_type)
@click.argument("url", type=click.STRING, autocompletion=dev_type)
def get(dev, url):
    if 'cpu'.startswith(dev):
        data = hp.cpu_get(url)
        click.echo(json.dumps(data,indent=2))
    elif "switch".startswith(dev):
        data = hp.sw_get(url)
        click.echo(json.dumps(data,indent=2))


if __name__ == '__main__':
    pass
