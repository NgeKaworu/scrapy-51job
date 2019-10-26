# -*- coding: utf-8 -*-
import scrapy
from jobsearch.items import JobsearchItem


class FrontendSpider(scrapy.Spider):
    name = 'frontend'
    allowed_domains = ['m.51job.com']
    start_urls = ['https://m.51job.com/search/joblist.php?keyword=%E5%89%8D%E7%AB%AF&jobarea=030600',
                  'https://m.51job.com/search/joblist.php?keyword=%E5%89%8D%E7%AB%AF&jobarea=040000']

    def parse(self, response):
        for href in response.css('.e.eck').xpath('./@href'):
            yield response.follow(href, callback=self.parseDetail)

        for href in response.css('a.next').xpath('./@href'):
            yield response.follow(href, callback=self.parse)

    def parseDetail(self, response):
        item = JobsearchItem()
        # item['detail'] = response.xpath('//article').xpath('string(.)').extract_first().strip()
        # same as next
        item['detail'] = response.xpath(
            'string(//article)').extract_first().strip()
        item['salary'] = response.xpath(
            'string(//p[@class="jp"])').extract_first()
        item['experience'] = response.xpath(
            'string(//span[@class="s_n"])').extract_first()
        item['area'] = response.xpath(
            'string(//div[@class="jt"]/em)').extract_first()

        yield item
