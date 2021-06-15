

####!!! config !!!####
dev_ips=("192.168.1.201")
drop_id=128
ingress=1
errlog='./err.log'
####!!! config !!!####

Lines=()
read_each_line(){
    # arr=(`echo $1|awk '{len=split($0,a,",");for(i=1;i<=len;i++) print a[i]}'`)  
    arr=(${1//,/ })
    if [ "${#arr[@]}" -ne "18" ];then
        echo "line[$2] syntax error in reading, len is ${#arr[@]}:">>$errlog;echo $1>>$errlog;
    else
        #add line
        # echo [line]: $2
        Lines=("${Lines[@]}" "${1}")
    fi
}

clear_cmdfile(){
    :>rule_add
    :>rule_del
    :>rule_bind
    :>rule_unbind
}

gen_cmd(){
    # echo ${*}
    if [[ ${*} =~ "set" ]];then
        echo ${*} >> rule_add
    else
        if [[ ${*} =~ "unbind" ]];then
            echo ${*} >> rule_unbind
        else
            if [[ ${*} =~ "bind" ]];then
                echo ${*} >> rule_bind
            else
                if [[ ${*} =~ "delete" ]];then
                    echo ${*} >> rule_del
                fi
            fi
        fi
    fi
}

rpcc_do_file(){
    # echo cmd is : "${*}"
    while read line || [[ -n ${line} ]]
    do
        for dev in ${dev_ips[@]}
        do
            result=`./rpcc-static $dev 9090 2 "${line}" 10`
            if [[ $result =~ "uccess" ]];then
                :
            else
                echo [$dev] [errcmd] ${line} >>$errlog;echo [$dev] $result >>$errlog
            fi
        done
    done < $1
}


rpcc_do_cmd(){
    # echo cmd is : "${*}"
    for dev in ${dev_ips[@]}
    do
        result=`./rpcc-static $dev 9090 2 "${*}" 10`
        if [[ $result =~ "uccess" ]];then
            :
        else
            echo [$dev] [errcmd] ${*} >>$errlog;echo [$dev] $result >>$errlog
        fi
    done
}

ruleType=("unuse" "hyper" "hyper6" "user" "user" "user" "user" "both")
delete_rule(){
    # $srcRuleType $dstRuletype $idx
    if [ "$1" -eq "7" ] || [ "$2" -eq "7" ];then
        gen_cmd "unbind ingress-interface ${ingress} access-list ipset rule $(($3*2))"
        gen_cmd "unbind ingress-interface ${ingress} access-list ipset rule $(($3*2+1))"
        gen_cmd "unbind ingress-interface ${ingress} access-list ipsetv6 rule $(($3*2))"
        gen_cmd "unbind ingress-interface ${ingress} access-list ipsetv6 rule $(($3*2+1))"
        gen_cmd "delete access-list ipset rule $(($3*2))"
        gen_cmd "delete access-list ipset rule $(($3*2+1))"
        gen_cmd "delete access-list ipsetv6 rule $(($3*2))"
        gen_cmd "delete access-list ipsetv6 rule $(($3*2+1))"
    fi

    if [ "$1" -ne "0" ];then
            # src rule
            gen_cmd "unbind ingress-interface ${ingress} access-list ${ruleType[${1}]} rule ${3}"
            gen_cmd "delete access-list ${ruleType[${1}]} rule ${3}"
    else
        # dst rule 
        gen_cmd "unbind ingress-interface ${ingress} access-list ${ruleType[${2}]} rule ${3}"
        gen_cmd "delete access-list ${ruleType[${2}]} rule ${3}"
    fi
}

userType=("unuse" "unuse" "unuse" "imsi" "msisdn" "imei" "cell_id")
create_user_rule(){
    # create_user_rule $idx $srcRuleType $srcRule $wtype
   gen_cmd "set access-list user rule ${1} ${userType[${2}]} ${3}"
    # if drop
    if [ "$4" -eq "0" ];then
        gen_cmd "bind ingress-interface ${ingress} access-list user rule ${1} action ${drop_id}"
    fi
}

create_src_ip(){
    #create_src_tuple $idx $srcRuleType $srcRule $sMasklen $protocol $srcPort $wtype
    sport="any"
    proto="any"
    if [ "$6" -ne "0" ];then
        sport=$6
    fi
    if [ "$5" -ne "0" ];then
        protocol=$5
    fi
    gen_cmd "set access-list ${ruleType[${2}]} rule ${1} sip ${3}/${4} dip any sp $sport dp any proto $proto priority 255"
    # echo debug tuplev4 $create
    # if drop
    if [ "$7" -eq "0" ];then
        gen_cmd  "bind ingress-interface ${ingress} access-list ${ruleType[${2}]} rule ${1} action ${drop_id}"
    fi
}

create_dst_ip(){
    #create_dst_ip $idx $dstRuletype $dstRule $dMasklen $protocol $dstPort $wtype
    dport="any"
    proto="any"
    if [ "$6" -ne "0" ];then
        dport=$6
    fi
    if [ "$5" -ne "0" ];then
        protocol=$5
    fi
    gen_cmd "set access-list ${ruleType[${2}]} rule ${1} sip any dip ${3}/${4} sp any dp ${dport} proto ${proto} priority 255"
    # echo debug hyper $create
    # if drop
    if [ "$7" -eq "0" ];then
        gen_cmd "bind ingress-interface ${ingress} access-list ${ruleType[${2}]} rule ${1} action ${drop_id}"
    fi
}

create_port(){
    #create_port 2 $idx $dstPort $wtype
    port=""
    if [ "${1}" -eq "1" ];then
        port="sport"
    else
        if [ "${1}" -eq "2" ];then
            port="dport"
        else
            echo "[error] port rule ${2} $1 $3 $4" >> $errlog
        fi
    fi

    gen_cmd "set access-list ipset rule $(($2*2)) ${port} ${3} protocol 17"
    gen_cmd "set access-list ipset rule $(($2*2+1)) ${port} ${3} protocol 6"
    gen_cmd "set access-list ipsetv6 rule $(($2*2)) ${port} ${3} protocol 17"
    gen_cmd "set access-list ipsetv6 rule $(($2*2+1)) ${port} ${3} protocol 6"
    # if drop
    if [ "$4" -eq "0" ];then
        gen_cmd "bind ingress-interface ${ingress} access-list ipset rule $(($2*2)) action ${drop_id}"
        gen_cmd "bind ingress-interface ${ingress} access-list ipset rule $(($2*2+1)) action ${drop_id}"
        gen_cmd "bind ingress-interface ${ingress} access-list ipsetv6 rule $(($2*2)) action ${drop_id}"
        gen_cmd "bind ingress-interface ${ingress} access-list ipsetv6 rule $(($2*2+1)) action ${drop_id}"
    fi
}

gen_cmd_each_line(){
    for line in ${Lines[@]}
    do
        rule_field=(`echo ${line}|awk '{len=split($0,a,",");for(i=1;i<=len;i++) print a[i]}'`)   
        method=${rule_field[0]}
        # grpid=${rule_field[1]}        #unused
        # timeout=${rule_field[5]}      #unused
        # direct=${rule_field[7]}       #unused
        # priority=${rule_field[16]}    #unused
        # reserve=${rule_field[17]}     #unused
        idx=${rule_field[2]}
        wtype=${rule_field[3]}
        extend=${rule_field[4]}
        protocol=${rule_field[6]}
        srcRule=${rule_field[8]}
        sMasklen=${rule_field[9]}
        srcRuleType=${rule_field[10]}
        srcPort=${rule_field[11]}
        dstRule=${rule_field[12]}
        dMasklen=${rule_field[13]}
        dstRuletype=${rule_field[14]}
        dstPort=${rule_field[15]}


        if [ "$method" -eq "1" ];then
            # echo "delete rule"
            delete_rule $srcRuleType $dstRuletype $idx
        else
            # add rule
            # echo add rule rule type:$srcRuleType  $dstRuletype 
            case $srcRuleType in
            0)
                # goto dst rule
                case $dstRuletype in
                0)
                    echo "error srcRuleType 0 dstRuleType 0" >> $errlog
                ;;
                1)
                    create_dst_ip $idx $dstRuletype $dstRule $dMasklen $protocol $dstPort $wtype
                ;;
                2)
                    create_dst_ip $idx $dstRuletype $dstRule $dMasklen $protocol $dstPort $wtype
                ;;
                7)
                    #only port
                    create_port 2 $idx $dstPort $wtype
                ;;
                *)
                #3,4,5,6 user rule
                    create_user_rule $idx $dstRuletype $dstRule $wtype
                esac
                ;;
            1)
                #src tuplev4
                create_src_ip $idx $srcRuleType $srcRule $sMasklen $protocol $srcPort $wtype
                ;;
            2)
                #src tuplev6
                create_src_ip $idx $srcRuleType $srcRule $sMasklen $protocol $srcPort $wtype
                ;;
            7)
                #only port
                create_port 1 $idx $srcPort $wtype
                ;;
            *)
                #3,4,5,6 user rule
                create_user_rule $idx $srcRuleType $srcRule $wtype
                ;;
            esac
        fi
    done
}

