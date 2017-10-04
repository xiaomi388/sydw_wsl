#coding:utf-8
import asyncio
import aiohttp
import json
import os

from logger_helper import logger

class Scheduler(object):
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(__file__), 'config')

    def load_config(self):
        global settings, xpath, arguments_map
        xpath_path = os.path.join(self.config_dir, 'xpath.json')
        settings_path = os.path.join(self.config_dir, 'settings.conf')
        districts_path = os.path.join(self.config_dir, 'districts.json')

        with open(xpath_path) as f:
            self.xpath = json.loads(f.read())
        with open(settings_path) as f:
            self.settings = json.loads(f.read())
        with open(districts_path) as f:
            self.districts_json = json.loads(f.read())


    async def start(self):
        from spider.listSpider import listSpider
        from spider.reportSpider import reportSpider

        print("Loading config...")
        logger.info("Loading config")
        self.load_config()
        print("Load config successfully.")
        logger.info("Loading config complete")

        conn = aiohttp.TCPConnector(limit=self.settings['tcp_limit'])
        async with aiohttp.ClientSession(connector=conn) as session:
            await session.get('http://search.gjsy.gov.cn:9090/queryAll/searchFrame?districtCode=110000&checkYear=2016&sydwName=&selectPage=1')
            if os.path.exists('.job') and \
                input("You have unsave job, do you still want to continue the job last time? y/n:") != 'n':
                with open('.job', 'r') as f:
                    self.report_list = set([ (i.split(',')[0], i.split(',')[1]) for i in f.read().splitlines() ])
                    os.remove('.job')
            else:
                    print("Crawling report_id...")
                    logger.info("Crawling report id")
                    self.list_spider = listSpider(self.settings, self.districts_json, session)
                    self.report_list = await self.list_spider.start()
                    print("Crawl report_id successfully.")
                    logger.info("Crawl report id successfully")

            print("Crawling report...")
            logger.info("Crawling report")
            self.report_spider = reportSpider(self.settings, self.report_list, self.xpath, self.districts_json, session)
            await self.report_spider.start()


if __name__ == "__main__":
    scheduler = Scheduler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scheduler.start())
    loop.close()

