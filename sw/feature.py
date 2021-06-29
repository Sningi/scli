from click import argument, Choice
from common.base import cli, sprint
from utils.http_helper import hp
from utils.tools import gen_table, gen_table_sw

expect={
    'errpkt_permit':[
        'link-layer',
        'ether-layer'
    ]
}

@cli.command()
@argument("op", type=Choice(['show','enable','disable']),default='show')
@argument("field", type=Choice(['link-layer','ether-layer','all']),default='all')
def errpkt_permit(op, field):
    if 'show'.startswith(op):
        data = hp.sw_get('system')
        tb = gen_table_sw(data,expect=expect,tab='switch',filter='errpkt_permit')
        sprint(tb)
    elif op in('enable','disable'):
        if op == 'enable':
            cfg = 'true'
        else:
            cfg = 'false'
        pd = []
        if field in ('link-layer','all'):
            pd.append({"op":"add", "path": "/configuration/errpkt_permit/link-layer", "value": cfg})
        if field in ("ether-layer","all"):
            pd.append({"op":"add", "path": "/configuration/errpkt_permit/ether-layer", "value": cfg})
        data = hp.sw_patch("system", pd)
        sprint(gen_table(data, tab="switch"))

sw_feature_finish = ''
