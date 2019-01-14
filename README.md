# 大众点评爬虫可用api

> 可用于大众点评网页版

> 目前可用：
> * 获取大众点评当前可以查询查看到店铺的所有已激活城市信息
> * 获取大众点评里所有省市直辖市的provinceId以及地区areaId
> * 根据给定的中文城市、地区名称来获取其大众点评首页链接
> * 通过id获取地区名称
> * 通过id获取地区内的所有子地区信息
> * 获取某个城市的 热搜关键词
> * 获取某个城市的 当前可见有效店铺分类
> * 获取某个城市的 当前可见有效的辖区信息，包含子地区
> * 获取某个城市的 某个关键词相关的搜索结果和结果数
> * （单线程与多线程）搜索某个城市关于某个关键词的某个分类、子地区、排序方式的相关店铺并支持MongoDB存储和本地文件存储
> * 获取某个商铺的评分、星级、地址、电话、点评数、人均消费、点评标签、点评种类等
> * 获取某个商铺的加密点评信息，支持条数设定

## 环境
使用环境：
> - win 7 64bits
> - pycharm
> - python3

第三方库：
> * bs4 >=0.0.1
> * lxml >=4.2.5
> * pymongo >=3.7.1
> * requests >=2.19.1

## 使用前

因为大众点评的反爬措施，需要设置IP代理以及随机切换可用的User-Agent来进行大量数据的爬取。
> **IP代理(Proxy)**

> 如何设置？config.py中有详细的各个代理设置注释，建议使用PROXY_POOL进行IP代理，可以使用一次一个的接口来获取代理IP。

> **UA池**

> user-agent可以使用settings.py中的UA池，如果你有更多的可用UA，可以自己加进去或者替换掉。

> **用户cookie**

> 如果你需要爬取加密的商铺点评数据（页数>1），则需要添加点评用户的登陆cookie到config.py的COOKIE中。具体内容为一个字符串，如：
'_lxsdk_cuid=1681d897b62c8;_hc.v=ff4f63f6;thirdtoken=c9792'之类的。可以在浏览器调试界面获得。

> **数据库存储（MongoDB）与本地存储**

> 如果需要存储搜索的店铺数据，则需要到config.py中设置MongoDB的数据库设置(本地存储可以在城市搜索api中设置保存本地的路径。)，其中
> * 'database'为默认使用的数据库，
> * 'records'为记录抓取的数据表名，
> * 'searchDB'为搜索结果存放的数据库

> 其他相关的配置可以参见config.py 中的设置注解
## 使用

* 获取大众点评当前可以查询查看到店铺的所有已激活城市信息
```python
from dianping import DianPing
dp = DianPing()
cities = dp.active_cities
```
> 返回结果 cities 为大众点评全国可以显示搜索到店铺的激活城市列表：
```json
[
   {
        "activeCity": true, 
        "appHotLevel": 1, 
        "cityAbbrCode": "BJ", 
        "cityAreaCode": "010", 
        "cityEnName": "beijing", 
        "cityId": 2, 
        "cityLevel": 1, 
        "cityName": "北京", 
        "cityOrderId": 406, 
        "cityPyName": "beijing", 
        "directURL": "", 
        "gLat": 39.904667, 
        "gLng": 116.408198, 
        "overseasCity": false, 
        "parentCityId": 0, 
        "provinceId": 1, 
        "scenery": false, 
        "tuanGouFlag": 1
    },
    ...
]
```

* 获取大众点评里所有省市直辖市的provinceId以及地区areaId
```python
from dianping import DianPing
dp = DianPing()
provinces = dp.provinces
```
> 返回结果 provinces 为全国的省、直辖市的ID信息：
```json
{
    "北京": {
        "areaId": 1, 
        "provinceId": "1"
    }, 
    "天津": {
        "areaId": 1, 
        "provinceId": "2"
    }, 
    "河北": {
        "areaId": 1, 
        "provinceId": "3"
    }, 
    "山西": {
        "areaId": 1, 
        "provinceId": "4"
    }, 
    ...
}
```

