import os
import pickle
import requests
import time
from json import dumps
from utils.http_code import Httplib
from config import Config

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def SCLI_HTTP_REQUEST(cls_func):
    def wrapper(self, *args, **kwargs):
        try:
            return cls_func(self, *args, **kwargs)
        except Exception as e:
            if type(e).__name__ in requests.exceptions.__dir__():
                return [type(e).__name__  , self.addr, "connect error!!"]
    return wrapper


class Http:
    timeout = 30

    def __init__(self, uname, pwd, addr , restv, dev_rest_type = "switch"):
        self.addr = addr
        self.base_url = "https://" + addr + restv
        if dev_rest_type == "cpu":
            """cpu"""
            self.auth ={'username': uname,'password':pwd}
            self.login_url = "https://" + addr + restv + "login"
        else:
            """sw"""
            self.auth =dumps({'username': uname,'password':pwd})
            self.login_url = "https://" + addr+ "/login"

        self.session  = requests.Session()
        ret = self.login_may_use_cookie()
        if ret[0] not in [Httplib.OK, Httplib.CREATED]:
            print("{0} login failed ".format(self.addr), ret)

    def login_may_use_cookie(self, clear_cookie=False, diff_time=7190):# diff_time 2h-10s
        cookie = "/tmp/cookie_"+self.addr.replace(":","_")
        if clear_cookie and os.path.isfile(cookie):
            #cookie is invalid
            os.remove(cookie)

        if os.path.isfile(cookie) :
            diff_time = time.time()- os.path.getmtime(cookie)
            if diff_time < 7190:
                with open(cookie,"rb") as cke:
                    self.session.cookies = pickle.load(cke)
            else:
                try:
                    self.session.post(self.login_url, 
                        timeout=self.timeout, data=self.auth,verify=False)
                except Exception as e:
                    print("login {0} failed", self.addr)
        else:
            try:
                self.session.post(self.login_url, 
                    timeout=self.timeout, data=self.auth,verify=False)
            except Exception as e:
                print("login {0} failed".format(self.addr))  
        if self.session.cookies:  #refash cookie
            if diff_time >= 7190:
                with open(cookie,"wb") as cke:
                    pickle.dump(self.session.cookies,cke)
            return [Httplib.CREATED]
        else:
            return [Httplib.BAD_REQUEST]

    @SCLI_HTTP_REQUEST
    def get(self, short_url, data=None, params = None, loop = 0):
        loop += 1
        if loop > 5:
            return ["error",self.addr,"Connection impassability!"]
        self.response = self.session.get(url=self.base_url + short_url, params = params, timeout=self.timeout, verify=False)
        if self.response.status_code == Httplib.UNAUTHORIZED:
            self.login_may_use_cookie(clear_cookie=True)
            return self.get(short_url, data, params, loop = loop)
        return [self.response.status_code, self.addr, self.response.json()]

    @SCLI_HTTP_REQUEST
    def post(self, short_url, data, params = None): 
        self.response = self.session.post(url=self.base_url + short_url, json=data, params = params, timeout=self.timeout, verify=False)
        if self.response.status_code == Httplib.UNAUTHORIZED:
            self.login_may_use_cookie(clear_cookie=True)
            return self.post(short_url, data, params)
        return [self.response.status_code, self.addr, self.response.json()]

    @SCLI_HTTP_REQUEST
    def raw_post(self, short_url, raw_data, header = None, params = None): 
        self.response = self.session.post(url=self.base_url + short_url, data=raw_data, header = header , params = params, timeout=self.timeout, verify=False)
        if self.response.status_code == Httplib.UNAUTHORIZED:
            self.login_may_use_cookie(clear_cookie=True)
            return self.post(short_url, data, header, params)
        return [self.response.status_code, self.addr, self.response.text]

    @SCLI_HTTP_REQUEST
    def delete(self, short_url, data=None, params = None, ):
        self.response = self.session.delete(url=self.base_url+short_url, params = params, timeout=self.timeout, verify=False)
        if self.response.status_code == Httplib.UNAUTHORIZED:
            self.login_may_use_cookie(clear_cookie=True)
            return self.delete(short_url, data, params)
        return [self.response.status_code ,self,addr, self.response.text]

    @SCLI_HTTP_REQUEST
    def put(self, short_url, data, params = None):
        self.response = self.session.put(url=self.base_url+short_url, json=data, params = params, timeout=self.timeout, verify=False)
        if self.response.status_code == Httplib.UNAUTHORIZED:
            self.login_may_use_cookie(clear_cookie=True)
            return self.put(short_url, data, params)
        return [self.response.status_code, self.addr, self.response.text]

    @SCLI_HTTP_REQUEST
    def patch(self, short_url, data, params = None):
        self.response = self.session.patch(url=self.base_url + short_url, json=data, params = params, timeout=self.timeout, verify=False)
        if self.response.status_code == Httplib.UNAUTHORIZED:
            self.login_may_use_cookie(clear_cookie=True)
            return self.patch(short_url, data, params)
        return [self.response.status_code, self.addr, self.response.text]

