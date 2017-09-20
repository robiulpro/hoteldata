import scrapy
from scrapy import signals

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import re


import os
import time

import json
import requests

import datetime

from scrapy.utils.project import get_project_settings



class TrivagoSpider(scrapy.Spider):
    name = "trivago"

    def __init__(self, hotel="", roomType="1", *args, **kwargs):
        super(TrivagoSpider, self).__init__(*args, **kwargs)

        self.url = "https://www.trivago.in/search/in-IN-IN/v11_09_2_ao_cache/suggest_concepts?q="+str(hotel)
        self.roomType = roomType
        self.settings = get_project_settings()




    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(TrivagoSpider, cls).from_crawler(crawler, *args, **kwargs)
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

        ipathData = self.getIpathData(response)
        dealsData = self.getDealsData(ipathData)

        response = {
            'title': re.sub(r'[{}]', '', ipathData['title']),
            'itemId': ipathData['iGeoDistanceItem'],
            'deals': dealsData
        }

        print "==========RESPONSE DATA========"
        print response


        #print hotels_blocks;
        yield response



    def getIpathData(self,response):
        response_data = json.loads(response.body)

        iPathId = response_data['result'][0]['app']['iPathId']
        cpt = response_data['result'][0]['id']
        title = response_data['result'][0]['tt']
        if 'iGeoDistanceItem' in response_data['result'][0]['app'].keys():
            iGeoDistanceItem = response_data['result'][0]['app']['iGeoDistanceItem']
        else:
            iGeoDistanceItem = 0
        payload = {
            'iPathId':iPathId,
            'cpt':cpt,
            'iGeoDistanceItem':iGeoDistanceItem,
            'title':title
        }
        return payload



    def getDealsData(self,ipathData):

        today = str(datetime.date.today())
        tomorrow = str(datetime.date.today() + datetime.timedelta(1))

        url = "https://www.trivago.in/?aDateRange[arr]="+str(today)+"&aDateRange[dep]="+str(tomorrow)+"&iRoomType="+str(self.roomType)+"&iPathId="+str(ipathData['iPathId'])+"&iGeoDistanceItem="+str(ipathData['iGeoDistanceItem'])
        driver = self.getChromeDriver()
        #driver = self.getPhantomDriver()
        driver.get(url)
        deals = []

        try:
            more_button = driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ol.hotellist:first-child button.deal-other__more")))
            more_button.click()

            deals_container = driver.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ol.hotellist:first-child div.sl-box__content")))
            items = deals_container.find_elements_by_css_selector("div.sl-deal")

            for item in items:
                price = item.find_element_by_css_selector('span.sl-deal__btn-lbl').text
                provider = item.find_element_by_css_selector('img.sl-deal__logo-img').get_attribute("title")

                price = map(str, re.findall(r'\d+', price))

                deal = {
                    'provider': provider,
                    'price': ''.join(price)
                }
                deals.append(deal)

        except TimeoutException:
            print("data not loaded yet")

        time.sleep(5)
        driver.quit()
        return deals




    def getChromeDriver(self):
        driver_path = self.settings.get('PROJECT_ROOT')+'/chromedriver'
        # = '/var/www/ENV/trivago/trivago/chromedriver'
        options = webdriver.ChromeOptions()
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-web-security')
        options.add_argument('--no-referrers')
        options.add_argument("'chrome.prefs': {'profile.managed_default_content_settings.images': 2}")

        driver = webdriver.Chrome(executable_path=driver_path,chrome_options=options)
        driver.wait = WebDriverWait(driver, 5)
        return driver


    def getPhantomDriver(self):
        headers = { 'Accept':'*/*',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'en-US,en;q=0.8',
        'Cache-Control':'max-age=0',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
        }

        for key, value in enumerate(headers):
            webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

        driver_path = self.settings.get('PROJECT_ROOT')+'/phantomjs'
        #driver_path = '/var/www/ENV/trivago/trivago/phantomjs'

        service_args = [
            '--disk-cache=false',
            '--load-images=no'
        ]

        driver = webdriver.PhantomJS(executable_path=driver_path,service_args=service_args,service_log_path=os.path.devnull)
        driver.wait = WebDriverWait(driver, 5)
        return driver
