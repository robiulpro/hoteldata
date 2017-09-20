import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

def dispatch(event, context):
    configure_logging({'LOG_ENABLED': False})
    hotels = event.get('hotels')

    print '###########PAYLOAD#############'
    print hotels
    print '\n'

    process = CrawlerProcess(get_project_settings())

    for hotel in hotels:
        print hotel['name']
        process.crawl('trivago', hotel=hotel['name'], roomType=hotel['roomType'])
    #process.start(stop_after_crawl=False)
    process.start()
