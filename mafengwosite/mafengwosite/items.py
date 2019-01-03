# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TravelReviewItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    source = scrapy.Field()       # 数据来源
    user_id = scrapy.Field()      # 评论用户id
    avater = scrapy.Field()       # 评论用户头像
    level = scrapy.Field()        # 评论用户等级
    useful_num = scrapy.Field()   # 评论有用数
    star = scrapy.Field()       # 评论星级
    content = scrapy.Field()      # 评论内容
    user_name = scrapy.Field()    # 用户名
    time = scrapy.Field()         # 评论时间
    # image_urls = scrapy.Field()    # 评论照片url
    # image_urlb = scrapy.Field()    # 评论照片url
    # image_id = scrapy.Field()     # 评论对应的照片


class TravelSiteItem(scrapy.Item):
    review = scrapy.Field()      # 景点评论内容
    location = scrapy.Field()    # 景点具体位置
    site_name = scrapy.Field()   # 景点名
    site_id = scrapy.Field()     # 景点id
    review_num = scrapy.Field()  # 评论量
    # read_num = scrapy.Field()    # 浏览量
