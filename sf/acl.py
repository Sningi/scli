from click import argument,option,STRING,Choice

from common.base import cli, sprint,get_args
from sf.general_rest_api import general_clean_data
from utils.http_helper import hp
from utils.tools import *

sync_data = [{"op": "replace", "path": "/", "value": 1}]


def acl_types(ctx, args, incomplete):
    args = get_args(args)
    field = []
    if "create" in args:
        field = [('imsi', 'imsi'),
                 ('imei', 'imei'),
                 ('msisdn', 'msisdn'),
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
    elif "show" in args:
        field = [("stat", "acl hit count"), ("cfg", "acl cfg")
                 ]
    elif "clean" in args:
        field = [("stat", "acl hit count"),
                 ]
    return [i for i in field if incomplete in i[0]]


def acl_idx(ctx, args, incomplete):
    idxs = get_existed_acl()
    if "show" in args or "delete" in args or "clean" in args:
        return [(idx, '') for idx in idxs if idx.startswith(incomplete)]
    elif "create" in args:
        return [(str(idx), '') for idx in range(1, 101) if str(idx) not in idxs and str(idx).startswith(incomplete)]
    else:
        return []


packet_types = (
    'error', 'vlan', 'mpls', 'gre', 'vxlan', 'ssl_tls',
    'ipip', 'ipip6', 'ip6ip', 'ip6ip6', 'teredo', 'ipsec_ah', 'ipsec_esp',
    'gtpu', 'gtpv0', 'gtpv1', 'gtpv2', 'http', 'http2', 'sip', 'rtp',
    'rtcp', 'diameter', 'sgs_ap', 's1ap', 'ngap', 'ftp', 'pop3', 'smtp', 'dns',
    'radius', 'coap', 'pptp', 'l2tp', 'https', 'icmp', 'bgp', 'ospf', 'isis', 'gtp', 'sctp',
    'gtpv2_cdr','n2_cdr','gtpu_bear',
)


def acl_values(ctx, args, incomplete):
    args = get_args(args)
    field = []
    if "create" in args:
        if "packet_type" in args:
            return [(ptype, ptype) for ptype in packet_types if ptype.startswith(incomplete)]
    return [i for i in field if incomplete in i[0]]


@cli.command()  # @cli, not @click!
@argument("op", type=Choice(['show','create','delete','clean','sync']),default='show')
@argument("idx", type=STRING, autocompletion=acl_idx, required=False)
@argument("atype", type=STRING, autocompletion=acl_types, default="cfg", required=False)
@argument("value", type=STRING, autocompletion=acl_values,  required=False)
@option('--sip','-s', type=STRING, default=None, required=False)
@option('--dip','-d', type=STRING, default=None, required=False)
def acl(op, idx, atype, value, sip, dip):
    if 'show'.startswith(op):
        if "stat".startswith(atype):
            data2 = hp.cpu_get('acl/stat?group=1&index={0}'.format(idx))
        else:
            data2 = hp.cpu_get('acl/config/group_1/{}'.format(idx))
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
        elif "imei".startswith(atype):
            postd = {
                "group_1": {
                    idx: {
                        "rule_type": atype,
                        "rule_cfg": {
                            "imei": value,
                        },
                    },
                }
            }
        elif "msisdn".startswith(atype):
            postd = {
                "group_1": {
                    idx: {
                        "rule_type": atype,
                        "rule_cfg": {
                            "msisdn": value,
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
        elif "tuple4" == atype:
            rule_var = {
                "dip": "0.0.0.0",
                "dip_mask": 0,
                "dport_max": 65535,
                "dport_min": 0,
                "proto_max": 255,
                "proto_min": 0,
                "sip": "0.0.0.0",
                "sip_mask": 32,
                "sport_max": 65535,
                "sport_min": 0,
                "vlan_max": 4095,
                "vlan_min": 0
            }
            if sip:
                rule_var['sip'] = sip
            if dip:
                rule_var['dip'] = dip
            postd = {
                "group_1": {
                    idx: {
                        "rule_type": atype,
                        "rule_cfg": rule_var,
                    },
                }
            }
        data2 = hp.cpu_post('acl/config/group_1/{}'.format(idx), postd)
    elif "delete".startswith(op):
        data2 = hp.cpu_delete('acl/config?group=1&index={}'.format(idx))
        sprint(gen_table(data2))
    elif "sync".startswith(op):
        data2 = hp.cpu_patch('acl/sync', sync_data)
    elif "clean".startswith(op):
        data2 = hp.cpu_patch('acl/stat?group=1&index={0}'.format(idx), general_clean_data)
    else:
        return
    sprint(gen_table(data2))

sf_acl_finish = ''
