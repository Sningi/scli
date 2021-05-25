scli syscfg reset cpu

# ZTE
# scli acl create 103 msisdn 436605000099
# scli acl create 103 imsi 232145000000099

# HUAWEI
scli acl create 102 msisdn 8617201150204
# scli acl create 106 imsi 460072011500023

scli action create 1 forward G2
scli acl sync
# scli intf-cpu set G1 ingress_config rule_to_action {102:1}
scli intf-cpu set G1 ingress_config default_action 1
