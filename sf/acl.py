import click

from base import cli
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import *

sync_data = [{"op": "replace", "path": "/", "value": 1}]


def acl_operation(ctx, args, incomplete):
    op = [('show', 'show acl'),
          ('create', 'create acl'),
          ('delete', 'delete acl'),
          ('sync', 'sync acl'),
          ]
    return [c for c in op if c[0].startswith(incomplete)]


def acl_types(ctx, args, incomplete):
    field = []
    if "create".startswith(args[-2]):
        field = [('imsi', 'imsi'),
                 ('ipset4', 'ipset4'),
                 ('ipset6', 'ipset6'),
                 ('tuple4', 'tuple4'),
                 ('tuple6', 'tuple6'),
                 ('packet_type', 'packet_type'),
                 ('packet_len', 'packet_len'),
                 ('l2', 'l2'),
                 ('url', 'url'),
                 ('regex', 'regex'),
                 ('tcpflag', 'tcpflag'),
                 ('combined', 'combined'),
                 ]
    elif "show".startswith(args[-2]):
        field = [("stat", "acl hit count"),("cfg", "acl cfg")
                 ]
    return [i for i in field if incomplete in i[0]]


def acl_idx(ctx, args, incomplete):
    idxs = get_existed_acl()
    if "show".startswith(args[-1]) or "delete".startswith(args[-1]):
        return [(idx, '') for idx in idxs if idx.startswith(incomplete)]
    elif "create".startswith(args[-1]):
        return [(str(idx), '') for idx in range(1, 101) if str(idx) not in idxs and str(idx).startswith(incomplete)]
    else:
        return []


packet_types = (
    'error', 'vlan', 'mpls', 'gre', 'vxlan', 'ssl_tls',
    'ipip', 'ipip6', 'ip6ip', 'ip6ip6', 'teredo', 'ipsec_ah', 'ipsec_esp',
    'gtpu', 'gtpv0', 'gtpv1', 'gtpv2', 'http', 'http2', 'sip', 'rtp',
    'rtcp', 'diameter', 'sgs_ap', 's1ap', 'ngap', 'ftp', 'pop3', 'smtp', 'dns',
    'radius', 'coap', 'pptp', 'l2tp', 'https', 'icmp', 'bgp', 'ospf', 'isis', 'gtp', 'sctp',
    'gtpv2_cdr',
)


def acl_values(ctx, args, incomplete):
    field = []
    if "create".startswith(args[-3]):
        if "packet_type".startswith(args[-1]):
            return [(ptype, ptype) for ptype in packet_types if ptype.startswith(incomplete)]
    return [i for i in field if incomplete in i[0]]


@cli.command()  # @cli, not @click!
@click.argument("op", type=click.STRING, autocompletion=acl_operation)
@click.argument("idx", type=click.STRING, autocompletion=acl_idx, required=False)
@click.argument("atype", type=click.STRING, autocompletion=acl_types, default="cfg", required=False)
@click.argument("value", type=click.STRING, autocompletion=acl_values,  required=False)
def acl(op, idx, atype, value):
    if 'show'.startswith(op):
        if "stat".startswith(atype):
            data = hp.cpu_get('acl/stat?group=1&index={0}'.format(idx))
        else:
            data = hp.cpu_get('acl/config/group_1/{}'.format(idx))
        print(gen_table(data,))
    elif "create".startswith(op):
        postd = []
        if "imsi".startswith(atype):
            postd = {
                "group_1": {
                    idx: {
                        "rule_type": atype,
                        "rule_cfg": {
                            "imsi": value,
                        },
                    },
                }
            }
        elif "packet_type".startswith(atype):
            postd = {
                "group_1": {
                    idx: {
                        "rule_type": atype,
                        "rule_cfg": {
                            "packet_type": value,
                        },
                    },
                }
            }
        data = hp.cpu_post('acl/config/group_1/{}'.format(idx), postd)
        print(gen_table(data))
    elif "delete".startswith(op):
        data = hp.cpu_delete('acl/config?group=1&index={}'.format(idx))
        print("del", gen_table(data))
    elif "sync".startswith(op):
        data2 = hp.cpu_patch('acl/sync', sync_data)
        print(gen_table(data2))


sf_acl_finish = ''
