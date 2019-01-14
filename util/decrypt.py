#coding:utf-8
import requests
from settings import *
from util.http import send_http
from bs4 import BeautifulSoup as bs

def _clean(res_list):
    _ = []
    for i in res_list:
        if isinstance(i,str):
            _.append(i.strip('\n'))
    return ''.join(_).strip()

def _get_num_svg(url):
    resp = send_http( requests.Session(),
                      'get',
                      url,
                      retries=-1,
                      headers=CSS_HEADERS
                      )
    if resp:
        text = bs(resp[0].text, 'lxml')
        texts = text('text')
        if not texts:
            res = {}
            text_path = text('textpath')
            path = text('path')
            for _, i in enumerate(path):
                d = i['d']
                num = int(d.split(' ')[1].strip())
                string = text_path[_].text.strip()
                res[num] = string
            return res
        else:
            ys = {i['y']:i.text for i in texts if i}
            return ys

def _get_str_svg(url):
    resp = send_http( requests.Session(),
                      'get',
                      url,
                      retries=-1,
                      headers=CSS_HEADERS
                      )
    if resp:
        res = {}
        text = bs(resp[0].text,'lxml')
        text_path = text('textpath')
        if not text_path:
            texts = text('text')
            ys = {i['y']: i.text for i in texts if i}
            return ys
        else:
            path = text('path')
            for _,i in enumerate(path):
                d = i['d']
                num = int(d.split(' ')[1].strip())
                string = text_path[_].text.strip()
                res[num]=string
            return res

def _find_head(cls,tag_dict):
    for tag,_list in tag_dict.items():
        if cls.startswith(tag):
            return _list

def _find_css(cls,css_dict):
    if cls in css_dict:
        return css_dict[cls]