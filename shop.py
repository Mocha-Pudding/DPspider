#coding:utf-8

import requests
from config import *
from util.tools import *
from log import getLogger
from util.http import send_http
from decorator import already,timer
from decorator.shop import parsed_css

logger = getLogger(__name__)

class Shop(object):
	"""
	大众点评商铺
	"""
	api = API_SHOP

	def __init__(self,shopId):
		self.id = shopId
		self.headers = HEADERS
		self.css_headers = CSS_HEADERS
		self.session = requests.session()
		self.url = self.api.format(id=shopId)
		self.homepage = None
		self._fetched = False
		self.css = None
		self.proxy = None
		self.css_proxy = None
		self.decrypt_dict = None
		self._info = None
		self._name = None
		self._tags = None
		self._phone = None
		self._stars = None
		self._scores = None
		self._branch = None
		self._average = None
		self._reviews = None
		self._address = None
		self._abstract = None
		self._licenses = None
		self._comments = None
		self._recommend = None
		self._promotions = None
		self._price_photos = None
		self._review_tags = None
		self._comment_kinds = None
		self._business_hours = None
		self._official_photos = None
		self.__environment_photos = None

	@timer
	def get(self,headers=HEADERS,proxy=None):
		result = send_http(self.session,
						 'get',
						 self.url,
						 retries=MAX_RETRY,
						 headers=headers,
						 proxy=proxy,
						 timeout=TIMEOUT,
						 kind='SHOP',
						 )
		if result:
			response, self.proxy, self.headers = result
			self.homepage = response.text
			self._fetched = True
			logger.info(f'成功获取店铺:{self.id} 首页.')

	@property
	def name(self):
		return self._name if self._name else self.get_name()

	@property
	def stars(self):
		return self._stars if self._stars else self.get_stars()

	@property
	def scores(self):
		return self._scores if self._scores else self.get_scores()

	@property
	def average(self):
		return self._average if self._average else self.get_average()

	@property
	def reviews(self):
		return self._reviews if self._reviews else self.get_reviews()

	@property
	def address(self):
		return self._address if self._address else self.get_address()

	@property
	def phone(self):
		return self._phone if self._phone else self.get_phone()

	@property
	def comment_kinds(self):
		return self._comment_kinds if self._comment_kinds else self.get_comment_kinds()

	@property
	def review_tags(self):
		return self._review_tags if self._review_tags else self.get_review_tags()

	@already
	def get_all_infos(self,reget=False):
		pass

	@already	
	def get_name(self,reget=False):
		h1 = get_sub_tag(self.homepage,'name')
		if h1('a'):
			[i.extract() for i in h1('a')]
		self._name = h1.text.strip()
		return self._name

	@already
	def get_stars(self,reget=False):
		span = get_sub_tag(self.homepage,'stars')
		self._stars = from_pattern(PATTERN_STAR,''.join(span['class'])) if span else None
		return self._stars

	@already
	def get_scores(self,reget=False):
		span = get_sub_tag(self.homepage,'scores')
		res = {}
		if span:
			for _span in span('span'):
				name,score = _span.text.split('：')
				res[name]=score
		self._scores = res
		return self._scores

	@already
	def get_average(self,reget=False):
		span = get_sub_tag(self.homepage,'average')
		self._average = from_pattern(PATTERN_NUMS,span.text) if span else 0
		return self._average

	@already
	def get_reviews(self,reget=False):
		span = get_sub_tag(self.homepage,'reviews')
		self._reviews = from_pattern(PATTERN_NUMS,span.text) if span else 0
		return self._reviews

	@already
	def get_address(self,reget=False):
		span = get_sub_tag(self.homepage, 'address')
		self._address = re.sub('[地址: ：\n]','',span.text) if span else None
		return self._address

	@already
	def get_phone(self,reget=False):
		span = get_sub_tag(self.homepage,'phone')
		self._phone = re.sub('[电话: ：\n]','',span.text) if span else None
		return self._phone

	@already
	def get_comment_kinds(self,reget=False):
		div = get_sub_tag(self.homepage,'comment_kinds')
		labels = div('label')[1:] if div else []
		res = {}
		for label in labels:
			if label.span:
				count = from_pattern(PATTERN_NUMS,label.span.text)
				label.span.extract()
				name = re.sub('[\n ]','',label.text)
				res[name]=count
		self._comment_kinds = res
		return self._comment_kinds

	@already
	def get_review_tags(self,reget=False):
		div = get_sub_tag(self.homepage,'review_tags')
		_div = div('div',class_='content') if div else None
		res = []
		if _div:
			for span in _div[0]('span'):
				res.append(re.sub('[\n ]','',span.text))
			self._review_tags = res
			return self._review_tags

	@already
	def get_business_hours(self, reget=False):
		pass

	@already
	def get_abstract(self,reget=False):
		pass

	@already
	def get_branch(self, reget=False):
		pass

	@already
	def get_licenses(self,reget=False):
		pass

	@already
	def get_recommend(self,reget=False):
		pass

	@already
	def get_official_photos(self,reget=False):
		pass

	@already
	def get_price_photos(self,reget=False):
		pass

	@already
	def get_environment_photos(self,reget=False):
		pass

	@already
	def get_promotions(self,reget=False):
		pass

	@already
	def get_shop_css(self, reget=False):
		src = from_pattern(PATTERN_CSS,self.homepage)
		if src:
			url = '//'.join([CSS_URL_PREFIX,src])
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
	def get_tags(self,with_count=True,reget=False):
		pass

