import click
from json import dumps
from base import cli, sprint
from utils.http_helper import hp
from utils.tools import *
from utils.static_data import *
from utils.net_tools import *

from copy import deepcopy

SSLCON_OPENFLOW_INSTANCE_NAME = "br0"
SSLCON_BASE_VLAN = "4094"


SSLCON_MAP_PORT_VLAN = ["4038", "4039",
                        "4040", "4041", "4042", "4043", "4044", "4045", "4046", "4047", "4048", "4049",
                        "4050", "4051", "4052", "4053", "4054", "4055", "4056", "4057", "4058", "4059",
                        "4060", "4061", "4062", "4063", "4064", "4065", "4066", "4067", "4068", "4069",
                        "4070", "4071", "4072", "4073", "4074", "4075", "4076", "4077", "4078", "4079",
                        "4080", "4081", "4082", "4083", "4084"]


def sslcon_sw_base_op(ctx, args, incomplete):
    op = [('show',  'show switch sslcon base config'),
          ('create',   'create switch sslcon base config'),
          ('remove',   'remove switch sslcon base config')]
    return [c for c in op if incomplete in c[0]]


def sslcon_sw_base_configuration_show():
    data = hp.sw_get('openflowconf?type=flow')
    field_names = ["flows"]
    for i in data:
        sprint("Code : {0}   Ipaddr : {1}".format(i[0], i[1]))
        tb = PrettyTable()
        tb.field_names = field_names
        tb.align[field_names[0]] = "l"
        tb.padding_width = 1
        for ab in i[2]:
            tb.add_row([ab.strip()])
        sprint(str(tb))


def sslcon_sw_base_configuration_remove():
    pass


