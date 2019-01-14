#coding:utf-8

import requests
from settings import *
from config import PROVINCE_FILE_PATH,\
    CITY_DETAIL_FILE_PATH
from util.dianping import get_provinces,get_active_cities
from decorator.dianping import recover

class DianPing(object):
    """
    大众点评
    """

    _provinces = None
    _active_cities = None

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(DianPing, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.session = requests.session()

    @property
    def provinces(self):
        return self._provinces if self._provinces else self.get_provinces()

    @property
    def active_cities(self):
        return self._active_cities if self._active_cities else self.get_active_cities()

    @recover('_provinces',API_PROVINCE,PROVINCE_FILE_PATH)
    def get_provinces(self,reget=False):
        """
        获取所有省、直辖市的信息
        :param reget: 重新抓取
        """
        self._provinces = get_provinces(self.session,API_PROVINCE)
        return self._provinces

    @recover('_active_cities', API_PLACES, CITY_DETAIL_FILE_PATH)
    def get_active_cities(self,reget=False):
        """
        获取国内所有可见的地区、城市、县乡镇等的信息
        :param reget: 重新抓取
        """
        self._active_cities = get_active_cities(self.session,API_PLACES,self.provinces)
        return self._active_cities