class Helper:

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Helper, "_instance"):
            Helper._instance = Helper(*args, **kwargs)
        return Helper._instance

    def __init__(self, cfg):
        self.sws =  [Http(cfg.sw_user,  cfg.sw_pwd,  addr, cfg.sw_restv, "switch")  for addr in cfg.sw_addrs] 
        self.cpus = [Http(cfg.cpu_user, cfg.cpu_pwd, addr, cfg.cpu_restv, "cpu") for addr in cfg.cpu_addrs] 
    
    def cpu_get(self, url, data = None, params = None):
        data = [rest.get(url, data = None) for rest in self.cpus]
        return data

    def cpu_put(self, url, data = None, params = None):
        data = [rest.put(url,data) for rest in self.cpus]
        return data

    def cpu_post(self, url, data = None, params = None):
        data = [rest.post(url,data) for rest in self.cpus]
        return data

    def cpu_raw_post(self, url, data = None, header = None, params = None):
        data = [rest.raw_post(url, data, header) for rest in self.cpus]
        return data

    def cpu_patch(self, url, data = None, params = None):
        data = [rest.patch(url, data) for rest in self.cpus]
        return data

    def cpu_delete(self, url, data = None, params = None):
        data = [rest.delete(url, data) for rest in self.cpus]
        pass

    def sw_get(self, url, data = None, params = None):
        data = [rest.get(url, data) for rest in self.sws]
        return data

    def sw_put(self, url, data = None, params = None):
        data = [rest.put(url,data) for rest in self.sws]
        pass

    def sw_post(self, url, data = None, params = None):
        data = [rest.post(url,data) for rest in self.sws]
        pass

    def sw_raw_post(self, url, data = None, header = None, params = None):
        data = [rest.raw_post(url, data, header) for rest in self.sws]
        return data

    def sw_patch(self, url, data = None, params = None):
        data = [rest.patch(url, data) for rest in self.sws]
        return data

    def sw_delete(self, url, data = None, params = None):
        data = [rest.delete(url, data) for rest in self.sws]
        pass

def helper_may_use_cache(config):

    def create_helper():
        hp = Helper(config)
        with open(helper_cache,"wb") as hpc:
                pickle.dump(hp,hpc)
        return hp
    
    helper_cache = "/tmp/scli_helper"
    if os.path.isfile(helper_cache):
        diff_time = os.path.getmtime("./scli.cfg") - os.path.getmtime(helper_cache) 
        if diff_time < 0:
            with open(helper_cache,"rb") as hpc:
                return pickle.load(hpc)
        else:
            return create_helper()
    else:
        return create_helper()

hp = helper_may_use_cache(Config)

# import timeit
# def f1():
#     hp = helper_may_use_cache(Config)
# def f2():
#     hp = Helper(Config)
# print(timeit.repeat(stmt=f1,setup="from utils.http_helper import f1",number=100))
# print(timeit.repeat(stmt=f2,setup="from utils.http_helper import f2",number=100))