* 根据给定的中文城市、地区名称来获取其大众点评首页链接
```python
from city import City
beijing = City('北京')
url = beijing.url
```
> 返回结果 url 为北京市的大众点评首页:
```text
http://www.dianping.com/beijing
```
* 获取某个城市的 当前可见有效的辖区信息，包含子地区
```python
from city import City
beijing = City('北京')
beijing.get()
locations = beijing.locations
```
> 返回结果 locations 为当前城市的所有子地区信息：
```json
[
    {
    "text": "海淀区", 
    "value": "17", 
    "children": [
        {
            "text": "双榆树", 
            "value": "2587", 
            "children": [
                {
                    "text": "HQ尚客百货", 
                    "value": "6975"
                }, 
                {
                    "text": "当代商城", 
                    "value": "2622"
                }, 
                {
                    "text": "华星影城", 
                    "value": "2665"
                }, 
                {
                    "text": "双安商场", 
                    "value": "2720"
                }
            ]
        }, 
        ...
    ]
    },
    ...
]
```
* 通过id获取城市的某个地区名称
```python
#id 必须为城市中某个地区的id
from util.city import find_region_by_id
from city import City
beijing = City('北京')
beijing.get()
someplace = find_region_by_id(6975,beijing.locations)
```
> 返回结果 someplace 为北京地区的对应id的子地区名称：
```python
# ID 6975 对应的地区
HQ尚客百货
```

* 通过id获取地区内的所有子地区信息
```python
from util.city import find_children_regions
from city import City
beijing = City('北京')
beijing.get()
sub_regions = find_children_regions(5956,beijing.locations)
```
> 返回结果 sub_regions 为当前id下的所有子地区id列表：
```text
# id 在城市的子地区列表中，但其未有子地区，返回：
False
# id 在城市的子地区列表中, 如果其有子地区的话则返回子地区id列表：
['6008']
# id 不在城市的子地区列表中，则返回城市的一级子地区：
['17', '5951', '328', '15', '5952', '14', '5950', '9158', '16', '20', '9157']
```
* 获取某个城市的 热搜关键词
```python
from city import City
beijing = City('北京')
beijing.get()
hot = beijing.hot
```
> 返回结果 hot 为当前城市“北京”的热搜词汇列表（包含其所属分类id等信息）：
```json
[    
    {
        "subtag": "3",     
        "location": "7", 
        "maincategoryids": "35,60", 
        "datatype": "3002", 
        "id_": "786881", 
        "suggestkeyword": "温泉"
    }, 
    {
        "subtag": "18", 
        "location": "8", 
        "maincategoryids": "10", 
        "datatype": "3002", 
        "id_": "692874", 
        "suggestkeyword": "烤鸭"
    },
    ...
]
```
* 获取某个城市的 当前可见有效店铺分类
```python
from city import City
beijing = City('北京')
beijing.get()
category = beijing.category
```
> 返回结果 category 为该城市所有的店铺分类信息列表：
```json
[
    {
        "text": "酒吧", 
        "value": "133", 
        "children": [
            {
                "text": "清吧", 
                "value": "33950"
            }, 
            {
                "text": "Live House", 
                "value": "33951"
            }, 
            {
                "text": "夜店", 
                "value": "2951"
            }
        ]
    }, 
    {
        "text": "茶馆", 
        "value": "134"
    }, 
    ...
]
```
* 获取某个城市的 某个关键词相关的搜索结果和结果数
```python
from city import City
beijing = City('北京')
beijing.get()
relative = beijing.get_relative('健身')
```
> 返回结果 relative 为北京市关键词“健身”相关的搜索词汇以及其对应结果数：
```json
{
    "良子健身 京粮大厦店": "1", 
    "健身游泳瑜伽综合性会所": "1", 
    "Hey Heroes！私教健身工作室 泛悦坊店": "1", 
    "ULife悦体健身 五棵松店": "1", 
    "U-Vista优维斯塔健身工作室 金融街旗舰店": "1", 
    "健身房24小时": "161", 
    "健身体验卡": "1", 
    "锐健身": "29", 
    "Hot Fitness 热健身工作室 霍营店": "1", 
    "锻造健身ForgingFitness国际私教工作室": "1"
}
```
* （单线程与多线程）搜索某个城市关于某个关键词的某个分类、子地区、排序方式的相关店铺并支持MongoDB存储和本地文件存储

> * 单线程搜索下载相关店铺

