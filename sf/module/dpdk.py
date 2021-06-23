from click import argument, Choice
from json import dumps

from common.base import cli, sprint
from utils.http_helper import hp
from utils.tools import gen_table
from utils.static_data import *

@cli.command()
@argument("op", type=Choice(['show','clean']),default='show')
def dpdk_stat(op):
    if op == 'show':
        data = hp.cpu_get('vpp/dpdk')
        sprint(dumps(data,indent=2))
    elif op == 'clean':
        pd = [ {'op': 'replace', 'path': "/" , "value": ""}]
        data = hp.cpu_patch('vpp/dpdk', pd)
        sprint(gen_table(data, tab="code"))


sf_dpdk_finish = ''
