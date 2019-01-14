#coding:utf-8
import json
import requests
import dianping
from settings import *
from config import *
from shop import Shop
from decorator import timer
from log import getLogger
from util.tools import from_pattern
from exception import NoTextFiled
from util.tools import get_sub_tag
from util.http import send_http

logger = getLogger(__name__)

def init_db(db):
    if db and not db.connected:
        db.connect()
    return db

def init_search_db(db):
    if db and not db.connected:
        db.connect()
        db.use_db(MongoDB['searchDB'])
    return db

def get_city_list(url,headers=HEADERS,proxy=None):
    result = send_http(requests.session(),
                       'get',
                       url,
                       retries=-1,
                       proxy=proxy,
                       headers=headers,
                       timeout=TIMEOUT,
                       kind='CITY_LIST',
                       )
    if result:
        text = result[0].text
        ul = get_sub_tag(text,'city_list')
        if ul:
            with open(CITY_LIST_FILE_PATH,'w') as f:
                res = {}
                lis = ul('li')
                for li in lis:
                    _as = li('a')
                    for a in _as:
                        res[a.text] = CITY_URL_PREFIX+a['href']
                f.write(json.dumps(res))
            return res

def get_city_areacode(cityId=None,cityName=None):
    active_cities = dianping.DianPing().active_cities
    for city in active_cities:
        if cityId and str(cityId)==str(city['cityId']):
            return city['cityAreaCode']
        if cityName and city['cityName'].startswith(cityName):
            return city['cityAreaCode']
    logger.debug(f'未找到 Name:{cityName} ID:{cityId} 城市区号.')
    return ''

@timer
def get_city_shop_info(shopId,cityId,proxy,headers):
    shop = Shop(shopId)
    shop.get(proxy=proxy,headers=headers)
    if not shop._fetched:
        return
    data = {
        '地址':shop.address,
        '点评数':shop.reviews,
        '点评标签':shop.review_tags,
        '电话':get_full_phone(shop.phone,cityId),
        '点评类别':shop.comment_kinds,
        '评分':shop.scores
    }
    return data,shop.proxy,shop.headers

def get_full_phone(phone_str,cityId):
    if not phone_str:
        return
    res = []
    _phone =[i.strip() for i in  phone_str.split('\xa0') if i]
    for i in _phone:
        if from_pattern(PATTERN_PHONE,i):
            res.append(i)
        else:
            code = get_city_areacode(cityId)
            res.append('-'.join([code,i]))
    return res

def post_data(cityId,cityName,keyword,page,shopType,categoryId,regionId,mode,sortId,filterId):
    data = {
        "cityId": cityId,
        "cityEnName": cityName,
        "promoId": "0",
        "shopType": shopType,
        "categoryId": categoryId,
        "regionId": regionId,
        "sortMode": mode,
        "shopSortItem": sortId,
        "keyword": keyword,
        "searchType": "2",
        "branchGroupId": "0",
        "aroundShopId": "0",
        "shippingTypeFilterValue": filterId,
        "page": str(page)
    }
    return data

def transfer_data(item,locations):
    regions = [find_region_by_id(i,locations) for i in item['regionList']]
    data = {
        '店名':item['shopName'],
        '星级':item['shopPowerTitle'],
        '注册时间':item['addDate'],
        '地址':item['address'],
        '人均':item['avgPrice'],
        '预订': item['bookingSetting'],
        '分店url': HOST+item['branchUrl'],
        '商铺图片': item['defaultPic'],
        '商铺标签': item['dishTag'],
        '纬度': item['geoLat'],
        '经度': item['geoLng'],
        '电话':item['phoneNo'],
        '店铺ID':item['shopId'],
        '会员卡ID': item['memberCardId'],
        '地区':regions,
        'expand':item['expand'],
        'poi':item['poi'],
        'promoId':item['promoId'],
        'shopDealId':item['shopDealId'],
        'shopPower':item['shopPower'],
        'hasSceneryOrder': item['hasSceneryOrder'],
    }
    return data

def find_id(key,key_dict_list):
    def get_id(key,key_dict_list,parent=None):
        p = c = None
        if key is None:
            return '0','0'
        for item in key_dict_list:
            if item['text'] == key :
                _res = item['value']
                if not parent:
                    return _res,_res
            if item.get('children'):
                pid = item['value']
                _,c = get_id(key,item['children'])
                if c:
                    return pid,c
        return p,c
    _id = get_id(key,key_dict_list)
    if _id == (None,None):
        raise NoTextFiled(f'未找到 "{key}" 相关字段.')
    return _id

def find_sort_value(key,category_id,sort_dict):
    if category_id in sort_dict:
        if not key:
            return '2','0'
        item = sort_dict[category_id]
        for i in item:
            if i['text']==key:
                return i['mode'],i['sort']
    raise NoTextFiled(f'未找到 "{key}" 排序项.')

def find_filter_value(key):
    value =  SEARCH_MAP_FILTERS.get(key)
    return value if value else '0'

def find_region_by_id(id,key_dict_list):
    for item in key_dict_list:
        if item['value']==str(id):
            return item['text']
        elif item.get('children') != None:
            res = find_region_by_id(id,item.get('children'))
            if res:
                return res


def find_children_regions(id,key_dict_list,first=True):
    found = False
    for item in key_dict_list:
        if item['value']==str(id):
            found = True
            if item.get('children'):
                return [i['value'] for i in item['children']]
            else:
                return False
        elif item.get('children'):
            res = find_children_regions(id,item.get('children'),False)
            if not res is None:
                return res
    if not found and first:
        return [i['value'] for i in key_dict_list if i['value']!=0]

