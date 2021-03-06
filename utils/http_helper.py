import os
from re import S
import time
import asyncio

from json import dumps
from aiohttp import TCPConnector, CookieJar, ClientSession
from aiohttp.client_exceptions import ClientConnectorError
from attr import has
from utils.http_code import HTTP
from click import secho as sprint
from common.config import Config
class Http:
    timeout = 4
    long_timeout = 30

    def __init__(self, uname, pwd, addr, restv, dev_rest_type="switch"):
        self.addr = addr.split(".")[-1]
        self.base_url = "https://" + addr + restv
        self.dev_rest_type = dev_rest_type
        if dev_rest_type == "cpu":
            """cpu"""
            self.auth = {'username': uname, 'password': pwd}
            self.login_url = "https://" + addr + restv + "login"
        else:
            """sw"""
            self.auth = dumps({'username': uname, 'password': pwd})
            self.login_url = "https://" + addr + "/login"
        self.session = None
        self.active = False
        # ret = asyncio.run(self.login_may_use_cookie())
        # if ret not in [HTTP.OK, HTTP.CREATED]:
        #     pass
        #     print("{0} login failed ".format(self.addr), ret)

    # diff_time 2h-10s
    async def login_may_use_cookie(self, clear_cookie=False, diff_time=7190):

        cookie = "/tmp/cookie_"+self.addr.replace(":", "_")
        jar = CookieJar(unsafe=True)
        with_cookie = False

        async def login():
            try:
                async with self.session.post(self.login_url, timeout=self.timeout, data=self.auth) as res:
                    await res.read()
                    code = res.status
                    if code in [HTTP.OK, HTTP.CREATED]:
                        self.session.cookie_jar.save(cookie)
                        self.active = True
                    return code
            except Exception as e:
                print("[ERROR]: login {1} {0} failed".format(self.addr,self.dev_rest_type))

        if clear_cookie:
            # await self.del_session()
            if os.path.isfile(cookie):
                #cookie is invalid
                os.remove(cookie)

        if os.path.isfile(cookie) and time.time() - os.path.getmtime(cookie) < 7190:
            jar.load(cookie)
            with_cookie = True
        if not clear_cookie:
            self.session = ClientSession(
                connector=TCPConnector(ssl=False), cookie_jar=jar)

        if not with_cookie:
            return await login()
        else:
            self.active = True
            return HTTP.OK

    async def get(self, short_url, data=None, params=None, loop=0):
        loop += 1
        if loop > 3:
            return [400, self.addr, "E(1)"]
        async with self.session.get(url=self.base_url + short_url, params=params, timeout=self.timeout) as res:
            try:
                data = await res.json()
            except:
                data = await res.text()
            if res.status == HTTP.UNAUTHORIZED:
                await self.login_may_use_cookie(clear_cookie=True)
                return await self.get(short_url, data, params, loop=loop)
            return [res.status, self.addr, data]

    
    async def get_file(self, short_url, filename=None, params=None, loop=0):
        def save_file(fd , data):
            fd.write(data)
        loop += 1
        if loop > 3:
            return [400, self.addr, "E(1)"]
        async with self.session.get(url=self.base_url + short_url, params=params, timeout=self.long_timeout) as res:
            if res.status== HTTP.OK:
                fd = open(filename, 'wb')
                #获取loop 
                lp = asyncio.get_event_loop()
                while True:
                    #异步等待结果 , Chunk_size 每个分片大小
                    data = await res.content.read(512)
                    if not data:
                        break
                    #等待写入，在线程池中写入
                    # run_in_executor 返回一个future，因此可等待
                    await lp.run_in_executor(None,save_file,fd,data)

            if res.status == HTTP.UNAUTHORIZED:
                await self.login_may_use_cookie(clear_cookie=True)
                return await self.get(short_url, filename, params, loop=loop)
            return [res.status, self.addr, 'success']

    async def post(self, short_url, data, params=None, loop=0):
        loop += 1
        if loop > 3:
            return [400, self.addr, "E(1)"]
        async with self.session.post(url=self.base_url + short_url, json=data, params=params, timeout=self.timeout) as res:
            data = await res.text()
            if res.status == HTTP.UNAUTHORIZED:
                await self.login_may_use_cookie(clear_cookie=True)
                return await self.post(short_url, data, params, loop=loop)
            return [res.status, self.addr, data]

    async def post_file(self, short_url, filename=None,  params=None, loop=4):
        loop += 1
        if loop > 3:
            return [400, self.addr, "E(1)"]
        from aiohttp import FormData
        data = FormData()  
        data.add_field('shm_config',
                    open(filename, 'rb'),
                    filename=filename,
                    content_type='application/gzip')
    

        async with self.session.post(url=self.base_url + short_url, data=data, timeout=1000) as res:
            data = await res.text()
            if res.status == HTTP.UNAUTHORIZED:
                await self.login_may_use_cookie(clear_cookie=True)
                return await self.post_file(short_url, filename, params, loop=loop)
        return [res.status, self.addr, 'success']

    async def delete(self, short_url, data=None, params=None, loop=0):
        loop += 1
        if loop > 3:
            return [400, self.addr, "E(1)"]
        async with self.session.delete(url=self.base_url+short_url, params=params, timeout=self.timeout) as res:
            data = await res.text()
            if res.status == HTTP.UNAUTHORIZED:
                await self.login_may_use_cookie(clear_cookie=True)
                return await self.delete(short_url, data, params, loop=loop)
        return [res.status, self.addr, data]

    async def put(self, short_url, data, params=None, loop=0):
        loop += 1
        if loop > 3:
            return [400, self.addr, "E(1)"]
        async with self.session.put(url=self.base_url+short_url, json=data, params=params, timeout=self.timeout) as res:
            data = await res.text()
            if res.status == HTTP.UNAUTHORIZED:
                await self.login_may_use_cookie(clear_cookie=True)
                return await self.put(short_url, data, params, loop=loop)
            return [res.status, self.addr, data]

    async def patch(self, short_url, data, params=None, loop=0):
        loop += 1
        if loop > 3:
            return [400, self.addr, "E(1)"]
        async with self.session.patch(url=self.base_url + short_url, json=data, params=params, timeout=self.timeout) as res:
            data = await res.text()
            if res.status == HTTP.UNAUTHORIZED:
                await self.login_may_use_cookie(clear_cookie=True)
                return await self.patch(short_url, data, params, loop=loop)
            return [res.status, self.addr, data]

    async def del_session(self):
        if self.session:
            await self.session.close()


