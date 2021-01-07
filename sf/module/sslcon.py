import click
from json import dumps
from base import cli
from utils.http_helper import hp
from utils.tools import  * 
from utils.static_data import *


'''
    This module instructions:
        It's just an interim process at the moment
'''

def sslcon_stat_operation(ctx, args, incomplete):
    colors = [('show',  'show stat detail'),
              ('clean', 'clean stat all')]
    return [c for c in colors if incomplete in c[0]]

def sslcon_stat_filter(ctx, args, incomplete):
    if args[-1] == "clean":
        comp = [('all', 'clean all stat'),
                ('global_stat', 'clean global stat'),
                ('server_info', 'clean server_info detail stat')]
    elif args[-1]== "show":
        comp = [('all', 'all stat'),
                ('global_stat', 'clean global stat'),
                ('server_info', 'clean server_info detail stat')]
    return [c for c in comp if incomplete in c[0]]

@cli.command()
@click.argument("op", type=click.STRING, autocompletion=sslcon_stat_operation)
@click.argument("filter", type=click.STRING, autocompletion=sslcon_stat_filter, required=False)
def sslcon_stat(op, filter):
    if op == 'show':
        if filter == "all":
            data = hp.cpu_get('ssl_concatenation/stat')
        elif filter == "global_stat":
            data = hp.cpu_get('ssl_concatenation/stat/global_stat')
        elif filter == "server_info":
            data = hp.cpu_get('ssl_concatenation/stat/server_info')
        data = [[d[0],d[1],d[2]] for d in data]
        click.echo_via_pager(gen_table(data, tab="count", filter=None))
    elif op == 'clean':
        clean_data = []
        if filter == "all":
            clean_data.append({"op": "remove", "path": "/stat", "value": ""})
            clean_data.append({"op": "remove", "path": "/server_info", "value": ""})
        elif filter == "global_stat":
            clean_data.append({"op": "remove", "path": "/stat", "value": ""})
        elif filter == "server_info":
            clean_data.append({"op": "remove", "path": "/server_info", "value": ""})
        data = hp.cpu_patch('ssl_concatenation/stat', clean_data)
        field_names = ["code",  "ipaddr", "body"]
        click.echo(create_custiom_table(data,field_names))
