import scrapy
import requests
import time
from bs4 import BeautifulSoup
from mafengwosite.items import TravelSiteItem, TravelReviewItem


class Data_Crawl(scrapy.Spider):
    name = 'mafengwosite'
    allowed_domains = ['www.mafengwo.cn', 'pagelet.mafengwo.cn', 'm.mafengwo.cn']
    start_urls = "浙江"
    host = "http://www.mafengwo.cn/search/s.php?q="

    def start_requests(self):
        page_num = 50
        # for i in range(len(self.start_urls)):
        for j in range(41, page_num + 1):
            yield scrapy.Request(self.host + self.start_urls + "&p=" + str(j) + "&t=poi&kt=1", callback=self.parse_info)

    def parse_info(self, response):
        ids = response.xpath('//div[@class="ct-text "]/h3/a/@href').re(r'\d+')
        if len(ids) == 0:
            ids = response.xpath('//div[@class="ct-text"]/h3/a/@href').re(r'\d+')
        # urls = response.xpath('//div[@class="ct-text "]/h3/a/@href').extract()
        # if len(urls) == 0:
        #     urls = response.xpath('//div[@class="ct-text"]/h3/a/@href').extract()
        names = response.xpath('//div[@class="ct-text "]/h3/a/text()').extract()
        if len(names) == 0:
            names = response.xpath('//div[@class="ct-text"]/h3/a/text()').extract()
        # infos = response.xpath('//ul[@class="seg-info-list clearfix"]').extract()
        # titles = response.xpath('//div[@class="ct-text "]/h3').extract()
        location = response.xpath('//ul[@class="seg-info-list clearfix"]/li[1]/a/text()').extract()
        review_num = response.xpath('//ul[@class="seg-info-list clearfix"]/li[2]/a/text()').extract()

        for i in range(len(ids)):
            item = TravelSiteItem()
            item["location"] = location[i]
            # item["info"] = BeautifulSoup(infos[i], "lxml").get_text().replace("\n", "").replace(" ", "")
            item["site_id"] = ids[i]
            item["review_num"] = review_num[i].replace("点评(", "").replace(")", "")
            item["site_name"] = names[i].replace("景点 - ", "")
            from_data = {"poiid": ids[i], "page": "1", "type": "keyword", "wordId": "0"}
            yield scrapy.FormRequest(
                url="https://m.mafengwo.cn/poi/poi/comment_page",
                formdata=from_data,
                meta={"item": item, "ids": ids[i], "review_num": item["review_num"]},
                callback=self.parse_review)

    def parse_review(self, response):
        # self.log('fetched %s' % response.url)
        print("22222222222222222222222222222222222222")
        data_item = response.meta["item"]
        data_item["review"] = []
        url = "https://m.mafengwo.cn/poi/poi/comment_page"
        headers = {
            'user-agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, '
                          'like Gecko) Chrome/68.0.3440.106 Mobile Safari/537.36'
        }
        comment_num = response.meta["review_num"]
        for page in range(1, 11):
            form_data = {"poiid": response.meta["ids"], "page": page, "type": "keyword", "wordId": "0"}
            content = requests.post(url, data=form_data, headers=headers, timeout=30)
            content = content.text.encode('utf-8').decode('unicode_escape').replace("{\"html\":\"", "")\
                .replace("\"moreComment:true\"", "").replace("\\", "")
            if content:
                soup = BeautifulSoup('<html><head></head><body>' + content + '</body></html>', 'lxml')
                tmp = soup.find_all("li")
                if len(tmp) > 0:
                    for i in range(len(tmp)):
                        review_item = TravelReviewItem()
                        review_item["source"] = "mfw"
                        review_item["user_id"] = tmp[i].find("div", attrs={"class": "userbar"}).a.get('href').replace\
                            ("/u/", "").replace('.html', '')
                        review_item["avater"] = tmp[i].find("div", attrs={"class": "userbar"}).a.img.get("src")
                        review_item["user_name"] = tmp[i].find("span", attrs={"class": "username"}).get_text().replace(
                            " ", "").replace("\n", "")
                        review_item["level"] = tmp[i].find("span", attrs={"class": "grade"}).get_text()\
                            .replace("Lv.", " ")
                        review_item["star"] = int(int(tmp[i].find("div", attrs={"class": "stars"}).span.get("style")
                             .replace("width:","").replace("%","")) / 20)
                        review_item["content"] = tmp[i].find("div", attrs={"class": "context line5"}).get_text()\
                            .replace("\n", "").replace(" ", "").replace("\r", "")
                        review_item["useful_num"] = tmp[i].find("div", attrs={"class": "bottom"}).a.get_text()\
                            .replace(" ", "").replace("\n", "")
                        review_item["time"] = tmp[i].find("div", attrs={"class": "time"}).get_text().replace(" ", "")\
                            .replace("\n", "")
                        data_item['review'].append(review_item)
                time.sleep(10)
        yield data_item

        # # -*-针对每个景点的评论总页数 -*-content
        # try:
        #     total_page = int(soup.find("a", attrs={"class": "pi pg-last"}).get("data-page"))
        # except:
        #     total_page = 1
        # for page in range(1, total_page + 1):
        #     url = "http://pagelet.mafengwo.cn/poi/pagelet/poiCommentListApi?params={\"poi_id\":\"%s\",\"page\":%s,\"" \
        #           "just_comment\":1}"
        #     soup = json.loads(requests.get(url % (data_item["site_id"], str(page))).text)["data"]["html"]
        #     soup = BeautifulSoup('<html><head></head><body>' + soup + '</body></html>', 'lxml')
        #     tmp = soup.find_all("li")
        #     if len(tmp) > 0:
        #         for i in range(len(tmp)):
        #             review_item = TravelReviewItem()
        #             review_item["source"] = "mfw"
        #             review_item["user_id"] = tmp[i].find("a", attrs={"class": "avatar"}).get('href').replace("/u/", "")\
        #                                         .replace(".html", "")
        #             review_item["avatar"] = tmp[i].find("a", attrs={"class": "avatar"}).img.get("src")
        #             review_item["level"] = tmp[i].find("span", attrs={"class": "level"}).get_text()
        #             try:
        #                 review_item["useful_num"] = int(tmp[i].find("span", attrs={"class": "useful-num"}).get_text())
        #             except:
        #                 review_item["useful_num"] = 0
        #             review_item["star"] = int(tmp[i].find("span", attrs={"class": "s-star"}).get("class")[1].replace
        #                                       ("s-star", ""))
        #             review_item["user_name"] = tmp[i].find("a", attrs={"class": "name"}).get_text()
        #             # 爬取图片地址
        #             try:
        #                 review_item["image_urls"] = [item.img.get("src") for item in
        #                                              tmp[i].find("div", attrs={"class": "rev-img"}).find_all("a")]
        #                 review_item["image_urlb"] = ["http://www.mafengwo.cn" + item.get("href") for item in
        #                                              tmp[i].find("div", attrs={"class": "rev-img"}).find_all("a")]
        #                 review_item["image_id"] = [
        #                     item.get("href").replace("/photo/poi/", "").replace(".html", "") for item in
        #                     tmp[i].find("div", attrs={"class": "rev-img"}).find_all("a")]
        #             except:
        #                 review_item["image_urls"] = []
        #                 review_item["image_urlb"] = []
        #             # -*-图片爬取
        #             if len(review_item["image_urls"]) != 0:
        #                 filepath1 = 'travel_crawl/img'
        #                 print('准备爬取图片...')
        #                 if os.path.exists(filepath1) is False:
        #                     os.mkdir(filepath1)
        #                 for j in range(len(review_item["image_urls"])):
        #                     temp1 = filepath1 + '/%s.jpg' % review_item["image_id"][j]
        #                     urllib.request.urlretrieve(review_item["image_urls"][j], temp1)
        #         review_item["content"] = tmp[i].find("p", attrs={"class": "rev-txt"}).get_text()
        #         review_item["time"] = tmp[i].find("span", attrs={"class": "time"}).get_text()
        #         data_item['review'].append(review_item)
        #     time.sleep(5)
        # yield data_item
