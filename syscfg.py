import click

from base import cli
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import *

sync_data = [{"op": "replace", "path": "/", "value": 1}]


def sys_op(ctx, args, incomplete):
    op = [
        ('save', 'save config'),
        ('reset', 'reset config'),
        ('download', 'download config'),
        ('upload', 'upload config'),
    ]
    return [c for c in op if c[0].startswith(incomplete)]


def sys_dev(ctx, args, incomplete):
    dev = [('cpu', 'cpu'),
           ('sw', 'switch'),
           ('all', 'all'),
           ]
    return [i for i in dev if incomplete in i[0]]


@cli.command()  # @cli, not @click!
@click.argument("op", type=click.STRING, autocompletion=sys_op)
@click.argument("dev", type=click.STRING, autocompletion=sys_dev)
def syscfg(op, dev):
    '''
    CPU PATCH https://192.168.1.200:2020/rest/v1/system/config
    {"op": "replace", "path": "/", "value":1}
    '''
    if 'save'.startswith(op):
        pass
    elif "reset".startswith(op):
        if "cpu".startswith(dev):
            data = hp.cpu_patch("system/config", sync_data)
            print(gen_table(data, tab="cpu"))
        elif "sw".startswith(dev):
            data = hp.sw_delete("forward_policies")
            print(gen_table(data,tab="switch"))
            data = hp.sw_delete("elags/128")
        elif "all".startswith(dev):
            data = hp.cpu_patch("system/config", sync_data)
            print(gen_table(data, tab="cpu"))
            data = hp.sw_delete("forward_policies")
            print(gen_table(data,tab="switch"))
            data = hp.sw_delete("elags/128")
    elif "download".startswith(op):
        pass
    elif "upload".startswith(op):
        pass


sf_sys_finish = ''
