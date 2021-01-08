import click
from json import dumps
from base import cli, SF_PRINT
from utils.http_helper import hp
from utils.tools import  * 
from utils.static_data import *
from utils.net_tools import *


'''
    This module instructions:
        It's just an interim process at the moment
'''
################################ CONFIG  ####################################
def sslcon_config_operation(ctx, args, incomplete):
    op = [('show',  'show config detail'),
              ('set',   'set global config'),
              ('add',   'add interface config'),
              ('clean',   'clean interface config'),
              ('delete','detete interface config')]
    return [c for c in op if incomplete in c[0]]

def sslcon_config_config(ctx, args, incomplete):
    comp = []
    if args[-1]== "show":
        comp = [('all', 'all config'),
                ('concaten_interfaces', 'show concaten_interfaces config'),
                ('use_server_info_flag', 'show use_server_info_flag config')]
    elif args[-1] == "set":
        comp = [('use_server_info_flag', 'set user server_info')]
    elif args[-1] == "add":
        comp = [('concaten_interfaces', 'add concaten_interfaces')]
    elif args[-1] == "delete":
        comp = [('concaten_interfaces', 'delete concaten_interfaces')]
    elif args[-1] == "clean":
        comp = [('concaten_interfaces_all', 'clean all concaten_interfaces')]
    return [c for c in comp if incomplete in c[0]]

def sslcon_config_value(ctx, args, incomplete):
    comp = []
    try:
        if args[-1]== "concaten_interfaces" and args[-2] != "show":
            SF_PRINT("\nPlease input First interface\n")
            comp = set()
            try:
                comp = get_intfs_from_rest()
            except Exception as e:
                SF_PRINT("\nget sw interface error:{0}".format(e), fg = "red")
        elif args[-2]== "concaten_interfaces" and args[-3] != "show":
            SF_PRINT("\nPlease input Second interface\n")
            comp = set()
            try:
                comp = get_intfs_from_rest()
            except Exception as e:
                SF_PRINT("\nget sw interface error:{0}".format(e))
        elif args[-1] == "use_server_info_flag":
            comp = [('enable', 'open user server_info'),
                    ('disable', 'open user server_info')]
        elif args[-3] == "concaten_interfaces" and args[-4] != "show":
            comp = [('decrypto_output', 'decrypto_output config (action id)')]
        elif "decrypto_output" in args[4:]:
            SF_PRINT("\nPlease input output action id\n")
            comp = set()
            try:
                data = hp.cpu_get("actions")
                for d in data:
                    if isinstance(d[2],dict):
                        comp = list(d[2].keys())
            except Exception as e:
                SF_PRINT("\nget cpu actions error:{0}".format(e), fg = "red")
        else:
            return []
        return [c for c in comp if incomplete in c[0]]
    except:
        SF_PRINT("Invalid values input!!")

def sslcon_config_show(config):
    tb_data = []
    data = hp.cpu_get('ssl_concatenation/config')
    if config == "all":
        for d in data:
            SF_PRINT("\nCode : {0}  Ipaddr : {1}".format(d[0], d[1]))
            SF_PRINT("\ncurrent use_server_info_flag : {0}\n".format("enable" if d[2]["use_server_info_flag"] == 1 else "disable"))
            field_names = ["concaten_interfaces", "decrypted_output"]
            for info in d[2]["concatenation_interfaces_info"]:
                tb_data.append([info['interfaces_array'], info["decrypted_output"]])
        SF_PRINT(str(create_custiom_table(tb_data,field_names)))
    elif config == "concaten_interfaces":
        for d in data:
            SF_PRINT("\nCode : {0}  Ipaddr : {1}".format(d[0], d[1]))
            field_names = ["concaten_interfaces", "decrypted_output"]
            for info in d[2]["concatenation_interfaces_info"]:
                tb_data.append([info['interfaces_array'], info["decrypted_output"]])
        SF_PRINT(str(create_custiom_table(tb_data,field_names)))
    elif config == "use_server_info_flag":
        for d in data:
            SF_PRINT("\nCode : {0}  Ipaddr : {1}".format(d[0], d[1]))
            SF_PRINT("\ncurrent use_server_info_flag : {0}\n".format("enable" if d[2]["use_server_info_flag"] == 1 else "disable"))
    else:
        SF_PRINT("Invalid values input!!")

