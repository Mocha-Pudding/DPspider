#coding:utf-8

from settings import CITY_POST_HEADER

def get_provinces(session,url):
    data = session.post(url)
    p_list = data.json()['provinceList']
    res = {i['provinceName']: {'areaId': i['areaId'],
                            'provinceId': i['provinceId']} for i in p_list}
    return res

def get_active_cities(session,url,provinces,headers=CITY_POST_HEADER):
    provinces_ids = [i['provinceId'] for i in provinces.values()]
    data = []
    for i in provinces_ids:
        res = session.post(url,headers=headers,json={'provinceId':i})
        _data = res.json()['cityList']
        data.extend(_data)
    return data
