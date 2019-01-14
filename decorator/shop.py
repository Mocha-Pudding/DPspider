#coding:utf-8

from exception import NoCSStoDecrypt
from util.shop import parse_shop_css


def parsed_css(func):
	def wrapper(self,*args,**kwargs):
		if self.decrypt_dict:
			return func(self,*args,**kwargs)
		elif self.css:
			self.decrypt_dict = parse_shop_css(self.css)
		else:
			css = self.get_shop_css()
			if css:
				self.decrypt_dict = parse_shop_css(self.css)
			else:
				raise NoCSStoDecrypt('未获取到解析字体加密相关的CSS文件.')
		return func(self,*args,**kwargs)
	return wrapper
