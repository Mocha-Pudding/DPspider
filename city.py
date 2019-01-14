#coding:utf-8
import time
from util.tools import *
from util.city import *
from search import Search
from comment import Comments
from exception import InvalidCityUrl
from util.http import send_http
from util.thread import CrawlThread
from decorator.city import recover,\
    has_id,has_city_list,map_required
from decorator import already,timer
from log import getLogger

logger = getLogger(__name__)

class City(object):
    """
    已激活城市
    """

    api = API_CITY

    def __init__(self,
                 city,
                 url=None,
                 Id=None,
                 commentsDB=None,
                 searchDB=None):
        self._id = Id
        self._url = url
        self.city = city
        self.headers = HEADERS
        self.map_headers = SEARCH_MAP_POST_HEADERS
        self._pinyin = get_pinyin(city)
        self.session = requests.session()
        self.db = init_db(commentsDB)
        self.searchDB = init_search_db(searchDB)
        self.map_page = None
        self.city_list = None
        self.homepage = None
        self.shop_proxy = None
        self.proxy = None
        self._name = None
        self._hot = None
        self._filters = None
        self._sorts = None
        self._category = None
        self._locations = None

    @timer
    def get(self,headers=HEADERS,proxy=None):
        """
        抓取当前城市首页
        :param proxy:使用的代理
        :param headers:伪造的请求头部
        """
        result = send_http(self.session,
                           'get',
                           self.url,
                           retries=MAX_RETRY,
                           headers=headers,
                           proxy=proxy,
                           timeout=TIMEOUT,
                           kind='CITY',
                           )
        if result:
            response, self.proxy, self.headers = result
            self.homepage = response.text
            logger.info(f'获取 “{self.city}” 首页成功.')

    @has_id
    @timer
    def get_map(self,headers=HEADERS,proxy=None):
        url = API_CITY_MAP.format(id=self.id)
        result = send_http(self.session,
                           'get',
                           url,
                           retries=MAX_RETRY,
                           headers=headers,
                           proxy=proxy,
                           timeout=TIMEOUT,
                           kind='MAP',
                           )
        if result:
            response, self.proxy, self.headers = result
            self.map_page = response.text
            logger.info(f'获取 “{self.city}” 地图搜索页成功')

    @property
    def pinyin(self):
        py = self.url.split('/')[-1]
        return py

    @property
    def url(self):
        return self._url if self._url else self.get_url()

    @property
    def id(self):
        return self._id if self._id else self.get_id()

    @property
    def name(self):
        return self._name if self._name else self.get_name()

    @property
    def hot(self):
        return self._hot if self._hot else self.get_hot()

    @property
    def category(self):
        return self._category if self._category else self.get_category()

    @property
    def locations(self):
        return self._locations if self._locations else self.get_locations()

    @property
    def sorts(self):
        return self._sorts if self._sorts else self.get_sorts()

    @property
    def filters(self):
        return self._filters if self._filters else self.get_filters()

    @has_city_list
    def get_url(self,reget=False):
        """
        获取当前城市的首页链接
        :param reget: 重新抓取
        """
        if self._url:
            return self._url
        elif self.city in self.city_list:
            self._url = self.city_list[self.city]
            return self._url
        else:
            for city,url in self.city_list.items():
                if city.startswith(self.city):
                    self._url = url
                    return self._url
            raise InvalidCityUrl(f'未找到城市 "{self.city}" 首页链接.')

    @already
    def get_id(self,reget=False):
        """
        获取当前城市ID
        :param reget:重新抓取
        """
        self._id = from_pattern(PATTERN_CITYID,self.homepage)
        return self._id

    @already
    def get_name(self,reget=False):
        """
        获取当前城市中文全称
        :param reget:重新抓取
        """
        self._name = from_pattern(PATTERN_CITYCN,self.homepage)
        return self._name

    @recover(CATEGORY_FILE_PATH)
    @map_required
    def get_category(self, reget=False):
        """
        获取该城市的店铺分类,包含子分类
        :param reget: 重新抓取
        """
        _data = from_pattern(PATTERN_MAP_CATEGORY,self.map_page)
        self._category = json.loads(_data)
        return self._category

    @recover(LOCATIONS_FILE_PATH)
    @map_required
    def get_locations(self,reget=False):
        """
        获取该城市的所有地区，包含子地区
        :param reget: 重新抓取
        """
        _data = from_pattern(PATTERN_MAP_LOCATION, self.map_page)
        self._locations = json.loads(_data)
        return self._locations

    @recover(SORTS_FILE_PATH)
    @map_required
    def get_sorts(self,reget=False):
        """
        获取该城市搜索结果的排序相关字典
        :param reget:重新抓取
        """
        _data = from_pattern(PATTERN_MAP_SORT, self.map_page)
        self._sorts = json.loads(_data)
        return self._sorts

    @map_required
    def get_filters(self):
        res = {}
        div = get_sub_tag(self.map_page,'filters')
        if div:
            for li in div('li'):
                item = li.text.strip()
                value = li['data-value']
                res[item]=value
        self._filters  = res
        return self._filters

    @has_id
    @timer
    def get_relative(self, keyword):
        """
        返回关键词相关的搜索结果和结果数
        :param keyword:关键词
        :return:{相关结果:数量,..}
        """
        url = API_KEY_RELATIVE.format(id=self.id, key=keyword)
        result = send_http(self.session,
                           'get',
                           url,
                           headers=self.headers,
                           retries=MAX_RETRY,
                           kind='JSON',
                           proxy=self.proxy)
        if result:
            response, self.proxy, _ = result
            data = response.json()
            res = {i.split('|')[0]:from_pattern(PATTERN_NUMS, i.split('|')[-2])
                   for i in data['msg']['shop']}
            return res

    @has_id
    @timer
    def get_hot(self):
        """
        获取当前城市的搜索热度前十关键词
        :return:[{'子标签': '8', '索引': '0', '主分类id': '', '数据类型': '3000', 'id_': '587192', '关键词': '三里屯'},..]
        """
        url = API_CITY_HOT.format(id=self.id)
        result = send_http(self.session,
                           'get',
                           url,
                           headers=self.headers,
                           retries=MAX_RETRY,
                           kind='JSON',
                           proxy=self.proxy)
        if result:
            response,self.proxy,_ = result
            data = response.json()
            self._hot = [i['valueMap'] for i in  data['recordList']]
            return self._hot

    @map_required
    @timer
    def search(self,keyword,
               category=None,location=None,
               sort=None,filter=None,count=SEARCH_RESULTS,
               save=False,path=None,details=False,comments=False,
               comments_count=COMMENTS_RESULTS,comments_path=None,
               write_mode='a',comments_mode='a'):
        """
        获取该城市的关键词相关店铺搜索结果
        :param keyword:关键词
        :param category:店铺类别
        :param location:店铺所在地区
        :param sort:结果排序条件
        :param filter:结果过滤条件
        :param count:返回结果的最多条数,-1表示返回全部
        :param save:是否保存进数据库,按照count的返回值存储条数
        :param path:数据进行本地保存的文件路径
        :param details:是否爬取商铺的详细信息
        :param comments:是否爬取商铺的点评
        :param comments_count:需要下载的商铺点评数最大值
        :param comments_path:本地保存点评数据的文件路径
        :param write_mode:本地保存时的文件操作模式
        :param comments_mode:本地存储点评数据文件操作模式
        """
        page = 1
        _count = 0
        _region_count = 0
        pageCount = 0
        shop_proxy = None
        results = []
        shop_headers = HEADERS
        searcher = Search(self.city,keyword,self.category,
                          self.locations,self.sorts,
                          category,location,sort,filter,count)
        regions = [searcher.region_id,]
        hint = together(self.city,location,category,keyword)
        while 1:
            #无待爬取地区，此次查询结束
            if not regions:
                break
            _region_id = regions.pop(0)
            region_name = find_region_by_id(_region_id, self.locations)
            _region_name = self.city if not region_name else region_name
            #查询当前爬取地区是否已经爬取存进数据库中
            if save and self.searchDB:
                _record = self.searchDB.select({'tname': {'=': searcher.tname},
                                                'crawledID': {'=': _region_id}}, tname=MongoDB['records'])
                if _record:
                    logger.info(f'{hint}->{_region_name} 关于 {keyword} 的搜索结果已经被下载过.总条数:{_record[0]["count"]}')
                    continue
            #根据当前城市、地区ID、当前页数生成地图搜索POST参数数据
            data = searcher.get_map_post_data(self.id,self.pinyin,page,regionId=_region_id)
            result = self.fetch_map_page(data)
            if result:
                if page==1:
                    pageCount = int(result['pageCount'])
                    if pageCount == 0:
                        continue
                    logger.info(f'搜索 {hint}->{_region_name} 关于 {keyword} 的结果有{pageCount}页.')
                    #当前地区的页数是否超过大众点评预设的显示极限页数
                    if pageCount>SEARCH_LIMITS:
                        #当前地区页数过大，分解为子地区当前分类的搜索后再合并
                        children_regions = find_children_regions(_region_id,self.locations)
                        #当前地区无子地区，则只爬取大众点评显示极限条数
                        if not children_regions:
                            count = SEARCH_LIMITS*SEARCH_META_COUNT
                            logger.info(f'* {_region_name} 无子节点，限制最大搜索结果数为:{count}')
                        else:
                            logger.info(f'{_region_name} 搜索结果页数>{SEARCH_LIMITS}页,加入子节点{children_regions}.')
                            #存在子地区，将所有子地区插进待爬取地区列表头进行逐个搜索爬取
                            for i in children_regions:
                                regions.insert(0,i)
                            continue
                #当前地区页数大于1页小于总页数，则一直进行当前地区的搜索爬取
                if pageCount > 1 and page < pageCount:
                    regions.insert(0,_region_id)
                _list = result['shopRecordBeanList']
                if _list:
                    logger.info(f'成功获取到 {hint}->{_region_name} 第{page}页 {len(_list)} 条数据.')
                    for i in _list:
                        shopId = i['shopId']
                        #是否已经爬取过存入数据库
                        if save and self.searchDB:
                            if self.searchDB.select({'店铺ID':{'=':shopId}},tname=searcher.tname):
                                continue
                        i = transfer_data(i,self.locations)
                        #是否爬取更加详细的商铺信息
                        if details:
                            resp = get_city_shop_info(shopId,self.id,shop_proxy,shop_headers)
                            if resp:
                                shop_info, shop_proxy, shop_headers = resp
                                i.update(shop_info)
                            else:
                                continue
                        #是否需要保存进数据库
                        if save and self.searchDB:
                            self.searchDB.save(i,tname=searcher.tname)
                        #是否进行本地存储
                        elif path:
                            with open(path,write_mode) as f:
                                f.write(json.dumps(i))
                                f.write('\n')
                        results.append(i)
                        #是否爬取商铺的点评数据
                        if comments:
                            if i['点评数']:
                                comment = Comments(shopId,db=self.db)
                                comment.get_reviews(save=save,tname=hint,
                                                    path=comments_path,write_mode=comments_mode,
                                                    count=comments_count,reget=True)
                        #判断是否爬取商铺信息数量达到预设值
                        if _count >= count and count > 0:
                            logger.info(f'[{count}]完成获取 {_count} 条数据的任务.')
                            return results
                        _count+=1
                        _region_count+=1
                    #当前页已经是该地区的最后一页
                    if pageCount == page:
                        #此次查询是否还有待爬取地区
                        if not regions:
                            logger.info(f'[*] {searcher.tname} 所有数据获取完成,条数:{_count}.')
                            return results
                        else:
                            logger.info(f'{hint}-{_region_name} 抓取完成 {_region_count} 条.')
                            #将完全爬取完成的地区记录进数据库
                            if RECORD_ENABLE:
                                if self.searchDB:
                                    records = {
                                        "tname":searcher.tname,
                                        "crawledID":_region_id,
                                        "count":_region_count,
                                        "finishedAt":time_to_date(int(time.time()))
                                    }
                                    self.searchDB.save(records,tname=MongoDB['records'])
                            page = 1
                            _region_count = 0
                            continue
                    page += 1
                    continue
                break
            break
        return results

    @map_required
    @timer
    def async_search(self,keyword,
               category=None,location=None,
               sort=None,filter=None,
               save=False,path=None,details=False,comments=False,
               comments_count=COMMENTS_RESULTS,write_mode='a',
               comments_path=None,comments_mode='a'):
        """
        多线程获取该城市的关键词相关店铺搜索结果
        :param keyword:关键词
        :param page:从搜索结果第几页开始获取
        :param category:店铺类别
        :param location:店铺所在地区
        :param sort:结果排序条件
        :param filter:结果过滤条件
        :param save:是否保存进数据库,按照count的返回值存储条数
        :param path:数据进行本地保存的文件路径
        :param details:是否爬取商铺的详细信息
        :param comments:是否爬取商铺的点评
        :param comments_count:需要下载的商铺点评数最大值，-1表示所有
        :param write_mode:本地保存时的文件操作模式
        :param comments_path:本地保存点评数据的文件路径
        :param comments_mode:本地存储点评数据文件操作模式
        """
        results = []
        searcher = Search(self.city, keyword, self.category,
                          self.locations, self.sorts,
                          category, location, sort, filter)
        regions = [searcher.region_id,]
        hint = together(self.city,location,category,keyword)
        _count = 0
        while 1:
            threads = []
            _region_count = 0
            if not regions:
                break
            _region_id = regions.pop(0)
            region_name = find_region_by_id(_region_id, self.locations)
            _region_name = self.city if not region_name else region_name
            if save and self.searchDB:
                _record = self.searchDB.select({'tname': {'=': searcher.tname},
                                                'crawledID': {'=': _region_id}}, tname=MongoDB['records'])
                if _record:
                    logger.info(f'{hint}->{_region_name} 关于 {keyword} 的搜索结果已经被下载过.总条数:{_record[0]["count"]}')
                    continue
            data = searcher.get_map_post_data(self.id, self.pinyin, 1, regionId=_region_id)
            result = self.fetch_map_page(data)
            if result:
                pageCount = int(result['pageCount'])
                if pageCount==0:
                    continue
                logger.info(f'搜索 {hint}->{_region_name} 关于 {keyword} 的结果有{pageCount}页.')
                if pageCount > SEARCH_LIMITS:
                    children_regions = find_children_regions(_region_id, self.locations)
                    if not children_regions:
                        logger.info(f'* {_region_name} 无子节点，限制最大搜索结果页数为:{SEARCH_LIMITS}')
                    else:
                        logger.info(f'{_region_name} 搜索结果页数>{SEARCH_LIMITS}页,加入子节点{children_regions}.')
                        for i in children_regions:
                            regions.insert(0, i)
                        continue
                for i in range(1,pageCount+1):
                    data = searcher.get_map_post_data(self.id, self.pinyin, i, regionId=_region_id)
                    threads.append(CrawlThread(self.__fetch_page,args=(i,data,_region_id,searcher.tname,
                                                                       save,path,details,
                                                                       comments,comments_count,
                                                                       write_mode,comments_path,
                                                                       comments_mode)))
                for i in threads:
                    i.start()
                for i in threads:
                    i.join()
                    res = i.get_result()
                    if res:
                        _region_count += len(res)
                        results.extend(res)
                logger.info(f'{hint}-{_region_name} 抓取完成 {_region_count} 条.')
                if RECORD_ENABLE:
                    if save and self.searchDB:
                        records = {
                            "tname": searcher.tname,
                            "crawledID": _region_id,
                            "count": _region_count,
                            "finishedAt": time_to_date(int(time.time()))
                        }
                        self.searchDB.save(records, tname=MongoDB['records'])
                _count += _region_count
        logger.info(f'[*] {searcher.tname} 所有数据获取完成,条数:{_count}.')
        return results

    def fetch_map_page(self,data):
        result = send_http(self.session,
                           'post',
                           API_MAP_SEARCH,
                           retries=MAX_RETRY,
                           proxy=self.proxy,
                           headers=self.map_headers,
                           timeout=TIMEOUT,
                           data=data,
                           kind='JSON'
                           )
        if result:
            response, self.proxy, self.map_headers = result
            page_data = response.json()
            return page_data

    def __fetch_page(self,page,data,regionId,tname,
                     save,path,details,comments,
                     comments_count,write_mode,
                     comments_path,comments_mode):
        results = []
        shop_proxy = None
        shop_headers = HEADERS
        page_data = self.fetch_map_page(data)
        if page_data:
            if save and self.searchDB:
                _record = self.searchDB.select({'tname': {'=':tname},
                                                'crawledID': {'=': regionId}}, tname=MongoDB['records'])
                if _record:
                    logger.info(f'{tname}-地区ID:{regionId} 的搜索结果已经被下载过.总条数:{_record[0]["count"]}')
                    return
            data_list = page_data['shopRecordBeanList']
            logger.info(f'成功获取到 {tname}-地区ID:{regionId} 第{page}页 {len(data_list)} 条搜索结果.')
            for i in data_list:
                shopId = i['shopId']
                if save and self.searchDB:
                    if self.searchDB.select({'店铺ID': {'=': shopId}}, tname=tname):
                        continue
                i = transfer_data(i, self.locations)
                if details:
                    resp = get_city_shop_info(shopId, self.id, shop_proxy, shop_headers)
                    if resp:
                        shop_info, shop_proxy, shop_headers = resp
                        i.update(shop_info)
                    else:
                        continue
                if save and self.searchDB:
                    self.searchDB.save(i, tname=tname)
                elif path:
                    with open(path, write_mode) as f:
                        f.write(json.dumps(i))
                        f.write('\n')
                # 是否爬取商铺的点评数据
                if comments:
                    if i['点评数']:
                        comment = Comments(shopId, db=self.db)
                        comment.get_reviews(save=save, tname=tname,
                                            path=comments_path, write_mode=comments_mode,
                                            count=comments_count, reget=True)
                results.append(i)
            return results