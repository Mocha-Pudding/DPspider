#coding:utf-8
import re
import os
import copy
import time
import random
import threading
from config import *
from settings import *
from decorator import timer
from log import getLogger
from util.thread import CrawlThread
from w3lib.url import is_url
from util.proxy import get_proxy,gen_proxy
from exception import ForbiddenProxy
from bs4 import BeautifulSoup as bs

logger = getLogger(__name__)

@timer
def send_http(session,method,url,*,
                             retries=1,
                             interval=INTERVAL,
                             proxy = None,
                             timeout=None,
                             kind=None,
                             success_callback=None,
                             fail_callback=None,
                             headers=None,
                             **kwargs):
    forbiddens = 0
    fails = 0
    _404 = 0
    _ua = copy.deepcopy(USER_AGENTS)
    if method.lower() not in HTTP_METHODS:
        return
    if retries == -1:
        attempt = -1
    elif retries == 0:
        attempt = 1
    else:
        attempt = retries + 1
    logger.debug(f'当前请求[{kind}]:{url}')
    while attempt != 0:
        try:
            try:
                response = getattr(session,method.lower())(url,
                                                           timeout=timeout,
                                                           proxies=proxy,
                                                           headers=headers,
                                                           **kwargs)
            except Exception as e:
                logger.debug(f'[请求异常-代理:{proxy}] {e.__class__.__name__}:{e}')
                fails+=1
                if PROXY_ENABLE:
                    proxy = get_proxy()
                raise e
            code = response.status_code
            if code == 404:
                if _404 > NOT_FOUND_MAX_TO_DROP:
                    break
                _404 += 1
            if code in FORBIDDEN_CODE or \
                    should_verify(response) or \
                    fake_detail_response(response,kind)  or \
                    fake_pages_response(response,kind) or \
                    fake_css_response(response,kind) or \
                    fake_city_response(response,kind) or \
                    fake_json_response(response,kind) or \
                    fake_map_response(response,kind) or \
                    fake_city_list_response(response, kind):
                fails+=1
                logger.debug(f'[无效代理-{code}] {proxy} 请求无效.{headers["User-Agent"]}')
                if code in FORBIDDEN_CODE:
                    forbiddens+=1
                if not _ua:
                    _ua = copy.deepcopy(USER_AGENTS)
                if forbiddens > FORBIDDEN_MAX_TO_CHANGE and _ua:
                    headers['User-Agent'] = _ua.pop(random.choice([i for i in range(len(_ua))]))
                    # forbiddens = 0
                    logger.debug(f'切换UA:{headers["User-Agent"]}')
                if fails > FAIL_MAX_TO_DROP:
                    break
                if PROXY_ENABLE:
                    proxy = get_proxy()
                raise ForbiddenProxy
            if success_callback:
                success_callback(response)
            logger.debug(f'请求成功:[代理:{proxy},UA:{headers["User-Agent"]}]')
            return response,proxy,headers
        except:
            if RANDOM_SLEEP:
                time.sleep(random.uniform(*RANDOM_INTERVAL))
            else:
                time.sleep(interval)
        attempt-=1
    if fail_callback:
        fail_callback()
    tries = fails if retries<0 else retries
    logger.warn(f'[失败-{code}] 重试抓取{url} {tries} 次后失败.')

def should_verify(resp):
    try:
        a = resp.json()
        if a['customData']['verifyUrl']:
            return True
    except:
        return False

def fake_detail_response(resp,kind):
    html = bs(resp.text, 'lxml')
    if not html('h1', class_='shop-name') and kind=='SHOP':
        return True

def fake_pages_response(resp,kind):
    html = bs(resp.text, 'lxml')
    if not html('div', class_='tit') and kind=='PAGE':
        return True

def fake_css_response(resp,kind):
    a = re.findall(PATTERN_BACKGROUND, resp.text)
    if not a and kind=='CSS' :
        return True

def fake_city_response(resp,kind):
    html = bs(resp.text,'lxml')
    if not html('ul',class_='first-cate') and kind=='CITY':
        return True

def fake_city_list_response(resp,kind):
    html = bs(resp.text,'lxml')
    if not html('div',class_='main-citylist') and kind=='CITY_LIST':
        return True

def fake_json_response(resp,kind):
    if kind == 'JSON':
        try:
            res = resp.json()
        except:
            return True

def fake_map_response(resp,kind):
    html = bs(resp.text, 'lxml')
    if not html('div', class_='screen-filter') and kind == 'MAP':
        return True

def fetch(session,url,ip,fobj,lock,headers=HEADERS):
    try:
        resp = session.get(url,
            timeout=TIMEOUT,
            proxies = gen_proxy(ip),
           headers=headers)
    except:
        return
    if resp.status_code not in FORBIDDEN_CODE and not should_verify(resp):
        print(f'* [{resp.status_code}]找到可用代理IP:{ip}')
        lock.acquire()
        fobj.write(ip)
        lock.release()
        return 1

def test_proxy_pool(self,url):
    if not PROXY:
        if is_url(PROXY_POOL):
            return
        if PROXY_POOL_RAW and \
            os.path.isfile(PROXY_POOL_RAW):
            with open(PROXY_POOL_RAW, 'r') as f:
                p = f.readlines()
            fobj = open(PROXY_POOL,'a')
            print(f'* 配置中使用了文本代理IP池,开始检测所有代理IP.测试url:{url}')
            print(f'* 文本IP代理池中共有代理IP:{len(p)}')
            _ = 0
            lock = threading.Lock()
            while p:
                ps = [p.pop(0) for i in range(min(PROXY_TEST_MAX, len(p)))]
                print(f'* 检测条数:{len(ps)},文本IP代理池中剩余代理IP:{len(p)}')
                ts = []
                for i in ps:
                    a = CrawlThread(fetch, args=(self.session,url, i,fobj,lock))
                    ts.append(a)
                for i in ts:
                    i.start()
                for i in ts:
                    i.join()
                    if i.get_result():
                        _+=1
            fobj.close()
            print(f'>> 所有代理检测完成.共有{_}个.')