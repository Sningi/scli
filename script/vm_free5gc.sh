scli syscfg reset cpu

scli acl create 103 imei 11100000000000000
scli acl sync
scli acl clean 

scli action create 1 forward G2

scli intf set G1 ingress_config rule_to_action {103:1}
#scli intf-cpu set G1 ingress_config default_action 1