def sslcon_config_set(config, value):
    field_names = ["code",  "ipaddr", "body"]
    if config == "use_server_info_flag":
        if value[0] == "enable":
            patch_data = [{"op":"replace", "path":"/use_server_info_flag", "value":1}]
            data = hp.cpu_patch('ssl_concatenation/config', patch_data)
            SF_PRINT(str(create_custiom_table(data,field_names)))
        elif value[0] == "disable":
            patch_data = [{"op":"replace", "path":"/use_server_info_flag", "value":0}]
            data = hp.cpu_patch('ssl_concatenation/config', patch_data)
            SF_PRINT(str(create_custiom_table(data,field_names)))
        else:
            SF_PRINT("Invalid values input!!")
    else:
        SF_PRINT("Invalid values input!!")

def sslcon_config_add(config, value):
    field_names = ["code",  "ipaddr", "body"]
    if config == "concaten_interfaces":
        try:
            patch_data = [{"op":"add", "path":"/concatenation_interfaces_info", "value":[{"interfaces_array":[value[0], value[1]], "decrypted_output":int(value[3])}]}]
            data = hp.cpu_patch('ssl_concatenation/config', patch_data)
            SF_PRINT(str(create_custiom_table(data,field_names)))
        except:
            SF_PRINT("Invalid values input!!")
    else:
        SF_PRINT("Invalid values input!!")

def sslcon_config_delete(config, value):
    field_names = ["code",  "ipaddr", "body"]
    if config == "concaten_interfaces":
        try:
            patch_data = [{"op":"remove", "path":"/concatenation_interfaces_info", "value":[{"interfaces_array":[value[0], value[1]], "decrypted_output":int(value[3])}]}]
            data = hp.cpu_patch('ssl_concatenation/config', patch_data)
            SF_PRINT(str(create_custiom_table(data,field_names)))
        except:
            SF_PRINT("Invalid values input!!")
    else:
        SF_PRINT("Invalid values input!!")

def sslcon_config_clean(config, value):
    field_names = ["code",  "ipaddr", "body"]
    if config == "concaten_interfaces_all":
        patch_data = [{"op":"replace", "path":"/concatenation_interfaces_info", "value":[]}]
        data = hp.cpu_patch('ssl_concatenation/config', patch_data)
        SF_PRINT(str(create_custiom_table(data,field_names)))
    else:
        SF_PRINT("Invalid values input!!")

@cli.command()
@click.argument("op", type=click.STRING, autocompletion=sslcon_config_operation)
@click.argument("config", type=click.STRING, autocompletion=sslcon_config_config, required=False)
@click.argument("value", type=click.STRING, nargs = -1, autocompletion=sslcon_config_value, required=False)
def sslcon_config(op, config, value):
    if op == 'show':
        sslcon_config_show(config)
    elif op == "set":
        sslcon_config_set(config, value)
    elif op == "add":
        sslcon_config_add(config, value)
    elif op == "delete":
        sslcon_config_delete(config, value)
    elif op == "clean":
        sslcon_config_clean(config, value)
    else:
        SF_PRINT("Invalid values input!!")

################################STAT ####################################
def sslcon_stat_operation(ctx, args, incomplete):
    op = [('show',  'show stat detail'),
              ('clean', 'clean stat all')]
    return [c for c in op if incomplete in c[0]]

def sslcon_stat_filter(ctx, args, incomplete):
    if args[-1] == "clean":
        comp = [('all', 'clean all stat'),
                ('global_stat', 'clean global stat'),
                ('server_info', 'clean server_info detail stat')]
    elif args[-1]== "show":
        comp = [('all', 'all stat'),
                ('global_stat', 'clean global stat'),
                ('server_info', 'clean server_info detail stat')]
    return [c for c in comp if incomplete in c[0]]

