INPUT=X1
CPU=C5

scli syscfg reset all

scli acl-sw create group_1 100 --action forward --evif_name $CPU --type ipv4 --vlanid 4084 --vlan_cmd add_vlan
scli acl-sw add group_1 101 --action forward --evif_name $CPU --type ipv6 --vlanid 4084 --vlan_cmd add_vlan
scli intf-sw bind $INPUT group_1

scli intf-sw enable $INPUT,$CPU rx

#cpu config
scli acl create 1 packet_type n2_cdr
scli acl sync
scli action create 1 no_basis_action C2
scli action enable 1 remove_tunnel_header_gtp
scli action enable 1 g33_pad
scli intf-sw enable C2 loopback

scli intf set IG1 port_list X1-X48,C1-C4
scli intf set IG1 ingress_config default_action 1

scli sctp-stat clean
scli sctp-cfg disable sctp_decode
scli http2-cfg set connect_timeout 60