def sslcon_sw_base_configuration_create():
    field_names = ["code",  "ipaddr", "body"]
    field_intf_names = ["code",  "ipaddr", "body", "intf"]
    # create openflow instance
    of_instance_data = {
        SSLCON_OPENFLOW_INSTANCE_NAME: {
            "status": {
                "vlans": [
                    # map port vlan
                    "VLAN4038", "VLAN4039", "VLAN4040", "VLAN4041", "VLAN4042",
                    "VLAN4043", "VLAN4044", "VLAN4045", "VLAN4046", "VLAN4047",
                    "VLAN4048", "VLAN4049", "VLAN4050", "VLAN4051", "VLAN4052",
                    "VLAN4053", "VLAN4054", "VLAN4055", "VLAN4056", "VLAN4057",
                    "VLAN4058", "VLAN4059", "VLAN4060", "VLAN4061", "VLAN4062",
                    "VLAN4063", "VLAN4064", "VLAN4065", "VLAN4066", "VLAN4067",
                    "VLAN4068", "VLAN4069", "VLAN4070", "VLAN4071", "VLAN4072",
                    "VLAN4073", "VLAN4074", "VLAN4075", "VLAN4076", "VLAN4077",
                    "VLAN4078", "VLAN4079", "VLAN4080", "VLAN4081", "VLAN4082",
                    "VLAN4083", "VLAN4084",
                    # sslcon vlan
                    "VLAN4094"
                ],
                "ports": [
                    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20",
                    "21", "22", "23", "24", "25", "26", "27", "28", "29", "30",
                    "31", "32", "33", "34", "35", "36", "37", "38", "39", "40",
                    "41", "42", "43", "44", "45", "46", "47", "48", "49",
                    "50", "51", "52", "54"
                ]
            },
            "configuration": {
                "name": SSLCON_OPENFLOW_INSTANCE_NAME,
                "fail_mode": "secure",
                "table_miss": "default",
                "/1/match_field/ipv4": "in_port,dl_dst,dl_src",
                "/1/match_field/ipv6": "ipv6_dst",
                "/0/fuzzy_matching/ipv6": "dl_type,in_port,nw_proto,ipv6_dst,tp_dst,tp_src,dl_vlan,mpls_label,ipv6_src",
                "/1/fuzzy_matching/ipv6": "dl_type,in_port,nw_proto,ipv6_dst,tp_dst,tp_src,dl_vlan,mpls_label,ipv6_src",
                "/0/fuzzy_matching/ipv4": "dl_type,in_port,nw_proto,dl_dst,dl_src,nw_dst,tp_dst,tp_src,dl_vlan,mpls_label,nw_src,arp_tha,arp_sha",
                "/1/fuzzy_matching/ipv4": "dl_type,in_port,nw_proto,dl_dst,dl_src,nw_dst,tp_dst,tp_src,dl_vlan,mpls_label,nw_src,arp_tha,arp_sha",
                "/0/match_field/ipv6": "ipv6_dst",
                "/0/match_field/ipv4": "in_port,dl_dst,dl_src",
            }
        }
    }
    tb_data = hp.sw_post('bridges', of_instance_data)
    sprint("Openflow instance:")
    sprint(str(create_custiom_table(tb_data, field_names)))

    # create vlan
    vlan_data = {
        SSLCON_BASE_VLAN: {
            "configuration": {
                "interface": [
                    "1", "2", "3", "4", "5", "6", "7", "8", "9",
                    "10", "11", "12", "13", "14", "15", "16", "17", "18", "19",
                    "20", "21", "22", "23", "24", "25", "26", "27", "28", "29",
                    "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
                    "40", "41", "42", "43", "44", "45", "46", "47", "48", "49",
                    "50", "51", "52", "54"],
                "attach_openflow_instance": "br0",
                "mac_learning": "true",
                "l3_enable": "false"
            }
        }
    }
    for vlan_id in range(4038, 4085):
        vlan_data[str(vlan_id)] = {
            "configuration": {
                "interface": ["54"],
                "attach_openflow_instance": "br0",
                "mac_learning": "true",
                "l3_enable": "false"
            }}
    tb_data = hp.sw_post('vlans', vlan_data)
    sprint("Vlans:")
    sprint(str(create_custiom_table(tb_data, field_names)))

    # Modify the interfaces
    interface_base_data = [
        {"op": "add", "path": "/configuration/transceiver_mode", "value": "rx"},
        {"op": "add", "path": "/configuration/admin", "value": "up"},
        {"op": "add", "path": "/configuration/link_enable", "value": True},
        {"op": "add", "path": "/configuration/attach_openflow_instance",
         "value": SSLCON_OPENFLOW_INSTANCE_NAME},
        {"op": "add", "path": "/configuration/vlan_tag", "value": SSLCON_BASE_VLAN}
    ]
    tb = None
    for intf in range(1, 55):
        tmp = deepcopy(interface_base_data)
        tmp.append(
            {"op": "add", "path": "/configuration/ofport", "value": str(intf)})
        if intf == 54:
            tmp.append(
                {"op": "add", "path": "/configuration/vlan_mode", "value": "trunks"})
            tmp.append({"op": "add", "path": "/configuration/vlan_trunks",
                        "value": SSLCON_MAP_PORT_VLAN})
        else:
            tmp.append(
                {"op": "add", "path": "/configuration/vlan_mode", "value": "access"})
        tb_data = hp.sw_patch('interfaces/{0}'.format(intf), tmp)
        if tb == None:
            tb = create_custiom_table(tb_data, field_intf_names)
        else:
            table_add_row(tb, tb_data.append(str(intf)))
    sprint("Interfaces:")
    sprint(str(tb))


@cli.command()
@click.argument("op", type=click.STRING, autocompletion=sslcon_sw_base_op)
def sslcon_sw_base_configuration(op):
    if op == 'show':
        sslcon_sw_base_configuration_show()
    elif op == 'remove':
        sslcon_sw_base_configuration_remove()
    elif op == 'create':
        sslcon_sw_base_configuration_create()
    else:
        sprint("Invalid values input!!")


sw_sslcon_finsh = ''
