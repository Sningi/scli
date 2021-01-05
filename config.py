
class Config:

    cpu_ip_ports = []
    switch_ip_ports = []
    cpu_name = "admin"
    cpu_pwd = "passok"
    sw_name = "admin"
    sw_pwd = "Passok"
    sw_restv = "/rest/v2/"
    cpu_restv = "/rest/v1/"
    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Config, "_instance"):
            Config._instance = Config(*args, **kwargs)
        return Config._instance

Config.cpu_addrs = [
    "192.168.1.210:2020",
    "192.168.1.210:2014",
    # "192.168.3.95:2020",
    ]

Config.sw_addrs = [
    "192.168.1.210:81",
    "192.168.3.207:81",
    ]


if __name__ == "__main__":
    print("TEST IP:",Config.cpp_addrs)