scli syscfg reset all

scli acl-sw create group_2 1112 --action forward --evif_name C6 --type ipv4 --vlanid 4084 --vlan_cmd add_vlan
scli intf-sw bind X48 group_2 

scli acl-sw create group_3 1999 --action forward --evif_name X48 --type ipv4 --vlan 4084
scli intf-sw bind C6 group_3

scli intf-sw enable X48,C1 rx

scli acl create 1 imsi 460028100545447
scli action create 1 no_basis_action X48
scli acl sync

scli intf-cpu set IG1 port_list X48
scli intf-cpu set IG1 ingress_config rule_to_action {1:1}

scli gtpv2-stat cleanp