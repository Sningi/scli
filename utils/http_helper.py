import os
import time
import asyncio
import aiohttp
from json import dumps
from aiohttp import TCPConnector
from click.types import File
from utils.http_code import HTTP
from config import Config


def SCLI_HTTP_REQUEST(cls_func):
    """this Decorators may need not"""
    def wrapper(self, *args, **kwargs):
        try:
            return cls_func(self, *args, **kwargs)
        except Exception as e:
            if type(e) in aiohttp.http_exceptions.__all__:
                return [111, self.addr, "connect error"]
            if type(e).__name__ == "JSONDecodeError":
                return [self.response.status, self.addr, self.response.text]
            else:
                return [type(e).__name__, self.addr, "other error!!"]
    return wrapper


class Http:
    timeout = 30

    def __init__(self, uname, pwd, addr, restv, dev_rest_type="switch"):
        self.addr = addr
        self.base_url = "https://" + addr + restv
        if dev_rest_type == "cpu":
            """cpu"""
            self.auth = {'username': uname, 'password': pwd}
            self.login_url = "https://" + addr + restv + "login"
        else:
            """sw"""
            self.auth = dumps({'username': uname, 'password': pwd})
            self.login_url = "https://" + addr + "/login"
        self.session = None
        # ret = asyncio.run(self.login_may_use_cookie())
        # if ret not in [HTTP.OK, HTTP.CREATED]:
        #     pass
        #     print("{0} login failed ".format(self.addr), ret)

    # diff_time 2h-10s
    async def login_may_use_cookie(self, clear_cookie=False, diff_time=7190):

        cookie = "/tmp/cookie_"+self.addr.replace(":", "_")
        jar = aiohttp.CookieJar(unsafe=True)
        with_cookie = False

        async def login():
            try:
                async with self.session.post(self.login_url, timeout=self.timeout, data=self.auth) as res:
                    await res.read()
                    code = res.status
                    if code in [HTTP.OK, HTTP.CREATED]:
                        self.session.cookie_jar.save(cookie)
                    return code
            except Exception as e:
                print("ERROR: login {0} failed:".format(self.addr), e)

        if clear_cookie:
            # await self.del_session()
            if os.path.isfile(cookie):
                #cookie is invalid
                os.remove(cookie)

        if os.path.isfile(cookie) and time.time() - os.path.getmtime(cookie) < 7190:
            jar.load(cookie)
            with_cookie = True
        if not clear_cookie:
            self.session = aiohttp.ClientSession(
                connector=TCPConnector(ssl=False), cookie_jar=jar)

        if not with_cookie:
            return await login()
        else:
            return HTTP.OK

    # @SCLI_HTTP_REQUEST
    async def get(self, short_url, data=None, params=None, loop=0):
        loop += 1
        if loop > 5:
            return [400, self.addr, "login failed may error passwd or error date"]
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
        if loop > 5:
            return [400, self.addr, "login failed may error passwd or error date"]
        async with self.session.get(url=self.base_url + short_url, params=params, timeout=self.timeout) as res:
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

    # @SCLI_HTTP_REQUEST
    async def post(self, short_url, data, params=None, loop=0):
        loop += 1
        if loop > 5:
            return [400, self.addr, "login failed may error passwd or error date"]
        async with self.session.post(url=self.base_url + short_url, json=data, params=params, timeout=self.timeout) as res:
            data = await res.text()
            if res.status == HTTP.UNAUTHORIZED:
                await self.login_may_use_cookie(clear_cookie=True)
                return await self.post(short_url, data, params, loop=loop)
            return [res.status, self.addr, data]

    # @SCLI_HTTP_REQUEST
    async def post_file(self, short_url, filename=None,  params=None, loop=4):
        loop += 1
        if loop > 5:
            return [400, self.addr, "login failed may error passwd or error date"]
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

    # @SCLI_HTTP_REQUEST
    async def delete(self, short_url, data=None, params=None, loop=0):
        loop += 1
        if loop > 5:
            return [400, self.addr, "login failed may error passwd or error date"]
        async with self.session.delete(url=self.base_url+short_url, params=params, timeout=self.timeout) as res:
            data = await res.text()
            if res.status == HTTP.UNAUTHORIZED:
                await self.login_may_use_cookie(clear_cookie=True)
                return await self.delete(short_url, data, params, loop=loop)
        return [res.status, self.addr, data]

    # @SCLI_HTTP_REQUEST
    async def put(self, short_url, data, params=None, loop=0):
        loop += 1
        if loop > 5:
            return [400, self.addr, "login failed may error passwd or error date"]
        async with self.session.put(url=self.base_url+short_url, json=data, params=params, timeout=self.timeout) as res:
            data = await res.text()
            if res.status == HTTP.UNAUTHORIZED:
                await self.login_may_use_cookie(clear_cookie=True)
                return await self.put(short_url, data, params, loop=loop)
            return [res.status, self.addr, data]

    # @SCLI_HTTP_REQUEST
    async def patch(self, short_url, data, params=None, loop=0):
        loop += 1
        if loop > 5:
            return [400, self.addr, "login failed may error passwd or error date"]
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

    def __init__(self, cfg):
        self.sws = [Http(cfg.sw_user,  cfg.sw_pwd,  addr,
                         cfg.sw_restv, "switch") for addr in cfg.sw_addrs]
        self.cpus = [Http(cfg.cpu_user, cfg.cpu_pwd, addr,
                          cfg.cpu_restv, "cpu") for addr in cfg.cpu_addrs]
        self.loop = asyncio.get_event_loop()
        tasks = [self.loop.create_task(
            sw.login_may_use_cookie()) for sw in self.sws]
        tasks += [self.loop.create_task(cpu.login_may_use_cookie())
                  for cpu in self.cpus]
        wait_login = asyncio.wait(tasks)
        self.loop.run_until_complete(wait_login)


    def data_from_tasks(self, tasks):
        data = []
        for task in tasks:
            try:
                data.append(task.result())
            except aiohttp.client_exceptions.ClientConnectorError as e:
                data.append([111, '{0}:{1}'.format(e.host, e.port), "connect error"])
            except Exception as e:
                print('error:',e)
                data.append([111, 'unknown addr', "connect error"])
        return data

    def cpu_get(self, url, data=None, params=None):
        if not self.cpus:
            return None
        tasks = [self.loop.create_task(
            rest.get(url, data, params)) for rest in self.cpus]
        get = asyncio.wait(tasks)
        self.loop.run_until_complete(get)
        return self.data_from_tasks(tasks)

    def cpu_get_file(self, url, filename=None, params=None):
        if not self.cpus:
            return None
        tasks = [self.loop.create_task(
            rest.get_file(url, './syscfgf/'+rest.addr.replace(':','_')+"_"+filename, params)) for rest in self.cpus]
        get = asyncio.wait(tasks)
        self.loop.run_until_complete(get)
        return self.data_from_tasks(tasks)

    def cpu_upload_file(self, url, filename=None, params=None):
        if not self.cpus:
            return None
        tasks = [self.loop.create_task(
            rest.post_file(url, './syscfgf/'+rest.addr.replace(':','_')+"_"+filename, params)) for rest in self.cpus]
        get = asyncio.wait(tasks)
        self.loop.run_until_complete(get)
        return self.data_from_tasks(tasks)

    def cpu_put(self, url, data=None, params=None):
        if not self.cpus:
            return None
        tasks = [self.loop.create_task(
            rest.put(url, data, params)) for rest in self.cpus]
        put = asyncio.wait(tasks)
        self.loop.run_until_complete(put)
        return self.data_from_tasks(tasks)

    def cpu_post(self, url, data=None, params=None):
        if not self.cpus:
            return None
        tasks = [self.loop.create_task(
            rest.post(url, data, params)) for rest in self.cpus]
        post = asyncio.wait(tasks)
        self.loop.run_until_complete(post)
        return self.data_from_tasks(tasks)

    def cpu_raw_post(self, url, data=None, header=None, params=None, files=None):
        if not self.cpus:
            return None
        tasks = [self.loop.create_task(
            rest.raw_post(url, data, header, params, files)) for rest in self.cpus]
        post = asyncio.wait(tasks)
        self.loop.run_until_complete(post)
        return self.data_from_tasks(tasks)

    def cpu_patch(self, url, data=None, params=None):
        if not self.cpus:
            return None
        tasks = [self.loop.create_task(
            rest.patch(url, data, params)) for rest in self.cpus]
        patch = asyncio.wait(tasks)
        self.loop.run_until_complete(patch)
        return self.data_from_tasks(tasks)

    def cpu_delete(self, url, data=None, params=None):
        if not self.cpus:
            return None
        tasks = [self.loop.create_task(
            rest.delete(url, data, params)) for rest in self.cpus]
        delete = asyncio.wait(tasks)
        self.loop.run_until_complete(delete)
        return self.data_from_tasks(tasks)

    def sw_get(self, url, data=None, params=None):
        if not self.sws:
            return []
        tasks = [self.loop.create_task(
            rest.get(url, data, params)) for rest in self.sws]
        get = asyncio.wait(tasks)
        self.loop.run_until_complete(get)
        return self.data_from_tasks(tasks)

    def sw_put(self, url, data=None, params=None):
        if not self.sws:
            return []
        tasks = [self.loop.create_task(
            rest.put(url, data, params)) for rest in self.sws]
        put = asyncio.wait(tasks)
        self.loop.run_until_complete(put)
        return self.data_from_tasks(tasks)

    def sw_post(self, url, data=None, params=None):
        if not self.sws:
            return []
        tasks = [self.loop.create_task(
            rest.post(url, data, params)) for rest in self.sws]
        post = asyncio.wait(tasks)
        self.loop.run_until_complete(post)
        return self.data_from_tasks(tasks)

    def sw_raw_post(self, url, data=None, header=None, params=None, files=None):
        if not self.sws:
            return []
        tasks = [self.loop.create_task(
            rest.raw_post(url, data, header, params, files)) for rest in self.sws]
        post = asyncio.wait(tasks)
        self.loop.run_until_complete(post)
        return self.data_from_tasks(tasks)

    def sw_patch(self, url, data=None, params=None):
        if not self.sws:
            return []
        tasks = [self.loop.create_task(
            rest.patch(url, data, params)) for rest in self.sws]
        patch = asyncio.wait(tasks)
        self.loop.run_until_complete(patch)
        return self.data_from_tasks(tasks)

    def sw_delete(self, url, data=None, params=None):
        if not self.sws:
            return []
        tasks = [self.loop.create_task(
            rest.delete(url, data, params)) for rest in self.sws]
        delete = asyncio.wait(tasks)
        self.loop.run_until_complete(delete)
        return self.data_from_tasks(tasks)

    def __del__(self):
        tasks = [self.loop.create_task(sw.del_session()) for sw in self.sws]
        tasks += [self.loop.create_task(cpu.del_session())
                  for cpu in self.cpus]
        wait_login = asyncio.wait(tasks)
        self.loop.run_until_complete(wait_login)
        self.loop.close()


hp = Helper(Config)