下例为搜索下载北京市“海淀区”店铺分类为“运动健身”的“有团购”的与“器材”相关的所有店铺，搜索下载结果“按人气排序”，
save表示是否保存进MongoDB数据库，details表示是否抓取店铺的详细信息。具体参数可见search函数注释。
```python
from city import City
beijing = City('北京')
beijing.get()
results = beijing.search('器材',category='运动健身',location='海淀区',filter='有团购',sort='按人气排序',save=True,details=True)
```
> 返回结果 results 为搜索到的相关店铺，具体内容,单个店铺的MongoDB数据库显示:
```json
{
    "_id" : ObjectId("5c3c88f265b2fd3134266c7b"),
    "店名" : "优享健身(金源店)",
    "星级" : "四星商户",
    "注册时间" : "2017-07-25T23:19:00",
    "地址" : " 远大路世纪金源燕莎B1层卜蜂莲花超市内南侧家电区",
    "人均" : 3526,
    "预订" : false,
    "分店url" : "http://www.dianping.com/brands/b93357498s45g45",
    "商铺图片" : "http://vfile.meituan.net/joymerchant/-1945301364589883676-23601423-1525363931678.jpg",
    "商铺标签" : "健身房",
    "纬度" : 39.9573,
    "经度" : 116.28518,
    "电话" : [ 
        "010-57159188"
    ],
    "店铺ID" : 93357498,
    "会员卡ID" : 0,
    "地区" : [ 
        "远大路"
    ],
    "expand" : 0,
    "poi" : "HEHHURZVVGIDGF",
    "promoId" : 0,
    "shopDealId" : 27807431,
    "shopPower" : 40,
    "hasSceneryOrder" : false,
    "点评数" : "118",
    "点评标签" : [ 
        "环境优雅(43)", 
        "服务热情(17)", 
        "设施很赞(15)", 
        "教练很棒(14)", 
        "器械齐全(7)", 
        "体验很棒(7)", 
        "干净卫生(4)", 
        "高大上(4)"
    ],
    "点评类别" : {
        "图片" : "55",
        "好评" : "85",
        "中评" : "7",
        "差评" : "26"
    },
    "评分" : {
        "设施" : "8.3",
        "环境" : "8.2",
        "服务" : "7.6"
    }
}
```
> * 多线程搜索下载相关店铺

多线程搜索与单线程搜索流程一致，只是搜索线程多开了而已，线程数为搜索结果的页数，最多为50个（大众点评目前单页最多个数）。启用多线程的话，由于使用代理IP，有可能同时
获取的代理多个线程都是同一个，所以在config.py加入了RANDOM_INTERVAL（随机等待间隔）防止多个线程使用同一个代理被封。

* 获取某个商铺的评分、星级、地址、电话、点评数、人均消费、点评标签、点评种类等

> 下例以获取id为507576的店铺信息为例
```python
from shop import Shop
store = Shop('507576')
store.get()
#店铺名
name = store.name
#店铺星级，50为五星，40为四星，35为三星半
stars = store.stars
#地址
address = store.address
#联系方式
phone = store.phone
#点评数
reviews = store.reviews
#人均消费
average = store.average
#顾客评分
scores = store.scores
#点评种类及数量
comment_kinds = store.comment_kinds
#点评标签及数量
review_tags = store.review_tags
```
> 返回结果 :
```text
'满福楼'
'50'
'朝阳门外大街8号蓝岛大厦东区六层(东大桥铁站D2出口)''
'64030992 64053088'
'18821'
'128'
{'口味': '9.1', '环境': '9.1', '服务': '9.1'}
{'图片': '3513', '好评': '17632', '中评': '355', '差评': '95'}
['回头客(404)', '干净卫生(253)', '上菜快(106)', '停车方便(59)', '夜景赞(5)', '请客(161)', '朋友聚餐(93)', '家庭聚餐(44)', '现做现卖(22)', '下午茶(9)']
```
* 获取下载保存某个商铺的加密点评信息，支持条数设定

> 获取点评需要使用cookie，具体使用参见“使用前”，默认保存数据进入数据库，具体的参数详情参见get_reviews函数注释。下例以获取店铺id为 507576 的商铺以第2页为起点的 300条加密点评为例:

