#coding:utf-8
import asyncio
import aiohttp
import json
import os

class Scheduler(object):
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(__file__), 'config')

    def load_config(self):
        global settings, xpath, arguments_map
        xpath_path = os.path.join(self.config_dir, 'xpath.json')
        settings_path = os.path.join(self.config_dir, 'settings.conf')
#        map_path = os.path.join(self.config_dir, 'map.json')
        districts_path = os.path.join(self.config_dir, 'districts.json')

        with open(xpath_path) as f:
            self.xpath = json.loads(f.read())
        with open(settings_path) as f:
            self.settings = json.loads(f.read())
#        with open(map_path) as f:
#            self.argument_map = json.loads(f.read())
        with open(districts_path) as f:
            self.districts_json = json.loads(f.read())


    async def start(self):
        print("Loading config...")
        self.load_config()
        print("Load config successfully.")

        from spider.listSpider import listSpider
        from spider.reportSpider import reportSpider
        conn = aiohttp.TCPConnector(limit=self.settings['tcp_limit'])
        async with aiohttp.ClientSession(connector=conn) as session:
            print("Crawling report_id...")
            self.list_spider = listSpider(self.settings, self.districts_json, session)
            self.report_list = await self.list_spider.start()
            print("Crawl report_id successfully.")

            print("Crawling report...")
            self.report_spider = reportSpider(self.settings, self.report_list, self.xpath, self.districts_json, session)
            await self.report_spider.start()


if __name__ == "__main__":
    scheduler = Scheduler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scheduler.start())
    loop.close()