@cli.command()
@click.argument("op", type=click.STRING, autocompletion=sslcon_stat_operation)
@click.argument("filter", type=click.STRING, autocompletion=sslcon_stat_filter, required=False)
def sslcon_stat(op, filter):
    if op == 'show':
        if filter == "all":
            data = hp.cpu_get('ssl_concatenation/stat')
        elif filter == "global_stat":
            data = hp.cpu_get('ssl_concatenation/stat/global_stat')
        elif filter == "server_info":
            data = hp.cpu_get('ssl_concatenation/stat/server_info')
        else:
            SF_PRINT("Invalid values input!!")
            return
        data = [[d[0],d[1],d[2]] for d in data]
        click.echo_via_pager(str(gen_table(data, tab="count", filter=None)))
    elif op == 'clean':
        clean_data = []
        if filter == "all":
            clean_data.append({"op": "remove", "path": "/stat", "value": ""})
            clean_data.append({"op": "remove", "path": "/server_info", "value": ""})
        elif filter == "global_stat":
            clean_data.append({"op": "remove", "path": "/stat", "value": ""})
        elif filter == "server_info":
            clean_data.append({"op": "remove", "path": "/server_info", "value": ""})
        else:
            SF_PRINT("Invalid values input!!")
            return 
        data = hp.cpu_patch('ssl_concatenation/stat', clean_data)
        field_names = ["code",  "ipaddr", "body"]
        SF_PRINT(str(create_custiom_table(data,field_names)))

################################ passthrough_ip  ####################################
def sslcon_passip_operation(ctx, args, incomplete):
    op = [('show',  'show passthrough_ip'),
              ('add',   'add  passthrough_ip'),
              ('delete','delete passthrough_ip')]
    return [c for c in op if incomplete in c[0]]

def sslcon_passip_filter(ctx, args, incomplete):
    if args[-1] == "delete":
        comp = [('all', 'clean all passthrough_ip'), 
                ('IPv4', 'delete specified passthrough_ip')]
    elif args[-1]== "show":
        comp = [('all', 'all passthrough_ip')]
    elif args[-1]== "add":
        comp = [('IPv4', 'delete passthrough_ip')]
    return [c for c in comp if incomplete in c[0]]

@cli.command()
@click.argument("op", type=click.STRING, autocompletion=sslcon_passip_operation)
@click.argument("filter", type=click.STRING, autocompletion=sslcon_passip_filter, required=False)
@click.argument("value", type=click.STRING, required=False)
def sslcon_passthrough_ip(op, filter, value):
    if op == 'show':
        if filter == "all":
            data = hp.cpu_get('ssl_concatenation/passthrough_ip')
            field_names = ["code", "ipaddr", "passthrough_ip"]
            data = [[d[0],d[1],d[2]["passthrough_ip_list"]] for d in data]
            SF_PRINT(str(create_custiom_table(data, field_names)))
        else:
            SF_PRINT("Invalid values input!!")
    elif op == 'delete':
        field_names = ["code",  "ipaddr", "body"]
        clean_data = []
        if filter == "all":
            data = hp.cpu_get('ssl_concatenation/passthrough_ip')
            for info in data:
                passthrough_ip_list = info[2].get("passthrough_ip_list")
            if type(passthrough_ip_list) == list: 
                for ip in passthrough_ip_list:
                    clean_data.append({"op": "remove", "path": "/passthrough_ip_list", "value": ip})
            if len(clean_data) > 0:
                data = hp.cpu_patch('ssl_concatenation/passthrough_ip', clean_data)
                SF_PRINT(str(create_custiom_table(data,field_names)))
            else:
                SF_PRINT("no passthrough_ip need delete!!")
        elif filter == "IPv4":
            if is_valid_ipv4_address(value):
                clean_data.append({"op": "remove", "path": "/passthrough_ip_list", "value": value})
                data = hp.cpu_patch('ssl_concatenation/passthrough_ip', clean_data)
                SF_PRINT(str(create_custiom_table(data,field_names)))
            else:
                SF_PRINT("Invalid values input!!")
        else:
            SF_PRINT("Invalid values input!!")
    elif op == 'add':
        if filter == "IPv4":
            if is_valid_ipv4_address(value):
                data = [{"op": "add", "path": "/passthrough_ip_list", "value": value}]
                data = hp.cpu_patch('ssl_concatenation/passthrough_ip', data)
                field_names = ["code",  "ipaddr", "body"]
                SF_PRINT(str(create_custiom_table(data,field_names)))
            else:
                SF_PRINT("Invalid values input!!")
        else:
            SF_PRINT("Invalid values input!!")


