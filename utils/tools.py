from base import cli
from json import dumps
from re import split

from click.testing import Result
from mprettytable import PrettyTable
from utils.http_code import HTTP
from utils.http_helper import hp

INTF_MAP = dict((["X%d" % i, i] for i in range(1, 57)))
INTF_MAP.update(dict((["C%d" % (i-56), i] for i in range(57, 63))))
INTF_MAP_REST = dict(([INTF_MAP[k], k] for k in INTF_MAP))

INTF_CPU_MAP = dict((["IG%d" % i, i] for i in range(1, 65)))
INTF_CPU_MAP.update(dict((["G%d" % (i-64), i] for i in range(65, 86))))
INTF_CPU_MAP_REST = dict(([INTF_CPU_MAP[k], k] for k in INTF_CPU_MAP))

# General operation interface

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

def get_existed_acl():
    acl_ids = set()
    data = hp.cpu_get("acl/config/group_1")
    for d in data:
        if isinstance(d[2], dict) and "group_1" in d[2]:
                for idx in d[2]["group_1"]:
                    acl_ids.add(idx)
    return acl_ids


def gen_intfs_cpu(desc):
    restid = []

    def diss_a(child_str):
        intfs = child_str.split("-")
        if len(intfs) < 2 or intfs[0] not in INTF_CPU_MAP or intfs[-1] not in INTF_CPU_MAP:
            print("PORT INDEX ERROR")
            exit()
        for i in range(INTF_CPU_MAP[intfs[0]], INTF_CPU_MAP[intfs[-1]]+1):
            restid.append(INTF_CPU_MAP_REST[i])
    childs = desc.split(",")
    for c in childs:
        if "-" in c:
            diss_a(c)
        elif c in INTF_CPU_MAP:
            restid.append(c)
    return restid


def gen_intfs_sw(desc):
    restid = []

    def diss_a(child_str):
        intfs = child_str.split("-")
        if len(intfs) < 2 or intfs[0] not in INTF_MAP or intfs[-1] not in INTF_MAP:
            print("range error")
        for i in range(INTF_MAP[intfs[0]], INTF_MAP[intfs[-1]]+1):
            restid.append(INTF_MAP_REST[i])
    childs = desc.split(",")
    for c in childs:
        if "-" in c:
            diss_a(c)
        elif c in INTF_MAP:
            restid.append(c)
    return restid

def cut_line(rstr, step=60):
    lines = rstr.split('\n')
    row = len(lines)
    line_len = len(lines[0])
    clist = []

    s_pos = 0
    e_pos = 0
    while line_len > e_pos:
        e_pos = s_pos + step
        if line_len < e_pos:
            for line in lines:
                clist.append(line[s_pos:])
            break
        while lines[0][e_pos] != '+' and  lines[0][e_pos] != '|':
            e_pos -= 1
        for line in lines:
            clist.append(line[s_pos:e_pos]+line[0])
        s_pos = e_pos

    cstr = '\n'.join(clist)
    return cstr

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
                    row = [key]
                    for item in data:
                        if isinstance(item[2], dict):
                            if key in item[2]:
                                row.append(item[2][key])
                            else:
                                row.append(None)
                        else:
                            if '404' not in item[2]:
                                row.append(item[2])
                            else:
                                row.append("E(4)")
                    tb.add_row(row)
            break
    if len(tb._rows) == 0:
        row = ["status", *[HTTP.STATUS[item[0]][0] if item[0]
                           in HTTP.STATUS else item[0] for item in data]]
        tb.add_row(row)
    rstr = tb.get_string(sortby=tab, reversesort=True)
    return cut_line(rstr)


def gen_table_sw(data, expect, tab="item", filter=None):
    if not isinstance(data, list) or len(data) < 1:
        return
    tb = PrettyTable()
    tb.field_names = [tab, *expect[filter]]
    tb.align[tab] = "l"
    for portinfo in data:
        if isinstance(portinfo[2], dict):
            for port in portinfo[2]:
                if isinstance(portinfo[2][port],dict) and filter in portinfo[2][port]:
                    portstat = []
                    for stat in expect[filter]:
                        if isinstance(portinfo[2][port][filter], dict):
                            if stat in portinfo[2][port][filter]:
                                portstat.append(
                                    portinfo[2][port][filter][stat])
                            else:
                                portstat.append(None)
                        else:
                            portstat.append(portinfo[2][port][filter])
                    row = [port, *portstat]
                    tb.add_row(row)
                else:
                    pass
        else:
            row = [tab, *[item[2] for item in data]]
            if len(tb.field_names) == len(row):
                tb.add_row(row)
    rstr = tb.get_string(sortby=tab, reversesort=True)
    return cut_line(rstr)

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
    rstr = tb.get_string(reversesort=True)
    return cut_line(rstr)
