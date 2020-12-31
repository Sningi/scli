from prettytable import PrettyTable
from utils.http_code import STATUS
def gen_table(data, tab="item",filter=None):
    if not isinstance(data, list) or len(data)<1:
        return
    tb = PrettyTable()
    tb.field_names = [tab,*[item[1] for item in data]]
    tb.align[tab] = "l"
    if isinstance(data[0][2], dict):
        for key in data[0][2]:
            if filter and filter in key or not filter:
                row = [key, *[ item[2][key] for item in data]]
                tb.add_row(row)
                tb.get_string(sortby=tab, reversesort=True)
    else:
        # row = ["code", *[ STATUS[item[2]][0] for item in data] ]
        row = [tab, *[ item[2] for item in data] ]
        tb.add_row(row)
    return tb