#coding:utf-8

class LoginError(Exception):
	"""
	用户登录失败或异常
	"""

class NoHomePage(Exception):
	"""
	需要先获取商铺首页内容
	"""

class ForbiddenProxy(Exception):
	"""
	无效代理
	"""

class NoCSStoDecrypt(Exception):
	"""
	没有获取到解析字体加密相关的css文件
	"""

class NoCityId(Exception):
    """
    没有获取到城市Id
    """

class NoCityList(Exception):
    """
    未能获取到城市列表
    """

class InvalidCityUrl(Exception):
    """
    不是准确的城市首页链接
    """

class NoTextFiled(Exception):
	"""
	没有找到相关的字段
	"""

class NoDatabaseFound(Exception):
	"""
	没有对应的数据库
	"""