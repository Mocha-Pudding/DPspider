#coding:utf-8
import time
from log import getLogger
from functools import wraps
from exception import NoHomePage

logger = getLogger(__name__)

def already(func):
	def wrapper(self,*args,**kwargs):
		if kwargs.get('reget'):
			self.get(headers=self.headers,proxy=self.proxy)
		if self.homepage is None:
			raise NoHomePage(f'未先获取首页.')
		try:
			res =  func(self,*args,**kwargs)
		except Exception as e:
			logger.error(f'{e.__class__.__name__}:{e}')
			return
		else:
			return res
	return wrapper

def timer(func):
	@wraps(func)
	def wrapper(*args,**kwargs):
		start = time.time()
		res = func(*args,**kwargs)
		end = time.time()
		_ = round(end-start,2)
		logger.debug(f'{func} 耗时:{_}s')
		return res
	return wrapper