class Helper:

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(Helper, "_instance"):
            Helper._instance = Helper(*args, **kwargs)
        return Helper._instance

    def __init__(self, cfg, dev):
        self.loop = asyncio.get_event_loop()
        self.dev = dev
        tasks = []
        self.need_del = []
        if dev in ['all','switch']:
            self.sws = [Http(cfg.sw_user,  cfg.sw_pwd,  addr,
                            cfg.sw_restv, "switch") for addr in cfg.sw_addrs]
            tasks = [self.loop.create_task(
                sw.login_may_use_cookie()) for sw in self.sws]
        if dev in ['all', 'cpu']:
            self.cpus = [Http(cfg.cpu_user, cfg.cpu_pwd, addr,
                          cfg.cpu_restv, "cpu") for addr in cfg.cpu_addrs]
            tasks += [self.loop.create_task(cpu.login_may_use_cookie())
                    for cpu in self.cpus]
        if tasks:
            wait_login = asyncio.wait(tasks)
            self.loop.run_until_complete(wait_login)

    def load_conf(self,cfg):
        tasks = []
        old_ses = []
        if hasattr(self,'cpus'):
            old_ses += self.cpus
        if hasattr(self,'sws'):
            old_ses += self.sws
        if cfg.cpu_addrs and self.dev== 'cpu':
            addr = cfg.cpu_addrs[0]
            new_cpus =[]
            if hasattr(self,'cpus'):
                for c in self.cpus:
                    if "https://" + addr + cfg.cpu_restv in c.base_url:
                        new_cpus = [c]
                        break
            self.cpus = new_cpus
            if not self.cpus:
                self.cpus = [Http(cfg.cpu_user, cfg.cpu_pwd, addr,
                            cfg.cpu_restv, "cpu")]
                tasks += [self.loop.create_task(cpu.login_may_use_cookie())
                        for cpu in self.cpus]
        
        if cfg.sw_addrs:
            swaddr = cfg.sw_addrs[0]
            new_sws = []
            if hasattr(self,'sws'):
                for sw in self.sws:
                    if "https://" + swaddr + cfg.sw_restv in sw.base_url:
                        new_sws = [sw]
                        break
            self.sws = new_sws
            if not self.sws:
                self.sws = [Http(cfg.sw_user,  cfg.sw_pwd,  swaddr,
                                cfg.sw_restv, "switch")]
                tasks = [self.loop.create_task(
                    sw.login_may_use_cookie()) for sw in self.sws]
        if tasks:
            wait_login = asyncio.wait(tasks)
            self.loop.run_until_complete(wait_login)

        for rest in old_ses:
            used = 0
            if hasattr(self,'cpus'):
                if rest in self.cpus:
                    used = 1
            if hasattr(self,'sws'):
                if rest in self.sws:
                    used = 1
            if not used:
                self.need_del.append(rest)

    def data_from_tasks(self, tasks):
        data = []
        for task in tasks:
            try:
                data.append(task.result())
            except ClientConnectorError as e:
                data.append([111, '{0}:{1}'.format(e.host, e.port), "E(2)"])
            except Exception as e:
                data.append([111, e, "E(5)"])
        return data

    def cpu_get(self, url, data=None, params=None):
        if not self.cpus or not [cpu for cpu in self.cpus if cpu.active]:
            sprint("[CONFIG] has no active cpu rest")
            return None
        tasks = [self.loop.create_task(
            rest.get(url, data, params)) for rest in self.cpus if rest.active]
        get = asyncio.wait(tasks)
        self.loop.run_until_complete(get)
        return self.data_from_tasks(tasks)

    def cpu_get_file(self, url, filename=None, params=None):
        if not self.cpus or not [cpu for cpu in self.cpus if cpu.active]:
            sprint("[CONFIG] has no active cpu rest")
            return None
        tasks = [self.loop.create_task(
            rest.get_file(url, './cfg_saved/'+rest.addr.replace(':','_')+"_"+filename, params)) 
            for rest in self.cpus if rest.active]
        get = asyncio.wait(tasks)
        self.loop.run_until_complete(get)
        return self.data_from_tasks(tasks)

    def cpu_upload_file(self, url, filename=None, params=None):
        if not self.cpus or not [cpu for cpu in self.cpus if cpu.active]:
            sprint("[CONFIG] has no active cpu rest")
            return None
        tasks = [self.loop.create_task(
            rest.post_file(url, './cfg_saved/'+rest.addr.replace(':','_')+"_"+filename, params))
            for rest in self.cpus if rest.active]
        get = asyncio.wait(tasks)
        self.loop.run_until_complete(get)
        return self.data_from_tasks(tasks)

    def cpu_put(self, url, data=None, params=None):
        if not self.cpus or not [cpu for cpu in self.cpus if cpu.active]:
            sprint("[CONFIG] has no active cpu rest")
            return None
        tasks = [self.loop.create_task(
            rest.put(url, data, params)) for rest in self.cpus if rest.active]
        put = asyncio.wait(tasks)
        self.loop.run_until_complete(put)
        return self.data_from_tasks(tasks)

    def cpu_post(self, url, data=None, params=None):
        if not self.cpus or not [cpu for cpu in self.cpus if cpu.active]:
            sprint("[CONFIG] has no active cpu rest")
            return None
        tasks = [self.loop.create_task(
            rest.post(url, data, params)) for rest in self.cpus if rest.active]
        post = asyncio.wait(tasks)
        self.loop.run_until_complete(post)
        return self.data_from_tasks(tasks)

    def cpu_raw_post(self, url, data=None, header=None, params=None, files=None):
        if not self.cpus or not [cpu for cpu in self.cpus if cpu.active]:
            sprint("[CONFIG] has no active cpu rest")
            return None
        tasks = [self.loop.create_task(
            rest.raw_post(url, data, header, params, files)) for rest in self.cpus if rest.active]
        post = asyncio.wait(tasks)
        self.loop.run_until_complete(post)
        return self.data_from_tasks(tasks)

    def cpu_patch(self, url, data=None, params=None):
        if not self.cpus or not [cpu for cpu in self.cpus if cpu.active]:
            sprint("[CONFIG] has no active cpu rest")
            return None
        tasks = [self.loop.create_task(
            rest.patch(url, data, params)) for rest in self.cpus if rest.active]
        patch = asyncio.wait(tasks)
        self.loop.run_until_complete(patch)
        return self.data_from_tasks(tasks)

    def cpu_delete(self, url, data=None, params=None):
        if not self.cpus or not [cpu for cpu in self.cpus if cpu.active]:
            sprint("[CONFIG] has no active cpu rest")
            return None
        tasks = [self.loop.create_task(
            rest.delete(url, data, params)) for rest in self.cpus if rest.active]
        delete = asyncio.wait(tasks)
        self.loop.run_until_complete(delete)
        return self.data_from_tasks(tasks)

    def sw_get(self, url, data=None, params=None):
        if not self.sws or not [sw for sw in self.sws if sw.active]:
            sprint("[CONFIG] has no active switch rest")
            return
        tasks = [self.loop.create_task(
            rest.get(url, data, params)) for rest in self.sws if rest.active]
        get = asyncio.wait(tasks)
        self.loop.run_until_complete(get)
        return self.data_from_tasks(tasks)

    def sw_put(self, url, data=None, params=None):
        if not self.sws or not [sw for sw in self.sws if sw.active]:
            sprint("[CONFIG] has no active switch rest")
            return
        tasks = [self.loop.create_task(
            rest.put(url, data, params)) for rest in self.sws if rest.active]
        put = asyncio.wait(tasks)
        self.loop.run_until_complete(put)
        return self.data_from_tasks(tasks)

    def sw_post(self, url, data=None, params=None):
        if not self.sws or not [sw for sw in self.sws if sw.active]:
            sprint("[CONFIG] has no active switch rest")
            return
        tasks = [self.loop.create_task(
            rest.post(url, data, params)) for rest in self.sws if rest.active]
        post = asyncio.wait(tasks)
        self.loop.run_until_complete(post)
        return self.data_from_tasks(tasks)

    def sw_raw_post(self, url, data=None, header=None, params=None, files=None):
        if not self.sws or not [sw for sw in self.sws if sw.active]:
            sprint("[CONFIG] has no active switch rest")
            return
        tasks = [self.loop.create_task(
            rest.raw_post(url, data, header, params, files))
            for rest in self.sws if rest.active]
        post = asyncio.wait(tasks)
        self.loop.run_until_complete(post)
        return self.data_from_tasks(tasks)

    def sw_patch(self, url, data=None, params=None):
        if not self.sws or not [sw for sw in self.sws if sw.active]:
            sprint("[CONFIG] has no active switch rest")
            return
        tasks = [self.loop.create_task(
            rest.patch(url, data, params)) for rest in self.sws if rest.active]
        patch = asyncio.wait(tasks)
        self.loop.run_until_complete(patch)
        return self.data_from_tasks(tasks)

    def sw_delete(self, url, data=None, params=None):
        if not self.sws or not [sw for sw in self.sws if sw.active]:
            sprint("[CONFIG] has no active switch rest")
            return
        tasks = [self.loop.create_task(
            rest.delete(url, data, params)) for rest in self.sws if rest.active]
        delete = asyncio.wait(tasks)
        self.loop.run_until_complete(delete)
        return self.data_from_tasks(tasks)

    def __del__(self):
        tasks = []
        if hasattr(self,'sws'):
            tasks += [self.loop.create_task(sw.del_session()) for sw in self.sws]
        if hasattr(self, 'cpus'):
            tasks += [self.loop.create_task(cpu.del_session())
                    for cpu in self.cpus]
        tasks += [self.loop.create_task(rest.del_session())
                    for rest in self.need_del]
        if tasks:
            wait_login = asyncio.wait(tasks)
            self.loop.run_until_complete(wait_login)
        self.loop.close()
