class Config:
    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Config, "_instance"):
            Config._instance = Config(*args, **kwargs)
        return Config._instance

    cpu_user  = 'admin'
    cpu_pwd   = 'passok'
    sw_user   = 'admin'
    sw_pwd    = 'Passok'
    sw_restv  = '/rest/v2/'
    cpu_restv = '/rest/v1/'

    cpu_addrs = [
       "192.168.3.95:2020",
        # "192.168.1.210:2020",
        # "192.168.1.210:2014"
    ]
    sw_addrs = [
        "192.168.1.210:81"
    ]