################################ SERVER CONFIG  ####################################
def sslcon_serverip_operation(ctx, args, incomplete):
    op = [ ('show', 'show server config'),
           ('add',  'add  server config'),
           ('delete','delete server config'),
           ('sync', 'sync  server config')]
    return [c for c in op if incomplete in c[0]]

def sslcon_serverip_info(ctx, args, incomplete):
    if args[-1] == "show":
        comp = [('all', 'all server config')]
        data = hp.cpu_get('ssl_concatenation/server_config')
        for d in data:
            if isinstance(d[2],dict):
                for key in d[2].keys():
                    comp.append((key, 'show {0} server config'.format(key))) 
    elif args[-1] == "add":
        comp = [('server_index', 'server config index')]
    elif args[-1] == "delete":
        comp = [('all', 'all server config')]
        data = hp.cpu_get('ssl_concatenation/server_config')
        for d in data:
            if isinstance(d[2],dict):
                for key in d[2].keys():
                    comp.append((key, 'show {0} server config'.format(key))) 
    elif args[-1] == "sync":
        return []
    else:
        SF_PRINT("Invalid values input!!")
    return [c for c in comp if incomplete in c[0]]

def sslcon_serverip_server_index(ctx, args, incomplete):
    if args[-1] == "server_index":
        op = [('', 'index <1-65535>')]
    else:
        op = [('ip_type',   'next field name')]
    return [c for c in op if incomplete in c[0]]

def sslcon_serverip_server_iptype(ctx, args, incomplete):
    if args[-1] == "ip_type":
        op = [ ('4', 'only support ipv4')]
    else:
        op = [ ('server_ip',   'next field name')]
    return [c for c in op if incomplete in c[0]]

def sslcon_serverip_server_serverip(ctx, args, incomplete):
    if args[-1] == "server_ip":
        op = [ ('', '<IPv4> ipv4 address')]
    else:
        op = [('server_port',   'next field name')]
    return [c for c in op if incomplete in c[0]]

def sslcon_serverip_server_serverport(ctx, args, incomplete):
    if args[-1] == "server_port":
        op = [ ('', 'port number <1-65535>')]
    else:
        op = [ ('decrypted_server_port',   'next field name')]
    return [c for c in op if incomplete in c[0]]

def sslcon_serverip_server_decport(ctx, args, incomplete):
    if args[-1] == "decrypted_server_port":
        op = [ ('', 'port number <1-65535>')]
    else:
        return []
    return [c for c in op if incomplete in c[0]]

def sslcon_server_config_show(info):
    tb_data = []
    field_names = ["server_index", "ip_type", "srv_ip", "srv_port", "modify_port", 
                   "server_name", "key_filename", "cert_filename", "chain_filename"]
    if info == "all":
        data = hp.cpu_get('ssl_concatenation/server_config?depth=3')
        for d in data:
            if isinstance(d[2],dict):
                SF_PRINT("\nCode : {0}  Ipaddr : {1}".format(d[0], d[1]))
                for key in d[2].keys():
                    tb_data.append([d[2][key]["server_index"], d[2][key]["ip_type"], d[2][key]["srv_ip"], 
                                    d[2][key]["srv_port"], d[2][key]["modify_port"], d[2][key]["server_name"], 
                                    d[2][key]["key_filename"], d[2][key]["cert_filename"], d[2][key]["chain_filename"]])
                SF_PRINT(str(create_custiom_table(tb_data,field_names)))
    elif info.isdigit():
        data = hp.cpu_get('ssl_concatenation/server_config/{0}'.format(info))
        for d in data:
            if isinstance(d[2],dict):
                SF_PRINT("\nCode : {0}  Ipaddr : {1}".format(d[0], d[1]))
                for key in d[2].keys():
                    tb_data.append([d[2][key]["server_index"], d[2][key]["ip_type"], d[2][key]["srv_ip"], 
                                    d[2][key]["srv_port"], d[2][key]["modify_port"], d[2][key]["server_name"], 
                                    d[2][key]["key_filename"], d[2][key]["cert_filename"], d[2][key]["chain_filename"]])
                SF_PRINT(str(create_custiom_table(tb_data,field_names)))
    else:
        SF_PRINT("Invalid values input!!")

