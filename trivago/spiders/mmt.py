import scrapy
from scrapy import signals
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import json
import requests


class MmtSpider(scrapy.Spider):
    name = "mmt"
    #url = "https://www.trivago.in/?aDateRange%5Barr%5D=2017-10-25&aDateRange%5Bdep%5D=2017-10-26&aPriceRange%5Bfrom%5D=0&aPriceRange%5Bto%5D=0&iPathId=84767&aGeoCode%5Blng%5D=73.831543&aGeoCode%5Blat%5D=15.495606&iGeoDistanceItem=2400908&iGeoDistanceLimit=20000&aCategoryRange=0%2C1%2C2%2C3%2C4%2C5&aOverallLiking=1%2C2%2C3%2C4%2C5&sOrderBy=relevance%20desc&bTopDealsOnly=false&iRoomType=7&cpt=240090802&iIncludeAll=0&iViewType=0&bIsSeoPage=false&bIsSitemap=false&"
    #url = "https://www.makemytrip.com/pwa-hlp/hotelsCityList?term=asansol"

    def __init__(self, term="", *args, **kwargs):
        super(MmtSpider, self).__init__(*args, **kwargs)
        self.url = "https://www.makemytrip.com/pwa-hlp/hotelsCityList?term="+term

        # dcap = dict(DesiredCapabilities.PHANTOMJS)
        # dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36")
        #
        # self.driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any', '--web-security=false'])
        # self.driver.set_window_size(1366,768)



    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(MmtSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_error, signal=signals.spider_error)
        return spider

    def spider_error(self, failure, response, spider):
        print '###########SPIDER ERROR#############'
        print failure
        print '\n'
        spider.logger.info('Spider failed due to error!!: %s', spider.name)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)




    def parse(self, response):

        payload = self.generatePayload(response)
        # self.getSearchItems(payload)

        # print "==========PAYLOAD========"
        # print payload


        #print hotels_blocks;
        yield {
            'hotels':'test hotel'
        }



    def getIpathData(self,keyword):
        url = "https://www.trivago.in/search/in-IN-IN/v11_09_2_ao_cache/suggest_concepts"
        querystring = {"q":keyword}
        headers = {
        'x-user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 FKUA/website/41/website/Desktop",
        'cache-control': "no-cache"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        response_data = json.loads(response.text)

        iPathId = response_data['result'][0]['app']['iPathId']
        cpt = response_data['result'][0]['id']
        if 'iGeoDistanceItem' in response_data['result'][0]['app'].keys():
            iGeoDistanceItem = response_data['result'][0]['app']['iGeoDistanceItem']
        else:
            iGeoDistanceItem = 0
        path_data = {
            'iPathId':iPathId,
            # 'cpt':cpt,
            # 'iGeoDistanceItem':iGeoDistanceItem
        }
        return path_data






    def generatePayload(self,response):
        data = json.loads(response.body)
        item = data['response']['docs'][1]
        print item



    def getSearchItems(self,payload):
        url = "https://www.trivago.in/search/region"
        # headers = {
        # 'x-user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 FKUA/website/41/website/Desktop",
        # 'content-type': "application/json",
        # 'cache-control': "no-cache"
        # }
        # response = requests.request("GET", url, data=json.dumps(payload), headers=headers)
        # response_data =  json.loads(response.content)

        querystring = {"iGeoDistanceItem":"1236122","cpt":"123612202","iPathId":"84767","iRoomType":"7"}
        headers = {
        'x-user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36 FKUA/website/41/website/Desktop",
        'cache-control': "no-cache"
        }
        response = requests.request("GET", url, headers=headers, params=payload)
        response_data = json.loads(response.text)

        # print "=========API RESPONSE========="
        # print response_data['items']
        for item in response_data['items']:
            print item['name']
