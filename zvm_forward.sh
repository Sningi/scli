scli syscfg reset cpu

# ZTE
# scli acl create 103 msisdn 436605000099
# scli acl create 103 imsi 232145000000099

# HUAWEI
# scli acl create 200 packet_type n2_cdr
# scli acl create 101 imsi 460072011500023
# scli acl create 102 msisdn 8617201150204 
# scli acl create 103 imei 


#GTPV1
#scli acl create 200 packet_type gtpv1_cdr
#scli acl create 201 imsi 460017783705082
#scli acl create 202 msisdn 8614537784120 
# scli acl create 203 imei 358464061191850
scli acl create 203 imei 3584640611918540



#GTPV2
#scli acl create 300 packet_type gtpv2_cdr
# scli acl create 301 imsi 460000100001818
#scli acl create 302 msisdn - 
# scli acl create 303 imei 460000100001810
# scli acl create 304 imei 865166023744290

scli action create 1 forward G2
scli gtpv1-cfg enable cache

#scli acl create 144 tuple4 -s 10.150.198.182
#scli acl create 145 tuple4 -s 202.69.206.55
#scli intf-cpu set G1 ingress_config tuple_mode 2


scli acl sync
scli intf-cpu set G1 ingress_config rule_to_action {203:1}
# scli intf-cpu set G1 ingress_config rule_to_action {145:1}
#scli intf-cpu set G1 ingress_config default_action 1
