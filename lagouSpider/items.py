# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item,Field

class LagouItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass


# this Item is deprecated due to the response is json format
class Position(Item):
    positionName = Field()
    positionId = Field()
    positionTyep = Field()
    workYear = Field()
    education = Field()
    jobNature = Field()
    companyId = Field()
    companyName = Field()
    companyLogo = Field() #prefix www.lagou.com/
    industryField = Field()
    financeStage = Field()
    companyShortName = Field()
    city = Field()
    salary = Field()
    positionFirstType = Field()
    positionAdvantage = Field()
    createTime = Field()
    companyLabelList = Field()
    leaderName = Field()
    companySize = Field()
    score = Field()
    calcScore = Field()
    orderBy = Field()
    showOrder = Field()
    haveDeliver = Field()
    adWord = Field()
    randomScore = Field()
    countAdjusted = Field()
    adjustScore = Field()
    relScore = Field()
    formatCreateTime = Field()
    positionTypesMap = Field()
    createTimeSort = Field()
    hrScore = Field()