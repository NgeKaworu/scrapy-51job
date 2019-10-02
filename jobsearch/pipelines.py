# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import pymongo
import jieba.analyse
from datetime import datetime
from scrapy.exceptions import DropItem


class JobsearchPipeline(object):
    # 原始筛选, 用jieba测试新的筛选
    def __init__(self):
        self.keyWord = r'开发|实习|初|中|高|级|工程|软件|硬件|程序|技术|佛山|管理|程序|员|生|师|web|it'

    @staticmethod
    def _filter(value, keyWord):
        return re.sub(keyWord, ' ', value.lower().strip())

    def process_item(self, item, spider):
        if spider.name == '51job':
            item['title'] = self._filter(item['title'], self.keyWord)
            if item['title']:
                return item
            else:
                # 去空
                raise DropItem('Invalid Title')

        if spider.name == 'frontend':
            item['detail'] = self._filter(item['detail'], self.keyWord)
            if item['detail']:
                return item
            else:
                # 去空
                raise DropItem('Invalid detail')
        return item


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.createDate = datetime.now().strftime('%Y/%m/%d')
        self.cloud = ''
        self.detail = ''
        self.synonym = [
            (r'javascript', 'js'),
            (r'.net', 'net'),
            (r'bootstrap', 'bs'),
            (r'css3', 'css'),
            (r'html5|html', 'h5'),
            (r'angularjs', 'angular'),
            (r'reactjs', 'react'),
            (r'vuejs', 'vue')
        ]

    # 分词+词频统计
    @staticmethod
    def _analyse(sentence, synonym, allowPOS):
        # 根据规则转换近义词
        newValue = sentence
        for i in synonym:
            newValue = re.sub(i[0], i[1], newValue)

        topWord = jieba.analyse.extract_tags(
            newValue, topK=50, withWeight=True, allowPOS=allowPOS)
        return [{'word': i[0], 'count': i[1]} for i in topWord]

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def process_item(self, item, spider):
        if spider.name == '51job':
            self.cloud += item['title']

        if spider.name == 'frontend':
            self.db['front'].insert(
                {**item, "createTime": self.createDate},
            )
            self.detail += item['detail']
        return item

    def close_spider(self, spider):
        if spider.name == '51job':
            self.db['cloud'].insert_many(self._analyse(
                self.cloud, self.synonym, allowPOS=('eng', 'f')))

        # 这里是相当于做成缓存放一个新表
        # 更好的做法是在api那里调用时做计算
        # 然后缓存到redis中
        if spider.name == 'frontend':
            self.db['frontdetail'].update(
                {"createTime": self.createDate},
                {"$set": {
                    "createTime": self.createDate,
                    "classify": self._analyse(self.detail, self.synonym, allowPOS=('eng',)),
                },
                },
                True
            )

        self.client.close()
