# coding:utf-8

import pymongo
import logging
from inspect  import isfunction
from settings import CON_MAP

logger = logging.getLogger()

class Database(object):
    """
    对MongoDB数据库对象的封装，提供更高功能的接口使用
    """
    def __init__(self,settings):
        """
        初始化
        :param settings: 数据库设置
        """
        self.host   = settings['host']
        self.port   = settings['port']
        self.user   = settings['user']
        self.passwd = settings['password']
        self.db     = settings['database']
        self.connected = False
        self.conn    = None
        self.handler = None
        self.table   = None

    def connect(self):
        """
        连接MongoDB
        """
        if self.user and self.passwd:
            self.conn = pymongo.MongoClient(self.host, self.port,username=self.user,password=self.passwd)
        else:
            self.conn = pymongo.MongoClient(self.host, self.port)
        self.handler = self.conn[self.db]
        self.connected = True

    def close(self):
        """
        关闭数据库连接
        """
        self.conn.close()
        self.conn=None

    def use_db(self,dbname):
        """
        连接数据库后使用名为dbname的数据库
        :param dbname: 要使用的数据库
        """
        self.handler = self.conn[dbname]

    def save(self,data,tname=None,format=None):
        """
        保存数据到数据集
        :param data: 要保存的数据,{}类型或 [{},{}..]类型
        :param tname: 数据集(collection)
        :param format:对数据进行格式化的函数，可以根据数据结构自定义
        """
        table = tname if tname else self.table
        format = None if not isfunction(format) else format
        if not table:
            raise Exception('No table or data collection specified by tname.')
        if isinstance(data,dict):
            data = format(data) if format else data
            self.handler[table].insert(data)
        elif isinstance(data,list):
            for i in data:
                if isinstance(i,dict):
                    i = format(i) if format else i
                    self.handler[table].insert(i)
                else:
                    raise TypeError('Expected a dict type value inside the list,%s type received.' % type(data))
        else:
            raise TypeError('Expected a [{},{}..] or {} type data,%s type received.' % type(data))

    def select(self,condition,tname=None,sort=None):
        """
        条件查询数据库得到一个数据列表
        :param condition: 查询条件
        :param tname: 要查询的数据集合名
        :param sort: 排序规则，MongoDB标准，使用dict类型
        :return: 返回查询结果 [{},{},..] 类型
        """
        table = tname if tname else self.table
        if not isinstance(condition,dict):
            raise TypeError('condition is not a valid dict type param.')
        else:
            try:
                conditions = self.__gen_mapped_condition(condition)
                if sort and isinstance(sort,dict):
                    res = self.handler[table].find(condition).sort(list(sort.items()))
                else:
                    res = self.handler[table].find(conditions)
                data = list(res)
                return data if data else []
            except Exception as e:
                logger.error('Error class : %s , msg : %s ' % (e.__class__, e))
                return

    def delete(self,condition,tname=None):
        """
        删除数据库符合条件的数据条目
        :param condition: 删除条件  dict类型
        :param tname: 要删除数据所在的数据集合名
        """
        if not condition: return
        conditions = self.__gen_mapped_condition(condition)
        table = tname if tname else self.table
        if not isinstance(condition,dict):
            raise TypeError('condition is not a valid dict type param.')
        self.handler[table].delete_many(conditions)

    def update(self,condition,data,tname=None):
        """
        按照条件更新数据库数据
        :param condition: 查询条件 dict类型
        :param data: 更新数据 dict类型
        :param tname: 要更新的数据所在的数据集合名
        """
        table = tname if tname else self.table
        if not data :return
        if not isinstance(condition, dict) and not isinstance(data,dict):
            raise TypeError('Params (condition and data) should both be the dict type.')
        conditions= self.__gen_mapped_condition(condition)
        self.handler[table].update(conditions,{'$set':data},False,True )

    def all(self,tname=None):
        """
        返回MongoDB数据库某个集合的所有数据
        :param tname: 数据集合名
        :return: 所有该集合的数据 格式:[{},{},..]
        """
        table = tname if tname else self.table
        data = list(self.handler[table].find())
        return data

    def __gen_mapped_condition(self,condition):
        """
        MongoDB与sql语句的条件查询映射,使其符合MongoDB语法
        如：查询条件为 {'score':{'<':0}}
        则将其映射为   {'score':{'$lt':0}}
        符合MongoDB的查询语法
        :param condition:查询条件 dict类型
        :return: 映射结果 dict类型
        """
        for key in condition:
            if isinstance(condition[key], dict):
                t = condition[key]
                operator = list(t.keys())[0]
                value = t[operator]
                o = CON_MAP[operator]
                condition[key].pop(operator)
                condition[key][o] = value
        return condition
