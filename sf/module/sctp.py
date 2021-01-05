import click

from base import cli, clean_data
from utils.http_helper import hp
from utils.tools import gen_table

def sctp_operation(ctx, args, incomplete):
    colors = [('show', 'show config'),
              ('set', 'set config')]
    return [c for c in colors if incomplete in c[0]]

def config_field(ctx, args, incomplete):
    colors = [('ngap_decode', 'switch of ngap decode'),
              ('set', 'set config')]
    return [c for c in colors if incomplete in c[0]]

def config_value(ctx, args, incomplete):
    colors = [('enable', 'enable feature'),
              ('disable', 'set config')]
    return [c for c in colors if c[0].startswith(incomplete)]

@cli.command()# @cli, not @click!
@click.argument("op", type=click.STRING, autocompletion=sctp_operation)
@click.argument("field", type=click.STRING, autocompletion=config_field, required=False)
@click.argument("value", type=click.STRING, autocompletion=config_value, required=False)
def sctp_config(op, field=None, value =None):
    if op == 'show':
        data = hp.cpu_get('sctp/config')
        print(gen_table(data,))
    # elif op == 'clean':
    #     data = hp.cpu_patch('sctp/stat', clean_data)
    #     print(gen_table(data, tab="code"))

def sctp_stat_operation(ctx, args, incomplete):
    colors = [('show', 'show stat'),
              ('clean', 'clean stat')]
    return [c for c in colors if incomplete in c[0]]


def sctp_stat_filter(ctx, args, incomplete):
    colors = [('chunk', 'chunk stat'),
              ('error', 'error stat'),
              ('total', 'total stat')]
    return [c for c in colors if incomplete in c[0]]


@cli.command()
@click.argument("op", type=click.STRING, autocompletion=sctp_stat_operation)
@click.argument("filter", type=click.STRING, autocompletion=sctp_stat_filter, required=False)
def sctp_stat(op, filter):
    if op == 'show':
        print("get data ing...")
        data = hp.cpu_get('sctp/stat')
        print(gen_table(data, tab="count", filter=filter))
    elif op == 'clean':
        data = hp.cpu_patch('sctp/stat', clean_data)
        print(gen_table(data, tab="code"))