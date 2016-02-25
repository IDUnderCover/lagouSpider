# -*- coding: utf-8 -*-
from scrapy.spider import BaseSpider
from scrapy.selector import XPathSelector
from scrapy.http import Request
from scrapy.http import FormRequest
import json
from lagouSpider.items import Position

class LagouSpider(BaseSpider):
    name = "lagou"
    allowed_domains = ["lagou.com"]
    start_urls = (
        'http://www.lagou.com/',
        )

    # keyword 搜索的关键词
    # pagenum 页数，第一次请求为1，来获取总页数
    # callbackFunc 回调函数
    def formRequest(self, keyword, pagenum, callbackFunc):
        # kd key word
        # pn Page number
        # first  false
        return FormRequest(
                    'http://www.lagou.com/jobs/positionAjax.json',
                    formdata = {
                        'px':'new',          # 最新
                        'first':'fasle',     # unknown
                        'pn':pagenum,        # 页数
                        'kd':keyword,        # 关键词  @
                        },
                        callback=callbackFunc,
                        meta={'keyword':keyword}
                       )

    def parse(self, response):
        print "la gou spider is running.."
        keys = 'docker,Django,python,javascript'
        for key in keys.split(','):
            yield self.formRequest(key,'1',self.parsePages)

    def parsePages(self, response):
        res = json.loads(response.body)
        keyword = response.request.meta['keyword']
        pageCount = res['content']['totalPageCount'] # 获取该关键词的搜索结果总页数
        for page in range(pageCount):
           yield self.formRequest(keyword, str(page+1), self.parseItem)

    def parseItem(self, response):
        # pos = Position()
        result_list = json.loads(response.body)['content']['result']  # this json contain a list
        for res in result_list:
            yield res


