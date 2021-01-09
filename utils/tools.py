from json import dumps
from prettytable import PrettyTable
from utils.http_code import HTTP
from utils.http_helper import hp

INTF_MAP = dict((["X%d" % i, i] for i in range(1, 57)))
INTF_MAP.update(dict((["C%d" % (i-56), i] for i in range(57, 63))))
INTF_MAP_REST = dict(([INTF_MAP[k], k] for k in INTF_MAP))

INTF_CPU_MAP = dict((["IG%d" % i, i] for i in range(1, 65)))
INTF_CPU_MAP.update(dict((["G%d" % (i-64), i] for i in range(65, 86))))
INTF_CPU_MAP_REST = dict(([INTF_CPU_MAP[k], k] for k in INTF_CPU_MAP))

# General operation interface


def create_custiom_table(data, field_names, filter=None, padding_width=1):
    if not isinstance(field_names, list) or len(field_names) < 1:
        return
    if not isinstance(data, list) or len(data) < 1:
        return
    tb = PrettyTable()
    tb.field_names = field_names
    tb.align[field_names[0]] = "l"
    tb.padding_width = padding_width
    for body in data:
        if not isinstance(body, list) or len(body) < 1:
            print("You need to use list")
            continue
        tb.add_row(body)
    return tb


'''
[value1, value2, value3 .... , valueX]
'''


def table_add_row(tb, data):
    if not isinstance(data, list) or len(data) < 1:
        print("You need to use list")
        return
    tb.add_row(data)


'''
[tab, value1, value2, value3 .... , valueX]
'''


def table_add_colum(tb, data):
    if not isinstance(data, list) or len(data) < 1:
        print("You need to use list")
        return
    tb.add_colum(data)

# Common Generator Functions


def get_intfs_from_rest():
    intfs = []
    data = hp.cpu_get("interfaces/config")
    for d in data:
        if isinstance(d[2], dict):
            for item in d[2]:
                intfs.append(item)
    return intfs


def get_existed_action():
    idxs = []
    data = hp.cpu_get("actions")
    for d in data:
        if isinstance(d[2], dict):
            for item in d[2]:
                idxs.append(item)
    return idxs


def gen_intfs_cpu(desc):
    restid = []
    if "-" in desc:
        intfs = desc.split("-")
        if len(intfs) < 2 or intfs[0] not in INTF_CPU_MAP or intfs[-1] not in INTF_CPU_MAP:
            print("PORT INDEX ERROR")
            exit()
        for i in range(INTF_CPU_MAP[intfs[0]], INTF_CPU_MAP[intfs[-1]]+1):
            restid.append(INTF_CPU_MAP_REST[i])
    elif ',' in desc:
        intfs = desc.split(",")
        for i in intfs:
            if i in INTF_CPU_MAP:
                restid.append(i)
    elif desc in INTF_CPU_MAP:
        restid.append(desc)
    return restid


def gen_intfs_sw(desc):
    restid = []
    if "-" in desc:
        intfs = desc.split("-")
        if len(intfs) < 2 or intfs[0] not in INTF_MAP or intfs[-1] not in INTF_MAP:
            print("PORT INDEX ERROR")
            exit()
        for i in range(INTF_MAP[intfs[0]], INTF_MAP[intfs[-1]]+1):
            restid.append(INTF_MAP_REST[i])
    elif ',' in desc:
        intfs = desc.split(",")
        for i in intfs:
            if i in INTF_MAP:
                restid.append(i)
    elif desc in INTF_MAP:
        restid.append(desc)
    return restid


def gen_table(data, tab="item", filter=None):
    if not isinstance(data, list) or len(data) < 1:
        return
    for d in data:
        if not isinstance(d, list) or len(d) != 3:
            return
    tb = PrettyTable()
    tb.field_names = [tab, *[item[1] for item in data]]
    tb.align[tab] = "l"
    # if isinstance(data[0][2], dict):
    for one in data:
        if isinstance(one[2], dict):
            for key in sorted(one[2]):
                if (filter and filter in key) or not filter:
                    row = [
                        key, *[item[2][key] if isinstance(item[2], dict) else item[2] for item in data]]
                    # if(len(row)==len(tb.field_names)):
                    tb.add_row(row)
            break
    if len(tb._rows) == 0:
        row = ["status", *[HTTP.STATUS[item[0]][0] if item[0]
                           in HTTP.STATUS else item[0] for item in data]]
        tb.add_row(row)
    tb.get_string(sortby=tab, reversesort=True)
    return tb


def gen_table_intf(data, tab="item", filter=None):
    expect = {
        "statistics": [
            "rx_mbps",
            "rx_kpps",
            "rx_packets",
            "rx_bytes",
            # "rx_dropped",
            "tx_mbps",
            "tx_kpps",
            "tx_packets",
            "tx_bytes",
            # "tx_dropped"
        ],
        "status": [
            "connector",
            "link_state",
            "support_speeds"
        ],
        "configuration": [
            "speed",
            "mtu",
            "enable",
            "transceiver_mode",
        ]

    }
    if not isinstance(data, list) or len(data) < 1:
        return
    tb = PrettyTable()
    tb.field_names = [tab, *expect[filter]]
    tb.align[tab] = "l"
    for portinfo in data:
        if isinstance(portinfo[2], dict):
            for port in portinfo[2]:
                if filter in portinfo[2][port]:
                    portstat = [portinfo[2][port][filter][stat] if stat in portinfo[2]
                                [port][filter] else None for stat in expect[filter]]
                    row = [port, *portstat]
                    tb.add_row(row)
                else:
                    pass
        else:
            row = [tab, *[item[2] for item in data]]
            tb.add_row(row)
    tb.get_string(sortby=tab)
    return tb


def gen_table_intf_cpu(data, tab="item", filter=None):
    if not isinstance(data, list) or len(data) < 1:
        return
    tb = PrettyTable()
    tb.field_names = ["port", tab]
    tb.align[tab] = "l"
    for portinfo in data:
        if isinstance(portinfo[2], dict):
            for port in portinfo[2]:
                if filter in portinfo[2][port]:
                    # row = [port,  ",".join(portinfo[2][port][filter])]
                    row = [port,  portinfo[2][port][filter]]
                    tb.add_row(row)
                else:
                    pass
        else:
            row = [tab, *[item[2] for item in data]]
            tb.add_row(row)
    tb.get_string(sortby=tab)
    return tb
