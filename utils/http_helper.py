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
            print("login failed", ret)
        # print("login", ret)

    def login_may_use_cookie(self, diff_time=7190):# diff_time 2h-10s
        cookie = "/tmp/cookie_"+self.addr.replace(":","_")
        if os.path.isfile(cookie) :
            diff_time = time.time()- os.path.getmtime(cookie)
            if diff_time < 7190:
                with open(cookie,"rb") as cke:
                    self.session.cookies = pickle.load(cke)
            else:
                self.session.post(self.login_url, 
                    timeout=self.timeout, data=self.auth,verify=False)
        else:
            self.session.post(self.login_url, 
                timeout=self.timeout, data=self.auth,verify=False)
        if self.session.cookies:  #refash cookie
            if diff_time >= 7190:
                with open(cookie,"wb") as cke:
                    pickle.dump(self.session.cookies,cke)
            return [201]
        else:
            return [400]

    def get(self, short_url): 
        try:
            response = self.session.get(url=self.base_url + short_url, timeout=self.timeout, verify=False)
            return [response.status_code, self.addr, response.json()]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]

    def post(self, short_url, data): 
        try:
            response = self.session.get(url=self.base_url + short_url, json=data, timeout=self.timeout, verify=False)
            return [response.status_code, self.addr, response.json()]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]

    def delete(self, short_url):
        try:
            response = self.session.delete(url=self.base_url + short_url, timeout=self.timeout, verify=False)
            # response.raise_for_status()
            return [response.status_code , response.text]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]

    def put(self, short_url, data):
        try:
            response = self.session.put(url = self.sfurl, json = self.sfdata, timeout = self.timeout, verify=False)
            # response.raise_for_status()
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
        data = [rest.get(url) for rest in self.cpus]
        return data

    def cpu_post(self, url, data):
        pass

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
        pass

    def sw_delete(self, url, data):
        pass


hp = Helper(Config)



