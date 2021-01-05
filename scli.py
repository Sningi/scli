import os
import click

from config import Config
from base import cli
from utils.http_helper import hp
from utils.tools import gen_table
from sf.module.sctp import sctp_config, sctp_stat
from sw.intf.interface import intf_stat_sw
from sf.acl.acl import acl
from sf.action.action import action



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
def show_ip(op, dev):
    if op == "show":
        if dev == "all":
            data = []
            for index, cpu in enumerate(Config.cpu_addrs):
                data.append([
                    0,
                    cpu,
                    {}
                ])
            print(gen_table(data, tab="addr"))
        elif dev == "cpu":
            print()
        elif dev == "switch":
            print()

if __name__ == '__main__':
    pass