```python
from comment import Comments
from dbhelper import Database
from config import MongoDB
dianpingDB = Database(MongoDB)
target_shop = Comments('50576',db=dianpingDB)
target_shop.get()
target_shop.get_reviews(tname='保存数据表名',count=300,frompage=2)
```
> 结果已经被存储在数据库中，MongoDB数据库中的单条点评数据内容具体为：
```json
{
	"_id" : ObjectId("5c3c914e65b2fd3384558c69"),
	"点评ID" : "496225994",
	"点评链接" : "http://www.dianping.com/review/496225994",
	"点评用户" : "好想吃好",
	"用户ID" : "781396343",
	"用户主页" : "http://www.dianping.com/member/781396343",
	"用户头像" : "https://p0.meituan.net/userheadpicbackend/83fe454da66682fcbd43aed7e716f7c5104831.jpg",
	"用户等级" : "lv5",
	"VIP用户" : true,
	"点评商铺" : "满福楼",
	"商铺ID" : "507576",
	"点评星级" : "50",
	"用户评价" : {
		"口味" : "非常好",
		"环境" : "非常好",
		"服务" : "非常好"
	},
	"点评时间" : "2019-01-13 21:17",
	"点评图片" : [
		"http://qcloud.dpfile.com/pc/chB7IwRZcpIwgAZu6ZkIE1Ts_aTNOyiGGbmIGbs4RjCN3JfGN-IioWlr9osF8hImjoJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg",
		"http://qcloud.dpfile.com/pc/zGhlhFul5cqBQs7e5Vz8vKGz21xv2xOlIEIwy7kf50p-NpRbr0UwQ7niAIDwKWOCjoJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg",
		"http://qcloud.dpfile.com/pc/Ve_jDe47G9v8Da_Hsy9MpZqCs0Fb67Yq6j2rkpqgN7H0kAawvhDXOXBa2ZnI1FIWjoJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg",
		"http://qcloud.dpfile.com/pc/StJvWhLl7MjtPi7VbNfYIR2I1IS9esxPO21bqfDKVaPygfipf3l2ctLCNDL5jbj1joJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg",
		"http://qcloud.dpfile.com/pc/7UmBsS10yRloypGc2Pp1pdlmdKP2hDzRhWT5wZLgI-JbnpM9T49yMmnt4yPiPxuwjoJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg",
		"http://qcloud.dpfile.com/pc/sI_CeStxWNFGJcOTa1bhmxOKkLGBEHBmXGaXkST7jk8t-HQzlOY35ADlO6UZvd_rjoJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg",
		"http://qcloud.dpfile.com/pc/fXFthqUVtnH64f56FytXNTHCV_h2ItUd8n-LqQllEf8Ho8itsBkcmVncTI8kIYxjjoJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg",
		"http://qcloud.dpfile.com/pc/7DrPJ4wMkZMQJQMwzrV_htFX28QHwS538qf9O7X1Hx0i8AgtQV76cj-_sKD6JTPFjoJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg",
		"http://qcloud.dpfile.com/pc/FZy3uddbXxAZkk2-J8EI7GFutnl-xTc7gEdOn8IsUFQrvkHyMac7eaNrOOmvIgmcjoJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg",
		"http://qcloud.dpfile.com/pc/px379Hd9MRRqOF6opKanBs8QEGc7UK5pjkSHtQoP9BrbMF6JuBDWN8BUF4VB5oV5joJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg",
		"http://qcloud.dpfile.com/pc/xwUMFgIHr8Uemd33o3rQMg6ktHU-4BMTzvInDCRMhkhXBw3IHLzmZnDdPoSzfFepjoJrvItByyS4HHaWdXyO_DrXIaWutJls2xCVbatkhjUNNiIYVnHvzugZCuBITtvjski7YaLlHpkrQUr5euoQrg.jpg"
	],
	"评论事件" : {
		"赞" : "4"
	},
	"点评内容" : "家里的抓到300元代金券，今天到店品尝美味。乘直梯到六楼，进店入眼就是放着小铜锅的餐桌，才十一点多点儿大厅就几乎满员。仨人按大众点评的推荐及个人喜好点了「牛骨高汤」「手切鲜羊肉」「羊上脑」「手切精品鲜黄瓜条」「精品太阳肉」仨「羊肉串儿」「糖卷果」肚子实在没地方了，可精品还没吃，只好「烤火烧」「炸火烧」「肉沫烧饼」「烤腰子」各点一个，三人分着尝口儿。点的肉涮着吃没一点儿膻味儿，还很嫩，麻酱蘸料很好吃！特别是腰子烤的牛极了，外面包的油焦脆，里面的腰子火候正好，美味！各种火烧也很好吃！[服务]服务很到位！锅里刚有点儿沫子，服务小妹就帮着撇出去，最后还送了果盘，看我们挺爱吃的，又提示我们果盘还可以续，并送了我们2019年新挂历，谢谢！！"
}
```

## ToDo

* 如果想要抓取多个商铺的点评数据，可以使用多个账户+多代理+UA池来绕过反爬
* 尝试使用selenium对爬取点评数据进行验证码滑动验证
* 使用手机接码平台注册多个账户进行模拟登陆后获取cookie进行爬取点评数据
