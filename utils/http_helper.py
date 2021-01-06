import os
import pickle
import requests
import time
from json import dumps
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from utils.http_code import STATUS
from config import Config

class Http:
    timeout = 10

    def __init__(self, uname, pwd, addr , restv):
        self.addr = addr
        self.base_url = "https://" + addr + restv
        if pwd == "Passok":
            """sw"""
            self.auth =dumps({'username': uname,'password':pwd})
            self.login_url = "https://" + addr+ "/login"
        else:
            """cpu"""
            self.auth ={'username': uname,'password':pwd}
            self.login_url = "https://" + addr + restv + "login"

        self.session  = requests.Session()
        ret = self.login_may_use_cookie()
        if ret[0] not in [200, 201]:
            print("{0} login failed ".format(self.addr), ret)
        # print("login", ret)

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
            return [201]
        else:
            return [400]

    def get(self, short_url, loop=0):
        loop += 1
        if loop > 5:
            return ["error",self.addr,"Connection impassability!"]
        try:
            response = self.session.get(url=self.base_url + short_url, timeout=self.timeout, verify=False)
            if response.status_code == 401:
                self.login_may_use_cookie(clear_cookie=True)
                return self.get(short_url,loop)
            return [response.status_code, self.addr, response.json()]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return ["error",self.addr,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]
        except Exception as e:
            print("error :",e)
            print(response.status_code)
            print(response.content)

    def post(self, short_url, data): 
        try:
            response = self.session.get(url=self.base_url + short_url, json=data, timeout=self.timeout, verify=False)
            if response.status_code == 401:
                self.login_may_use_cookie(clear_cookie=True)
                return self.post(short_url, data)
            return [response.status_code, self.addr, response.json()]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]

    def delete(self, short_url):
        try:
            response = self.session.delete(url=self.base_url+short_url, timeout=self.timeout, verify=False)
            if response.status_code == 401:
                self.login_may_use_cookie(clear_cookie=True)
                return self.delete(short_url)
            return [response.status_code , response.text]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]

    def put(self, short_url, data):
        try:
            response = self.session.put(url=self.base_url+short_url, json=dumps(data), timeout=self.timeout, verify=False)
            if response.status_code == 401:
                self.login_may_use_cookie(clear_cookie=True)
                return self.put(short_url, data)
            return [response.status_code, self.addr, response.text]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]
        finally:
            return [response.status_code, response.text]

    def patch(self, short_url, data):
        try:
            url = self.base_url + short_url
            response = self.session.patch(url=url, json=data, timeout=self.timeout, verify=False)
            if response.status_code == 401:
                self.login_may_use_cookie(clear_cookie=True)
                return self.patch(short_url, data)
            return [response.status_code, self.addr, response.json()]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]
        finally:
            return [response.status_code, self.addr, response.status_code]

class Helper:

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Helper, "_instance"):
            Helper._instance = Helper(*args, **kwargs)
        return Helper._instance

    def __init__(self, cfg):
        self.sws = [Http(cfg.sw_name, cfg.sw_pwd, addr, cfg.sw_restv) for addr in cfg.sw_addrs] 
        self.cpus = [Http(cfg.cpu_name, cfg.cpu_pwd, addr, cfg.cpu_restv) for addr in cfg.cpu_addrs] 
    
    def cpu_get(self, url):
        data = [rest.get(url) for rest in self.cpus]
        return data

    def cpu_put(self, url, data):
        data = [rest.put(url,data) for rest in self.cpus]
        return data

    def cpu_post(self, url, data):
        data = [rest.post(url,data) for rest in self.cpus]
        return data

    def cpu_patch(self, url, data):
        data = [rest.patch(url, data) for rest in self.cpus]
        return data

    def cpu_delete(self, url, data):
        pass

    def sw_get(self, url):
        data = [rest.get(url) for rest in self.sws]
        return data

    def sw_put(self, url, data):
        pass

    def sw_post(self, url, data):
        pass

    def sw_patch(self, url, data):
        data = [rest.patch(url, data) for rest in self.sws]
        return data

    def sw_delete(self, url, data):
        pass

def helper_may_use_cache(config):

    def create_helper():
        hp = Helper(config)
        with open(helper_cache,"wb") as hpc:
                pickle.dump(hp,hpc)
        return hp
    
    helper_cache = "/tmp/scli_helper"
    if os.path.isfile(helper_cache):
        diff_time = os.path.getmtime("./config.py") - os.path.getmtime(helper_cache) 
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


