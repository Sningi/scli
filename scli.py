import json
from click import argument,option, STRING, Choice
from itertools import zip_longest

from common.base import cli,sprint
from common.config import Config
from utils.http_helper import hp
from utils.tools import *

from common.syscfg import sf_sys_finish
# sf
from sf.acl import sf_acl_finish
from sf.action import sf_action_finish
from sf.interface import sf_intf_finish

# switch
from sw.interface import sw_intf_finish
from sw.acl import sw_acl_finish


# module
from sf.module.sctp import sf_sctp_finish
from sf.module.http2 import sf_http2_finish
from sf.module.gtpu import sf_gtpu_finish
from sf.module.gtpv2 import sf_gtpv2_finish
from sf.module.gtpv1 import sf_gtpv1_finish
from sf.module.sig import sf_sig_finish
from sf.module.dpdk import sf_dpdk_finish


def dev_op(ctx, args, incomplete):
    comp = [('show', 'show stat')]
    return [c for c in comp if c[0].startswith(incomplete)]

def dev_type(ctx, args, incomplete):
    comp = [('cpu', 'cpu ip'),
            ('switch', 'switch ip'),
            ('all', 'all ip')]
    return [c for c in comp if c[0].startswith(incomplete)]


@cli.command()
@argument("op", type=STRING, autocompletion=dev_op)
@option('--dev','-d', type=Choice(['cpu', 'switch','all']), default="all", required=False)
def dev_ip(op, dev='all'):
    data = []
    if op == "show":
        if dev == "all":
            field_names = ["index", "SWITCH", "CPU"]
            for index, group in enumerate(zip_longest(Config.sw_addrs,Config.cpu_addrs)):
                data.append([index + 1, group[0], group[1]])
            tb = create_custiom_table(data, field_names)
            sprint(tb)
        elif dev == "cpu":
            field_names = ["index",  "CPU"]
            for index, group in enumerate(Config.cpu_addrs):
                data.append([index + 1, group])
            tb = create_custiom_table(data, field_names)
            sprint(tb)
        elif dev == "switch":
            field_names = ["index",  "SWITCH"]
            for index, group in enumerate(Config.sw_addrs):
                data.append([index + 1, group])
            tb = create_custiom_table(data, field_names)
            sprint(tb)


@cli.command()
@argument("dev",  type=Choice(['cpu', 'switch']))
@argument("url", type=STRING)
@option('--format','-f', type=Choice(['json', 'table']), default="json", required=False)
def get(dev, url, format):
    if 'cpu'.startswith(dev):
        data = hp.cpu_get(url)
    elif "switch".startswith(dev):
        data = hp.sw_get(url)
    else:
        return
    try:
        if format == 'table':
            sprint(gen_table(data))
        elif format == 'json':
            sprint(json.dumps(data,indent=2))
        else:
            sprint(data)
    except:
        sprint(data)


@cli.command()
@argument("dev",  type=Choice(['cpu', 'switch']))
@argument("url", type=STRING)
@argument("file", type=STRING)
@option('--format','-f', type=Choice(['json', 'table']), default="json", required=False)
def patch(dev, url, file, format):
    import os
    if not os.path.exists(file):
        sprint("File Not Exists: {0}".format(file))
        return
    with open(file,'r') as f:
        pd = json.load(f)
    if 'cpu'.startswith(dev):
        data = hp.cpu_patch(url,data=pd)
    elif "switch".startswith(dev):
        data = hp.sw_patch(url,data=pd)
    else:
        return
    try:
        if format == 'table':
            sprint(gen_table(data))
        elif format == 'json':
            sprint(json.dumps(data,indent=2))
        else:
            sprint(data)
    except:
        sprint(data)


@cli.command()
@argument("dev", type=Choice(['cpu', 'switch']))
@argument("url", type=STRING)
@argument("file", type=STRING)
@option('--format','-f', type=Choice(['json', 'table']), default="json", required=False)
def post(dev, url,file, format):
    import os
    if not os.path.exists(file):
        sprint("File Not Exists: {0}".format(file))
        return
    with open(file,'r') as f:
        pd = json.load(f)
    if 'cpu'.startswith(dev):
        data = hp.cpu_post(url, data=pd)
    elif "switch".startswith(dev):
        data = hp.sw_post(url, data=pd)
    else:
        return
    try:
        if format == 'table':
            sprint(gen_table(data))
        elif format == 'json':
            sprint(json.dumps(data,indent=2))
        else:
            sprint(data)
    except:
        sprint(data)


@cli.command()
@argument("dev", type=Choice(['cpu', 'switch']))
@argument("url", type=STRING)
@option('--format','-f', type=Choice(['json', 'table']), default="json", required=False)
def delete(dev, url, format):
    if 'cpu'.startswith(dev):
        data = hp.cpu_delete(url)
    elif "switch".startswith(dev):
        data = hp.sw_delete(url)
    else:
        return
    try:
        if format == 'table':
            sprint(gen_table(data))
        elif format == 'json':
            sprint(json.dumps(data,indent=2))
        else:
            sprint(data)
    except:
        sprint(data)

if __name__ == '__main__':
    cli()
