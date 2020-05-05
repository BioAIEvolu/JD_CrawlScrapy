# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.spiders import  Rule #CrawlSpider,
from scrapy_redis.spiders import CrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
import re
import pprint


class JdSpiderSpider(CrawlSpider):
    name = 'jd_spider'
    allowed_domains = ['jd.com', 'p.3.cn']
    start_urls = ['https://m.jd.com/']

    rules = {
        Rule(LinkExtractor(allow=()), # 设置规则第一次过滤的时候，允许所有链接都抓取
        callback='parse_shop', #用字符串方式是为了与旧版本兼容
        follow=True # 跟随所有链接。不断地抓取新链接，然后回调给解析函数
        ), 
        
    }
  
    def parse_shop(self, response): #由于parse被通用爬虫CrawlSpider占用了，所以需要改名字，不能用parse
        print('ok1')
        ware_id_list = list()
        url_group_shop = LinkExtractor(allow=(r'(http|https)://item.jd.com/product/\d+.html')).extract_links(response) # 过滤商品链接的url
        re_get_id = re.compile(r'(http|https)://item.jd.com/product/(\d+).html')

        for url in url_group_shop:
            print('ok2')
            ware_id =  re_get_id.search(url.url).group(2)
            ware_id_list.append(ware_id)

        for id in ware_id_list:
            print('ok3')
            """
            https://item.m.jd.com/ware/detail.json?wareId={}
            https://p.3.cn/prices/mgets?type=1&skuIds=J_{}
            """
            yield Request('https://item.m.jd.com/ware/detail.json?wareId={}'.format(id),
                            callback=self.detail_pag,
                            meta={'id':id},
                            priority=5)
            

    def detail_pag(self, response):
        print('ok4')
        _ = self
        data = json.loads(response.text)
        
        yield Request('https://p.3.cn/prices/mgets?type=1&skuIds=J_{}'.format(response.meta['id']),
                            callback=self.get_price_pag,
                            meta={'id':response.meta['id'],
                                  'data': data},
                            priority=10)

    def get_price_pag(self, response):
        print('ok5')
        _ = self
        data = json.loads(response.text)
        detail_data = response.meta['data']
        ware_id = response.meta['id']

        item = {
            'detail': detail_data,
            'price': data,
            'ware_id': ware_id
            }
        
        pprint.pprint(item)
        yield item
