from json import dumps
from prettytable import PrettyTable
from utils.http_code import STATUS

INTF_MAP = dict((["X%d"%i, i] for i in range(1, 73)))
temp = dict((["C%d"% (i-72), i] for i in range(73, 79)))
for key in temp:
    INTF_MAP[key]= temp[key]
INTF_MAP_REST = dict(([INTF_MAP[k], k] for k in INTF_MAP))

INTF_CPU_MAP = dict((["IG%d"%i, i] for i in range(1, 65)))
INTF_CPU_MAP_REST = dict(([INTF_CPU_MAP[k], k] for k in INTF_CPU_MAP))

def gen_table(data, tab="item",filter=None):
    if not isinstance(data, list) or len(data)<1:
        return
    tb = PrettyTable()
    tb.field_names = [tab,*[item[1] for item in data]]
    tb.align[tab] = "l"
    if isinstance(data[0][2], dict):
        for key in sorted(data[0][2]):
            if (filter and filter in key) or not filter:
                row = [key, *[ dumps(item[2][key]) for item in data]]
                tb.add_row(row)
                tb.get_string(sortby=tab, reversesort=True)
    else:
        # row = ["code", *[ STATUS[item[2]][0] for item in data] ]
        row = [tab, *[ item[2] for item in data] ]
        tb.add_row(row)
    return tb

def gen_table_intf(data, tab="item",filter=None):
    expect = [
        "rx_mbps",
        "rx_kpps",
        "rx_packets",
        "rx_bytes",
        "tx_mbps",
        "tx_kpps",
        "tx_packets",
        "tx_bytes"
    ]
    if not isinstance(data, list) or len(data)<1:
        return
    tb = PrettyTable()
    try:
        ports = [(list(item[2].keys())[0]) for item in data if item[2]]
    except Exception as e:
        return "\n!!!{} data is none !!!\n".format(tab)
    tb.field_names = [tab, *expect]
    tb.align[tab] = "l"
    for portinfo in data:
        if isinstance(portinfo[2], dict):
            for port in portinfo[2]:
                if filter in portinfo[2][port]:
                    portstat = [portinfo[2][port][filter][stat] for stat in expect]
                    row = [port,*portstat]
                    tb.add_row(row)
                else:
                    pass
        else:
            row = [tab, *[ item[2] for item in data] ]
            tb.add_row(row)
    tb.get_string(sortby=tab)
    return tb


def gen_table_intf_cpu(data, tab="item",filter=None):
    if not isinstance(data, list) or len(data)<1:
        return
    tb = PrettyTable()
    try:
        ports = [(list(item[2].keys())[0]) for item in data if item[2]]
    except Exception as e:
        return "\n!!!{} data is none !!!\n".format(tab)
    tb.field_names = ["port", tab]
    tb.align[tab] = "l"
    for portinfo in data:
        if isinstance(portinfo[2], dict):
            for port in portinfo[2]:
                if filter in portinfo[2][port]:
                    row = [port, portinfo[2][port][filter]]
                    tb.add_row(row)
                else:
                    pass
        else:
            row = [tab, *[ item[2] for item in data] ]
            tb.add_row(row)
    tb.get_string(sortby=tab)
    return tb