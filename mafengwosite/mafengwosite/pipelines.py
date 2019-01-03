# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from scrapy import log
from mafengwosite.items import TravelSiteItem


class MafengwositePipeline(object):
    def __init__(self):
        client = pymongo.MongoClient("localhost", 27017)
        db = client["mafengwosite"]
        self.spot_review = db["spot_review"]

    def process_item(self, item, spider):
        if isinstance(item, TravelSiteItem):
            try:
                self.spot_review.insert(dict(item))
                log.msg("New addded to MongoDB database!", level=log.DEBUG, spider=spider)
            except Exception:
                pass
        return item
