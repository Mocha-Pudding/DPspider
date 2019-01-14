#coding:utf-8

import re
from settings import *

def parse_shop_css(css):
    cls_dict = {}
    css_dict = {}
    backgrounds = re.findall(PATTERN_BACKGROUND,css)
    spans = re.findall(PATTERN_SPAN_CLASS,css)
    for i in spans:
        cls_dict.update({i[0]:[int(i[1].strip()),CSS_URL_PREFIX+i[2]]})
    for i in backgrounds:
        css_dict[i[0]]={
            'x':-float(i[1].strip()),
            'y':-float(i[-1].strip()),
        }
    return cls_dict,css_dict