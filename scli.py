import os
import click

from config import Config
from base import cli
from utils.http_helper import hp
from utils.tools import create_custiom_table 

from sf.acl.acl import acl
from sf.action.action import action
from sw.intf.interface import intf_stat_sw
from sf.intf.interface import intf_cfg_cpu
#module
from sf.module.sctp import sctp_cfg, sctp_stat
from sf.module.http2 import http2_config, http2_stat
from sf.module.ip_reass import ipreass_config, ipreass_stat
from sf.module.sslcon import *

def dev_op(ctx, args, incomplete):
    comp = [('show', 'show stat')]
    return [c for c in comp if incomplete in c[0]]


def dev_type(ctx, args, incomplete):
    comp = [    ('cpu', 'cpu ip'),
                ('switch', 'switch ip'),
                ('all', 'all ip')]
    return [c for c in comp if incomplete in c[0]]

@cli.command()
@click.argument("op", type=click.STRING, autocompletion=dev_op)
@click.argument("dev", type=click.STRING, autocompletion=dev_type)
def show_devcontrol_ip(op, dev):
    data = []
    if op == "show":
        if dev == "all":
            field_names = ["index", "SWITCH", "CPU"]
            for index, group in enumerate(zip(Config.cpu_addrs,Config.sw_addrs)):
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

if __name__ == '__main__':
    pass
