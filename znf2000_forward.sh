scli syscfg reset all

scli acl create 1 imsi 460028100545447
scli action create 1 no_basis_action C1
scli acl sync

scli intf-cpu set IG1 port_list X27
scli intf-cpu set IG1 ingress_config rule_to_action {1:1}

scli gtpv2-stat cleanp