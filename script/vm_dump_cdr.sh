scli syscfg reset cpu

# scli acl create 100 packet_type n2_cdr
scli acl create 200 packet_type s1_cdr
#scli acl create 200 packet_type gtpv1_cdr
#scli acl create 300 packet_type gtpv2_cdr
scli action create 1 forward G2
scli acl sync
scli intf set G1 ingress_config rule_to_action {200:1}