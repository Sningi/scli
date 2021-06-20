import click
from json import dumps

from base import cli
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *

def dpdk_stat_operation(ctx, args, incomplete):
    comp = [('show', 'show stat'),
            ('clean', 'clean stat')]
    return [c for c in comp if c[0].startswith(incomplete)]


@cli.command()
@click.argument("op", type=click.STRING, autocompletion=dpdk_stat_operation)
def dpdk_stat(op):
    if op == 'show':
        data = hp.cpu_get('vpp/dpdk')
        print(data)
    elif op == 'clean':
        pd = [ {'op': 'replace', 'path': "/" , "value": ""}]
        data = hp.cpu_patch('vpp/dpdk', pd)
        print(gen_table(data, tab="code"))


sf_dpdk_finish = ''
