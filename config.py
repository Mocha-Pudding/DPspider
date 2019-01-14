
#是否使用代理
PROXY_ENABLE = True

#使用单个的代理ip，优先级最高
#此项若有填写，则使用此代理，后面的不会考虑
# 格式可以为下面几种:
# 1.  "1.1.1.1:1111"
# 2.  "username:password@1.1.1.1:1111"
# 3.  "www.dailiurl.com/path/xxxx"
# 4.  "username:password@www.dailiurl.com/path/xxxx"
PROXY = ''

#IP代理池，优先级低于PROXY高于PROXY_POOL_RAW
# * 建议使用购买的代理池API，一次请求一个代理，每次请求不重复，请求间隔为INTERVAL
# * 或者是一个代理IP文件，文件的一行便是一个代理如:<ip>:<port>
# * 或者是一个代理池IP列表，如:[<ip>:<port>,..]
# 格式可以为下面几种:
# 1、 "http:http://39.108.59.38:8888/Tools/proxyIP.ashx?OrderNumber=xxxx&poolIndex=xxx&cache=1&qty=1"
# 2、 ['1.1.1.1:1111','1.1.1.1:1112','1.1.1.1:1113',...]
# 3、 "D://proxyfile.txt"
PROXY_POOL =  'http://39.108.59.38:8888/Tools/proxyIP.ashx?OrderNumber=912694cb32aff4d695d58412c48c3859&poolIndex=17922&cache=1&qty=1'
# PROXY_POOL = 'http://39.108.59.38:8888/Tools/proxyIP.ashx?OrderNumber=a2b03f9d740e34f50946d4d8f5b6707f&poolIndex=53411&cache=1&qty=1'

#未经过验证有效性的代理池文件,如:'txt/rawproxy.txt'，如果PROXY_POOL是一个文件
#那么程序会进行自动检测代理的有效性后将可用代理写入PROXY_POOL
#后进行使用，优先级最低,测试代理url为PROXY_TEST_URL
PROXY_POOL_RAW = 'txt/rawproxy.txt'
#当PROXY_POOL_RAW不为空时，检测代理可用性使用此url
PROXY_TEST_URL = 'http://www.dianping.com/'
#测试代理池可用性的最大线程数
PROXY_TEST_MAX = 200

# 城市的店铺种类分类文件，存储在本地，再次获取某个城市的店铺分类时
# 如果存在此文件，读取此文件，文件中存有此城市的店铺分类数据时，不再
# 重新请求获取，没有的话请求获取后更新进此文件.删除此文件会重新更新存储.
CATEGORY_FILE_PATH = 'JSON/category.json'

# 城市的激活地区文件，存储在本地，再次获取某个城市的某些地区时
# 如果存在此文件，读取此文件，文件中存有此城市的地区数据时，不再
# 重新请求获取，没有的话请求获取后更新进此文件.删除此文件会重新更新存储.
LOCATIONS_FILE_PATH = 'JSON/locations.json'

# 城市搜索结果进行排序的选项字典文件，存储在本地，再次获取某个城市的某个关键词
# 的搜索结果进行排序时，如果存在此文件，读取此文件，可以根据文件内容进行选择
# 排序搜索结果。没有的话请求获取后更新进此文件.删除此文件会重新更新存储.
SORTS_FILE_PATH = 'JSON/sorts.json'

# 全国城市地区链接文件，存储在本地，访问某个城市时，会查询文件中是否有
# 这个城市。如果没有此文件，会进行请求获取下载。删除此文件会重新更新存储.
CITY_LIST_FILE_PATH = 'JSON/cityList.json'

# 全国所有激活注册大众点评的地区城市详细的信息json文件，
# 本地存储.删除此文件会重新更新存储.
CITY_DETAIL_FILE_PATH = 'JSON/active_cities.json'

# 全国各个省份的ID及地区ID文件，本地存储.删除此文件会重新更新存储.
PROVINCE_FILE_PATH = 'JSON/province.json'

#MongoDB数据库设置
MongoDB = {
    'host'          :'127.0.0.1',
    'port'          :27017,
    'database'      :'大众点评',
    'records'       :'爬取记录',
    'searchDB'      :'大众点评地图搜索',
    'user'          :'',
    'password'      :'',
}

#允许网络请求的HTTP方法
HTTP_METHODS = ['get','head','post','put','options']

#记录搜索爬取痕迹，下次搜索爬取便不会重复下载存储
RECORD_ENABLE = True

#请求失败后的重试次数：
# -1表示无限次请求；
# 0表示不重试；
# >0的表示重试次数
MAX_RETRY = -1

#店铺间的抓取时间间隔:秒
SLEEP = 1

#每一次请求或者重试失败后的等待延时时间：秒，
#也是使用代理时失败再次使用代理API提取代理的间隔
INTERVAL = 0

#随机请求等待时间间隔，秒
#数组表示(a,b)返回a到b范围内的随机秒数
#开始随机等待将RANDOM_SLEEP置True
RANDOM_SLEEP = True
RANDOM_INTERVAL = (1,10)

#请求超时时间设置：秒
TIMEOUT = 10

#哪些请求状态码视为被禁
FORBIDDEN_CODE = [403,]

#被禁多少次之后进行User-Agent的更换
FORBIDDEN_MAX_TO_CHANGE = 3

#404状态返回多少次后放弃该请求
NOT_FOUND_MAX_TO_DROP = 6

#请求失败多少次之后放弃当前请求
FAIL_MAX_TO_DROP = 200

#搜索相关结果返回的条数，
# -1表示全部返回
# >0返回最多该条数
SEARCH_RESULTS = -1

#店铺点评下载返回的条数，
# -1表示全部返回
# >0返回最多该条数
COMMENTS_RESULTS = -1

#商铺点评 获取的默认条数
# -1 表示获取全部
# >0获取最多该条数
COMMENTS_COUNT_DEFAULT = -1

#点评页获取时间间隔，秒
#(a,b)为a到b的随机秒数
COMMENTS_SLEEP = (50,60)

#日志设置
#启用日志
LOG_ENABLE = True
#日志级别
LOG_LEVEL = 'INFO'
#日志文件编码
LOG_FILE_ENCODING = 'UTF-8'
#日志文件路径
LOG_FILE_SAVE_PATH = r'txt/log.txt'
#日志时间格式
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
#日志级别对应格式
LOG_FORMAT = {
    'DEBUG'     : '%(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'INFO'      : '%(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'WARNING'   : '%(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'ERROR'     : '%(asctime)s %(name)s(%(levelname)s) - %(message)s',
    'CRITICAL'  : '%(asctime)s %(name)s(%(levelname)s) - %(message)s',
}

#获取所有点评必须使用大众点评注册用户的登陆cookie
COOKIE = ''