def sslcon_server_config_delete(info):
    tb_data = []
    field_names = ["code",  "ipaddr", "body"]
    if info == "all":
        data = hp.cpu_get('ssl_concatenation/server_config')
        for d in data:
            if isinstance(d[2],dict):
                for key in d[2].keys():
                    hp.cpu_delete('ssl_concatenation/server_config/{0}'.format(key))
        for http in hp.cpus:
            tb_data.append([200, http.addr, ""])
        SF_PRINT(str(create_custiom_table(tb_data,field_names)))
        SF_PRINT("NEED SYNC!!!!")
    elif info.isdigit():
        tb_data = hp.cpu_delete('ssl_concatenation/server_config/{0}'.format(info))
        SF_PRINT(str(create_custiom_table(tb_data,field_names)))
        SF_PRINT("NEED SYNC!!!!")
    else:
        SF_PRINT("Invalid values input!!")

def sslcon_server_config_add(info, \
    server_index, ip_type, server_ip, server_port, decrypted_server_port, \
    server_name, key_file, cert_file, chain_file):

    server_index = server_index[0]
    ip_type      = ip_type[0]
    server_ip    = server_ip[0]
    server_port  = server_port[0]

    if not server_index.isdigit() or \
       not ip_type.isdigit() or \
       not is_valid_ipv4_address(server_ip) or \
       not server_port.isdigit() or \
       not decrypted_server_port.isdigit():
           SF_PRINT("Invalid values input!!")
           return

    fields ={
        "server_index": server_index,
        "ip_type": ip_type,
        "srv_ip": server_ip,
        "srv_port": server_port,
        "modify_port": decrypted_server_port
    }
    if server_name:
        fields["server_name"] = server_name

    files = []
    if key_file:
        files.append(("key_file", (key_file.name.split("/")[-1], key_file.read(), "application/octet-stream")))

    if cert_file:
        files.append(("cert_file", (cert_file.name.split("/")[-1], cert_file.read(), "application/octet-stream")))

    if chain_file:
        files.append(("chain_file", (chain_file.name.split("/")[-1], chain_file.read(), "application/octet-stream")))

    field_names = ["code",  "ipaddr", "body"]
    tb_data = hp.cpu_raw_post('ssl_concatenation/server_config', data = fields, files = files)
    SF_PRINT(str(create_custiom_table(tb_data,field_names)))
    SF_PRINT("NEED SYNC!!!!")

@cli.command()
@click.argument("op", type=click.STRING, autocompletion=sslcon_serverip_operation)
@click.argument("info", type=click.STRING, autocompletion=sslcon_serverip_info, required=False)
@click.argument("server_index", type=click.STRING, nargs = 2, autocompletion = sslcon_serverip_server_index, required=False)
@click.argument("ip_type", type=click.STRING,   nargs = 2, autocompletion = sslcon_serverip_server_iptype, required=False)
@click.argument("server_ip", type=click.STRING, nargs = 2, autocompletion = sslcon_serverip_server_serverip, required=False)
@click.argument("server_port", type=click.STRING, nargs = 2, autocompletion = sslcon_serverip_server_serverport, required=False)
@click.argument("decrypted_server_port", type=click.STRING, nargs=1, autocompletion = sslcon_serverip_server_decport, default = "80", required=False)
@click.option("--server_name", type=click.STRING,   required=False)
@click.option("--key_file",   type=click.File("rb"), required=False)
@click.option("--cert_file",  type=click.File("rb"), required=False)
@click.option("--chain_file", type=click.File("rb"), required=False)
def sslcon_server_config(op, info, \
    server_index, ip_type, server_ip, server_port, decrypted_server_port, \
    server_name, key_file, cert_file, chain_file):
    if op == "sync":
        patch_data = [{"op":"replace", "path": "/sync", "value":""}]
        data = hp.cpu_patch('ssl_concatenation/server_config', patch_data)
        field_names = ["code",  "ipaddr", "body"]
        SF_PRINT(str(create_custiom_table(data,field_names)))
    elif op == "show":
        sslcon_server_config_show(info)
    elif op == "add":
        sslcon_server_config_add(info, \
                server_index, ip_type, server_ip, server_port, decrypted_server_port, \
                server_name, key_file, cert_file, chain_file)
    elif op == "delete":
        sslcon_server_config_delete(info)
    else:
        SF_PRINT("Invalid values input!!")

