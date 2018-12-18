# -*- coding: utf-8 -*-
import scrapy
from jobsearch.items import JobsearchItem


class A51jobSpider(scrapy.Spider):
    name = '51job'
    allowed_domains = ['m.51job.com']
    start_urls = ['https://m.51job.com/search/joblist.php?funtype=0107']

    def parse(self, response):
        item = JobsearchItem()
        for h in response.css('.e.eck'):
            item['title'] = h.css('span::text').extract_first()
            yield item

        for href in response.css('a.next').xpath('./@href'):
            yield response.follow(href, callback=self.parse)
