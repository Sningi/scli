# 一. 系统配置

1. #### 重置配置

   ```
   scli syscfg reset [cpu|sw|all]
   ```

2. #### 保存配置[未实现]

   ```
   scli syscfg save [cpu|sw|all]
   ```

3. #### 下载配置[未实现]

   ```
   scli syscfg download [cpu|sw|all] [PATH]
   ```

4. #### 上传配置[未实现]

   ```
   scli syscfg upload [cpu|sw|all] PATH
   ```

   

# 二. CPU



### A. 规则 ACL

1. #### 创建规则

   ```
   scli acl create ID TYPE VALUE
   #TYPE
   #imsi         msisdn       url          tcpflag    
   #imei         packet_type  l2           regex        combined
   #当前仅支持 imsi msisdn imei packet_type
   ```

2. ####  显示规则列表；显示规则内容

   ```
   scli acl show
   scli acl show ID
   ```

3. #### 删除规则

   ```
   scli acl delete [ID|ID-ID]
   ```

4. #### 同步规则

   ```
   scli acl delete ID
   ```



### B. 端口 INTERFACE

1. #### 查看端口配置

   ```
   scli intf-cpu show PORT ITEM
   #ITEM
   #port_list             tcp_reass_config      deduplication_enable  
   #ingress_config        ip_reass_config       deduplication_config
   ```

2. ####  配置端口属性

   ```
   #关闭去重
   scli intf-cpu set PORT deduplication_enable 0
   #设置去重忽略项
   scli intf-cpu set PORT deduplication_config deduplication_no_care_mac 1
   #设置tuple_mode 
   scli intf-cpu set PORT ingress_config tuple_mode [0|1]
   #设置端口列表【用于NF2000】
   scli intf-cpu set PORT port_list [Xn|Xn-Xm|Xn,Xm-Ck]
   ```

3. #### 配置默认转发

   ```
   scli intf-cpu set PORT ingress_config default_action ACTION_ID
   ```

4. #### 配置规则转发

   ```
   #可多行累加
   scli intf-cpu set PORT ingress_config rule_to_action {ACL_ID:ACTION_ID}
   #清除转发
   scli intf-cpu set PORT ingress_config rule_to_action {}
   ```



### B. 转发策略 ACTION

1. #### 创建action

   ```
   #转发策略【VM】
   scli action create ID forward PORT
   #转发策略【NF2000】
   scli action create ID no_basis_action PORT1,PORT2
   ```

2. ####  删除action

   ```
   scli action delete ID
   ```

3. #### 配置高级功能

   ```
   #配置gtp头剥离
   scli action [enable|disable] 128 remove_tunnel_header_gtp
   ```

   

# 三. Switch