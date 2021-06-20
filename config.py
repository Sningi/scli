import json
import configparser
from sys import exit

class Config:
    cpu_user = None
    cpu_pwd = None

    sw_user = None
    sw_pwd = None

    cpu_restv = None
    sw_restv = None

    cpu_addrs = []
    sw_addrs = []

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Config, "_instance"):
            Config._instance = Config(*args, **kwargs)
        return Config._instance


scli_cfg_dir = ""
scli_cfg_filename = scli_cfg_dir + "scli.cfg"

scli_config = configparser.ConfigParser()
scli_config.read(scli_cfg_filename, encoding="utf-8")

devControl = "devControl"

if scli_config.has_section(devControl):
    options_list = scli_config.options(devControl)
    for option in options_list:
        if option == "cpu_user":
            Config.cpu_user = scli_config.get(devControl, option)
        elif option == "cpu_pwd":
            Config.cpu_pwd = scli_config.get(devControl, option)
        elif option == "sw_user":
            Config.sw_user = scli_config.get(devControl, option)
        elif option == "sw_pwd":
            Config.sw_pwd = scli_config.get(devControl, option)
        elif option == "cpu_restv":
            Config.cpu_restv = scli_config.get(devControl, option)
        elif option == "sw_restv":
            Config.sw_restv = scli_config.get(devControl, option)
        elif option == "cpu_addrs":
            try:
                Config.cpu_addrs = json.loads(scli_config.get(devControl, option))
            except Exception as e:
                print("Config: CPU addrs error",e)
                exit()
        elif option == "sw_addrs":
            try:
                Config.sw_addrs = json.loads(scli_config.get(devControl, option))
            except:
                print("Config: SWITCH addrs error")
                exit()

if __name__ == "__main__":
    print("TEST IP:", Config.cpu_addrs, " type:", type(Config.cpu_addrs))
    print("TEST IP:", Config.sw_addrs, " type:", type(Config.sw_addrs))
    print("RESTv:", Config.sw_restv)
    print("RESTv:", Config.cpu_restv)