read_file(){
    declare -i linecount
    let linecount=0
    while read line || [[ -n ${line} ]]
    do
        let linecount=$linecount+1
        read_each_line $line $linecount
    done < $1
}


patch_config(){
    rpcc_do_file rule_unbind
    rpcc_do_file rule_del
    rpcc_do_cmd "sync"
    rpcc_do_file rule_add
    rpcc_do_cmd "sync"
    rpcc_do_file rule_bind
}


main(){
    
    # if [ "$1" = "do" ];then
    #     echo "${*}"
    #     gen_cmd $2
    #     exit 0
    # fi
    #STEP 1  assert file
    if [ ! -f $1 ];
    then
        echo "file not exist"
        exit 1
    else
        #STEP 2 read file
        echo ====[ `date` start ]==== > $errlog
        # start_time=$(date +%s)
        read_file $1
        echo ====[ `date` read over ]==== >> $errlog
        # end_time=$(date +%s)
        # cost_time=$[ $end_time-$start_time ]
        # echo "readfile time is $(($cost_time/60))min $(($cost_time%60))s"
        #STEP 3 clear cmdfile
        clear_cmdfile

        gen_cmd_each_line
        echo ====[ `date` gen finish ]==== >> $errlog

        # patch cmd to dev
        patch_config

        echo ====[ `date` patch finish ]==== >> $errlog
    fi
}


main ${*}
