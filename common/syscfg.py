from click import argument,option,Choice
from common.base import cli,sprint
from utils.http_helper import hp
from utils.tools import *

sync_data = [{"op": "replace", "path": "/", "value": 1}]

@cli.command()  # @cli, not @click!
@argument("op", type=Choice(['save', 'reset','download','upload']))
@argument("dev", type=Choice(['cpu', 'sw','all']))
def syscfg(op, dev):
    # '''
    # CPU PATCH https://192.168.1.200:2020/rest/v1/system/config
    # {"op": "replace", "path": "/", "value":1}
    # '''
    if 'save'.startswith(op):
        if "cpu".startswith(dev) or "all".startswith(dev):
            data = hp.cpu_patch("system/config/sync", sync_data)
            sprint(gen_table(data, tab="cpu"))
        if "sw".startswith(dev) or "all".startswith(dev):
            # data = hp.sw_patch("system/config", sync_data)
            # sprint(gen_table(data, tab="switch"))
            pass

    elif "reset".startswith(op):
        if "cpu".startswith(dev) or "all".startswith(dev):
            data = hp.cpu_patch("system/config", sync_data)
            sprint(gen_table(data, tab="cpu"))
        if "sw".startswith(dev) or "all".startswith(dev):
            data = hp.sw_delete("forward_policies")
            sprint(gen_table(data,tab="switch"))
            data = hp.sw_delete("elags/128")
    elif "download".startswith(op):
        if "cpu".startswith(dev) or "all".startswith(dev):
            data = hp.cpu_get_file("system/config",filename='config')
            sprint(gen_table(data, tab='cpu'))
    elif "upload".startswith(op):
        if "cpu".startswith(dev) or "all".startswith(dev):
            data = hp.cpu_upload_file("system/config",filename='config')
            sprint(gen_table(data, tab='cpu'))

@cli.command()
@argument("dev", type=Choice(['cpu', 'sw','all']),default='cpu',required=False)
@option('--filter','-f', type=Choice(['sf_version', 'release_version','platform','host_name','all']), default='sf_version', required=False)
def version(dev, filter):
    def cpu_ver():
        data = hp.cpu_get("system/info")
        if filter == 'all':
            sprint(gen_table(data, tab="cpu",filter=None))
        else:
            sprint(gen_table(data, tab="cpu",filter=filter))

    def sw_ver():
        data = hp.sw_get("system")
        sprint(gen_table(data, tab="switch",filter='status'))
    if "cpu".startswith(dev):
        cpu_ver()
    elif "sw".startswith(dev):
        sw_ver()
    elif "all".startswith(dev):
        cpu_ver()
        sw_ver()

sf_sys_finish = ''
