#coding:utf-8

import json
import codecs
from log import getLogger
from exception import NoDatabaseFound

logger = getLogger(__name__)

class Review(object):

    def __init__(self,userName,userId,userUrl,userImg,userLevel,userVip,
                 star,score,reviewId,reviewUrl,reviewTime,reviewShop,reviewShopId,
                 reviewPics,reviewWords,actions
                 ):
        self.userName = userName
        self.userId = userId
        self.userUrl = userUrl
        self.userImg = userImg
        self.userLevel = userLevel
        self.userVip = userVip
        self.star = star
        self.score = score
        self.id = reviewId
        self.url = reviewUrl
        self.reviewTime = reviewTime
        self.shopName = reviewShop
        self.shopId = reviewShopId
        self.imgs = reviewPics
        self.actions = actions
        self.content = reviewWords

    @property
    def data(self):
        data = {
            u'点评ID': self.id,
            u'点评链接': self.url,
            u'点评用户': self.userName,
            u'用户ID': self.userId,
            u'用户主页': self.userUrl,
            u'用户头像': self.userImg,
            u'用户等级': self.userLevel,
            u'VIP用户': self.userVip,
            u'点评商铺': self.shopName,
            u'商铺ID': self.shopId,
            u'点评星级': self.star,
            u'用户评价': self.score,
            u'点评时间': self.reviewTime,
            u'点评图片': self.imgs,
            u'评论事件': self.actions,
            u'点评内容': self.content,
        }
        return data

    def save(self,db=None,tname=None):
        self.tname = tname if tname else db.table
        if db is None:
            raise NoDatabaseFound
        if db.select({'点评ID':{'=':self.id}},tname=tname):
            return
        else:
            try:
                db.save(self.data,tname=tname)
            except Exception as e:
                logger.error(f'保存点评:{self.id}出错 - {e.__class__.__name__}:{e}')
            else:
                logger.info(f'点评 ID:{self.id},店铺:{self.shopName}  保存成功,数据表:{self.tname}')

    def write(self,path=None, mode='a'):
        if path:
            with codecs.open(path,mode,encoding='utf-8') as f:
                f.write(str(self.data))
                f.write('\n')
                logger.info(f'点评 ID:{self.id},店铺:{self.shopName} 保存成功,文件路径:{path}')



