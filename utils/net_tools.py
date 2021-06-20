import re
import socket
import os
###########################
#      IP string check
###########################


def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True


def is_valid_ipv6_address(address):
    try:
        socket.inet_pton(socket.AF_INET6, address)
    except socket.error:  # not a valid address
        return False
    return True


def check_ip_string(address):
    ret = is_valid_ipv4_address(address)
    if ret:
        return 0
    ret = is_valid_ipv6_address(address)
    if ret:
        return 1
    return -1

# check first : dst : bytes or ctype


def trans_ip4_address_str(address, dst):
    len = 4
    addr = socket.inet_pton(socket.AF_INET, address)

    for i in range(len):
        dst[i] = addr[i]

# check first : dst : bytes or ctype


def trans_ip6_address_str(address, dst):
    len = 16
    addr = socket.inet_pton(socket.AF_INET6, address)

    for i in range(len):
        dst[i] = addr[i]


def trans_ip4_address(target_bytes):
    length = 4
    temp = b'1234'
    t = bytearray(temp)
    zero_bytes_cnt = 0
    for i in range(length):
        t[i] = target_bytes[i]

        if t[i] == 0:
            zero_bytes_cnt += 1

    if zero_bytes_cnt == length:
        return None

    addr = socket.inet_ntop(socket.AF_INET, t)

    return addr


def trans_ip6_address(target_bytes):
    length = 16

    temp = (b'1234')*4
    t = bytearray(temp)

    zero_bytes_cnt = 0

    for i in range(16):
        t[i] = target_bytes[i]

        if t[i] == 0:
            zero_bytes_cnt += 1

    if zero_bytes_cnt == length:
        return None

    addr = socket.inet_ntop(socket.AF_INET6, t)

    return addr


###########################
#      MAC check
###########################

def check_mac_sting(mac_addr):
    valid = re.compile(r"([A-Fa-f0-9]{2}:){5}[A-Fa-f0-9]{2}")
    if valid.fullmatch(mac_addr) == None:
        return False
    return True

# dst : c_ubyte * 6


def trans_mac_to_bytes(dst, mac_addr):
    hex_bytes = mac_addr.split(":")
    for i in range(0, len(hex_bytes)):
        temp = "0x" + hex_bytes[i]
        value = int(temp, 16)
        dst[i] = value


def trans_ubytes_to_mac_addr(mac_bytes):
    result = str(hex(mac_bytes[0])).replace("0x", "")
    if len(result) == 1:
        result = "0" + result
    for i in range(1, 6):
        temp = hex(mac_bytes[i])
        value = temp.replace("0x", "")
        if len(value) == 1:
            value = "0" + value
        result = result + ":" + value
    return result


def trans_ubytes_to_mac_addr_none(mac_bytes):
    zero_cnt = 0
    for i in range(6):
        if mac_bytes[i] == 0:
            zero_cnt += 1

    if zero_cnt == 6:
        return None

    return trans_ubytes_to_mac_addr(mac_bytes)

###########################
#      vlan check
###########################


def check_vlan_id(vlan_id):
    if isinstance(vlan_id, int) == False:
        return False

    if vlan_id < 0 or vlan_id > 4095:
        return False

    return True

###########################
#      ether type check
###########################


def check_ether_type_hex_str(ether_type):
    if type(ether_type) != str:
        return False

    valid = re.compile(r"0x[A-Fa-f0-9]{4}")
    if valid.fullmatch(ether_type) == None:
        return False
    return True