hp = None
def get_hp(dev='all'):
    global hp
    if not hp:
        hp = Helper(Config, dev)
    return hp

def set_hp(sw, cpu):
    global hp
    if cpu:
        Config.cpu_addrs = [cpu]
    if sw:
        Config.sw_addrs = [sw]
    if not hp:
        hp = Helper(Config, 'all')
    else:
        hp.load_conf(Config)

import sys
args = sys.argv[1:]
if args:
    cpu_cmd = ['acl','action','dpdk-stat','gtpu-cfg','gtpu-stat',
        'gtpv1-cfg','gtpv1-stat','gtpv2-cfg','gtpv2-stat',
        'http2-cfg','http2-stat','intf','sctp-cfg','sctp-stat',
        'sig-cfg','sig-stat','ngap-stat','pfcp-stat','pfcp-cfg'
        ]
    sw_cmd = ['acl-sw','intf-sw','policies','errpkt-permit']
    both_cmd = ['delete','get','post','patch','version','syscfg']
    other = ['dev-ip']
    if args[0] in cpu_cmd:
        hp = get_hp(dev='cpu')
    elif args[0] in sw_cmd:
        hp = get_hp(dev='switch')
    elif args[0] in both_cmd:
        hp = get_hp(dev='all')
    else:
        hp = get_hp(dev='cpu')