#coding:utf-8
import os
import json
from config import *
from settings import API_CITY_LIST
from util.city import get_city_list
from exception import NoCityList,NoCityId

def recover(path):
    def outwrapper(func):
        def wrapper(self,*args,**kwargs):
            if kwargs.get('reget'):
                self.get_map(self.headers, self.proxy)
                return func(self,*args,**kwargs)
            res = None
            if os.path.isfile(path):
                with open(path, 'r') as f:
                    b = f.read()
                res = json.loads(b)
                cate = res.get(self.city)
                if cate:
                    return cate
            _res = func(self,*args,**kwargs)
            if path:
                if _res:
                    if res:
                        res.update({self.city:_res})
                    else:
                        res = {self.city:_res}
                    with open(path, 'w') as f:
                        f.write(json.dumps(res))
            return _res
        return wrapper
    return outwrapper

def map_required(func):
    def wrapper(self, *args, **kwargs):
        while not self.map_page:
            self.get_map(self.headers,self.proxy)
        return func(self, *args, **kwargs)
    return wrapper

def has_id(func):
    def wrapper(self, *args, **kwargs):
        if self.id:
            return func(self,*args,**kwargs)
        raise NoCityId(f'未获取城市 "{self.city}" ID.')
    return wrapper

def has_city_list(func):
    def wrapper(self, *args, **kwargs):
        if kwargs.get('reget') or not os.path.isfile(CITY_LIST_FILE_PATH) :
            self.city_list = get_city_list(API_CITY_LIST,
                                          self.headers,
                                          self.proxy)
            if self.city_list:
                return func(self,*args,**kwargs)
            raise NoCityList('未能获取到全国激活城市列表.')
        else:
            with open(CITY_LIST_FILE_PATH,'r') as f:
                b = f.read()
            self.city_list = json.loads(b)
        return func(self,*args,**kwargs)
    return wrapper