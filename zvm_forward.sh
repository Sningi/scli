scli syscfg reset cpu

scli acl create 1 imsi 460028100545447
scli action create 1 forward G2
scli acl sync
scli intf-cpu set G1 ingress_config rule_to_action {1:1}

scli gtpv2-stat clean