scli syscfg reset cpu

# scli acl create 103 msisdn 436605000099
scli acl create 103 imsi 232145000000099
scli action create 1 forward G2
scli acl sync
scli intf-cpu set G1 ingress_config rule_to_action {103:1}
# scli intf-cpu set G1 ingress_config default_action 1
