# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re, pymongo, time
from scrapy.exceptions import DropItem
from collections import Counter



class JobsearchPipeline(object):
    # 原始筛选, 用jieba测试新的筛选
    # def __init__(self):
    #     self.keyWord = r'开发|实习生|初|中|高|级|工程师|软件|硬件|程序员|技术员|\(.*\)|佛山|web|it|（.*）|\/'

    def process_item(self, item, spider):
        if spider.name == '51job':
            # item['title'] = re.sub(self.keyWord, '', item['title'].lower().strip())
            if item['title']:
                return item
            else:
                # 去空
                raise DropItem('Invalid Title')
        return item


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.cloud = ''
        self.detail = ''
    

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri = crawler.settings.get('MONGO_URI'),
            mongo_db = crawler.settings.get('MONGO_DB')
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
    
    def process_item(self, item, spider):
        if spider.name == '51job':
            self.cloud += item['title']

        if spider.name == 'frontend':
            self.detail += item['detail']
        

        return item

    def close_spider(self, spider):
        if spider.name == '51job':
            self.db['cloud'].insert({'title': 'cloud', 'cloud': self.cloud, 'query_date': time.time()})

        if spider.name == 'frontend':
            self.db['detail'].insert({'title': 'cloud', 'detail': self.cloud, 'query_date': time.time()})

        self.client.close()

