#coding:utf-8
import re
from settings import *
from pypinyin import pinyin,Style
from bs4 import BeautifulSoup as bs

def get_sub_tag(text,attr):
    html = bs(text, 'lxml')
    param = TAG_CLASS[attr]
    try:
        tag = html(param[0], **param[1])[0]
    except IndexError:
        return
    else:
        return tag

def get_pinyin(name):
    py = pinyin(name,style=Style.NORMAL)
    py = [i[0] for i in py]
    res = ''.join(py)
    return res

def together(*args,sep='-'):
    return sep.join([str(i) for i in args if i])

def from_pattern(pattern,text):
    res = re.findall(pattern,text)
    if res:
        return res[0]

def cookie_str_to_dict(cookie_str):
    seps = cookie_str.split(';')
    _dict = {i.split('=')[0]:i.split('=')[1] for i in seps}
    for i in _dict.items():
        yield {'name': i[0].strip(), 'value': i[1].strip()}

def time_to_date(timestamp):
    """
    时间戳转换为日期
    :param timestamp : 时间戳，int类型，如：1537535021
    :return:转换结果日期，格式： 年-月-日 时:分:秒
    """
    import time
    timearr = time.localtime(timestamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timearr)
    return  otherStyleTime