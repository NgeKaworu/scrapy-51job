# -*- coding: utf-8 -*-
import scrapy
from jobsearch.items import JobsearchItem

class FrontendSpider(scrapy.Spider):
    name = 'frontend'
    allowed_domains = ['m.51job.com']
    start_urls = ['https://m.51job.com/search/joblist.php?keyword=%E5%89%8D%E7%AB%AF&jobarea=030600']

    def parse(self, response):
        for href in response.css('.e.eck').xpath('./@href'):
            yield response.follow(href, callback=self.parseDetail)

        for href in response.css('a.next').xpath('./@href'):
            yield response.follow(href, callback=self.parse)

    def parseDetail(self, response):
        item = JobsearchItem()
        detail = response.xpath('//article').xpath('string(.)').extract_first().strip()
        item['detail'] = detail
        yield item