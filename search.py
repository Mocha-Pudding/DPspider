#coding:utf-8

from util.city import *
from util.tools import together
class Search(object):
    """
    城市店铺搜索
    """

    def __init__(self,cityName,keyword,
                 categories,locations,sorts,
                 category=None,location=None,
                 sort=None,filter=None,count=-1):
        self.city = cityName
        self.keyword = keyword
        self.shopType, self.category_id = find_id(category, categories)
        _, self.region_id = find_id(location, locations)
        self.mode, self.sort_id = find_sort_value(sort, self.shopType,sorts)
        self.filter_id = find_filter_value(filter)
        flag = '全' if count < 0 else str(count)
        self.tname = together(cityName, location, category, filter, keyword, flag)

    def get_map_post_data(self,cityId,cityEnName,page,regionId=None):
        region_id = regionId if regionId else self.region_id
        return post_data(cityId,cityEnName,self.keyword,page,self.shopType,
                         self.category_id,region_id,self.mode,self.sort_id,self.filter_id)

