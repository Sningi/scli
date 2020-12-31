import requests
from json import dumps
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from utils.http_code import STATUS
from config import Config

class Http:
    timeout = 5

    def __init__(self, uname, pwd, addr , restv):
        self.addr = addr
        self.base_url = "https://" + addr + restv
        if pwd == "Passok":
            self.auth =dumps({'username': uname,'password':pwd})
        else:
            self.auth ={'username': uname,'password':pwd}

        self.login_url = self.base_url+ "login"
        self.session  = requests.Session()
        self.timeout = 10
        ret = self.login()
        if ret[0] not in [200, 201]:
            print("login failed", ret)
        # print("login", ret)

    def login(self):
        try:
            #if cookie valid, avoid login  duplicate

            response = self.session.post(self.login_url, timeout=self.timeout, verify=False, data=self.auth)
            if response.status_code in [200, 201]:
                #save_cookie
            return [response.status_code, STATUS[response.status_code][-1]]
        except requests.exceptions.Timeout:
            return [response.status_code , ]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,]
        except requests.exceptions.HTTPError:
            return [response.status_code]


    def get(self, short_url): 
        try:
            url = self.base_url + short_url
            response = self.session.get(url=url, timeout=self.timeout,verify=False)
            # response.raise_for_status()
            return [response.status_code, self.addr, response.json()]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]


    def rest_post(self):
        try:
            response = self.session.post(url = self.sfurl, timeout = self.timeout, json = self.sfdata,  verify=False)
            return [response.status_code , response.text]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]
        #finally:
        #    return response.status_code

    def rest_delete(self):
        try:
            response = self.session.delete(url = self.sfurl, timeout = self.timeout, params = self.sfparams,verify=False)
            # response.raise_for_status()
            return [response.status_code , response.text]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]

    def rest_put(self):
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

    def rest_get_cookie(self):
        try:
            response = self.session.post(self.SF_login, timeout = self.timeout, verify=False, data= self.auth)
            return [response.status_code ,response.cookies.items()]
        except requests.exceptions.Timeout:
            return [response.status_code , "Timeout!"]
        except requests.exceptions.ConnectionError:
            return [response.status_code ,"Connection impassability!"]
        except requests.exceptions.HTTPError:
            return [response.status_code]

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
        pass

    def cpu_post(self, url, data):
        pass

    def cpu_patch(self, url, data):
        data = [rest.patch(url, data) for rest in self.cpus]
        return data

    def cpu_delete(self, url, data):
        pass

    def sw_get(self, url):
        pass

    def sw_put(self, url, data):
        pass

    def sw_post(self, url, data):
        pass

    def sw_patch(self, url, data):
        pass

    def sw_delete(self, url, data):
        pass


hp = Helper(Config)



