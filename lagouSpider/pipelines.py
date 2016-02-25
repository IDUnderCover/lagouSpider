# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json




class LagouspiderPipeline(object):
    def __init__(self):
        self.output = 'positions.json'
    def process_item(self, item, spider):
        with open(self.output,'a+') as f:
            f.write(json.dumps(item)+'\n')
