#coding:utf-8
import time
import random
import requests
from config import *
from util.tools import *
from util.comments import *
from log import getLogger
from decrypt import Decrypter
from reviews import Review
from exception import NoDatabaseFound
from decorator import already,timer
from decorator.shop import parsed_css
from decorator.comments import more_than
from util.http import send_http

logger = getLogger(__name__)

class Comments(object):
    """
    大众点评商铺点评类
    """

    api = API_REVIEWS

    def __init__(self,shopId,db=None,cookie=None):
        self.id = shopId
        self.cookie = cookie
        self.db = init_db(db)
        self.session = requests.Session()
        self.home_url = self.api.format(id=shopId,page=1)
        self.decrypter = Decrypter(shopId)
        self.homepage = None
        self.proxy = None
        self.css = None
        self.css_proxy = None
        self.decrypt_dict = None
        self.css_headers = CSS_HEADERS
        self.more_page = None
        self._headers = None

    @property
    def headers(self):
        if self._headers:
            return self._headers
        elif self.cookie:
            headers = HEADERS
            headers['Cookie'] = self.cookie
            return headers
        else:
            return LOGIN_HEADERS

    @headers.setter
    def headers(self,headers):
        self._headers = headers

    @timer
    def get(self,url=None,headers=LOGIN_HEADERS,proxy=None):
        _url = url if url else self.home_url
        result = send_http(self.session,
                           'get',
                           _url,
                           retries=MAX_RETRY,
                           headers=headers,
                           proxy=proxy,
                           timeout=TIMEOUT,
                           kind='SHOP'
                           )
        if result:
            response,self.proxy,self.headers = result
            self.homepage = response.text
            logger.info(f'成功获取店铺:{self.id} 点评相关页.')
        else:
            self.homepage = None

    @already
    def get_shop_css(self, reget=False):
        src = from_pattern(PATTERN_CSS, self.homepage)
        if src:
            url = '//'.join([CSS_URL_PREFIX, src])
            result = send_http(self.session,
                               'get',
                               url,
                               retries=MAX_RETRY,
                               headers=self.css_headers,
                               proxy=self.css_proxy,
                               timeout=TIMEOUT,
                               kind='CSS',
                               )
            if result:
                response, self.css_proxy, self.css_headers = result
                self.css = response.text
                return self.css

    @already
    def get_reviews_pages_count(self,reget=False):
        span = get_sub_tag(self.homepage,'reviews')
        count = int(from_pattern(PATTERN_NUMS,span.text).strip())
        if count==0:
            return 0
        if count > COMMENT_META_COUNT:
            next = get_sub_tag(self.homepage,'next')
            if next:
                return int(next.previous_sibling.previous_sibling.text.strip())
            else:
                return
        else:
            return 1

    @already
    @more_than(1)
    def get_reviews(self,save=True,path=None,tname=None,frompage=1,
                    count=COMMENTS_RESULTS,write_mode='a',
                    reget=False):

        def save_page_reviews(reviews,total=0):
            for review in reviews:
                res.append(review)
                if save:
                    if self.db:
                        review.save(db=self.db,tname=tname)
                    else:
                        raise NoDatabaseFound('未找到对应点评存储数据库')
                elif path:
                    review.write(path=path, mode=write_mode)
                total += 1
                if total >= count and count > 0:
                    logger.info(f'爬取存储{count}条店铺:{self.id}的点评数据 任务完成.已存储:{total}')
                    return
            return total

        res = []
        total = 0
        tname = tname if tname else self.db.table
        if frompage==1:
            reviews = self.get_cur_page_reviews()
            total = save_page_reviews(reviews)
            start = 2
        elif frompage >= 1 and frompage < self.more_page:
            start = frompage
        elif frompage > self.more_page:
            logger.error(f'[超过上限-{frompage}]当前商铺：{self.id}总点评页数只有 {self.more_page} 页.')
            return
        else:
            raise TypeError(f'非法页数类型：{frompage},页数应>=1')
        if self.more_page > 1:
            logger.info(f'店铺：{self.id} 点评数据有 {self.more_page} 页.')
            for i in range(start,self.more_page+1):
                url = self.api.format(id=self.id,page=i)
                self.get(url,headers=self.headers,proxy=self.proxy)
                if self.homepage:
                    logger.info(f'[获取] 店铺：{self.id} 点评 第{i}页.')
                    reviews = self.get_cur_page_reviews()
                    total = save_page_reviews(reviews,total)
                    if total is None:
                        return
                    time.sleep(random.uniform(*COMMENTS_SLEEP))
                else:
                    continue
            logger.info(f'店铺：{self.id} 此次运行点评数据爬取至最后一页完毕，页数:{self.more_page-frompage+1},此次爬取:{total}')
        return res

    def get_single_page_reviews(self,page,save=False,tname=None,path=None,mode='a'):
        url = self.api.format(id=self.id,page=page)
        tname = tname if tname else self.db.table
        self.get(url)
        reviews = self.get_cur_page_reviews()
        for i in reviews:
            if save and self.db:
                i.save(self.db,tname)
            elif path:
                i.write(path,mode)
        return reviews

    @already
    def get_cur_page_reviews(self,reget=False):
        res = []
        div = get_sub_tag(self.homepage, 'review_items')
        if div:
            lis = div(not_has_class_li)
            for li in lis:
                review = self._parse_review(li)
                res.append(review)
        return res

    @already
    @parsed_css
    def _parse_review(self,li):
        _user_info = li('div', class_='dper-info')[0]
        _user_rank = li('div', class_='review-rank')[0]
        _user_words = li('div', class_='review-words')[0]
        _reply = li('a',class_='reply')[0]
        _review_pic_li = li('div', class_='review-pictures')
        _review_pics = _review_pic_li[0] if _review_pic_li else None
        _review_info = li('div',class_='misc-info')[0]
        _score = _user_rank('span',class_='item')
        _actions = _review_info('span',class_='actions')[0]
        _actions_a = _actions('a')
        actions = {}
        imgs = []
        user_img = li.img['data-lazyload'].split('%')[0]
        #有可能是匿名用户
        user_url = HOST + li.a['href'].strip() if li.a.has_attr('href') else None
        user_id = li.a['data-user-id']
        user_name = _user_info.a.text.strip()
        user_level = from_pattern(PATTERN_USER_LEVEL,_user_info.img['src']) if _user_info.img else None
        use_vip = True if _user_info.span and _user_info.span['class'][0]=='vip' else False
        star = from_pattern(PATTERN_STAR,''.join(_user_rank.span['class']))
        score = {i.text.strip().split('：')[0]:i.text.strip().split('：')[1] for i in _score}
        review_time = _review_info.span.text.strip()
        review_shop = _review_info('span',class_='shop')[0].text
        review_shop_id = self.id
        review_id = _reply['data-id']
        review_url = 'http:'+_reply['href']
        for a in _actions_a:
            action_name = a.text.strip()
            _next = a.next_sibling.next_sibling
            if _next and _next.name=='em':
                num = from_pattern(PATTERN_NUMS,_next.text)
                actions[action_name]=num
        if _review_pics:
            for pic in _review_pics('img'):
                imgs.append(pic['data-big'])
        words = self.decrypter.decrypt(_user_words,*self.decrypt_dict,comment=True)
        review =  Review(user_name,user_id,user_url,user_img,user_level,use_vip,
                         star,score,review_id,review_url,review_time,review_shop,
                         review_shop_id,imgs,words,actions
                         )
        return review

    @already
    @parsed_css
    def decrypt_tag(self,tag_soup,pattern='.*',is_comment=False):
        text = self.decrypter.decrypt(tag_soup,*self.decrypt_dict,
                                      comment=is_comment,pattern=pattern)
        return text


