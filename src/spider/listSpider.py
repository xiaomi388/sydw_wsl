import aiohttp
import asyncio
import async_timeout
import tqdm
from lxml import etree as ET
from tenacity import *

from logger_helper import logger


class listSpider(object):
    def __init__(self, settings, districts_json, session):
        global max_attempts
        self.session = session
        self.settings = settings
        self.districts_json = districts_json
        self.report_list = set()

    def load_district(self, district_code):
        index = self.districts_json['index'][str(district_code)]
        res = self.districts_json['districts'][index[0]]
        if index[1] != -1:
            res = res[index[1]]
            if index[2] != -1:
                res = res[index[2]]
        return res

    def load_districts(self):
        self.districts_list = self.settings['districts']

        for province in self.settings['cities_in_provinces']:
            province = self.load_district(province)
            for city in province['sub_districts']:
                self.districts_list.append(city['district_code'])

        for city in self.settings['counties_in_cities']:
            city = self.load_district(city)
            for county in city['sub_districts']:
                self.districts_list.append(county['district_code'])

        for province in self.settings['counties_in_provinces']:
            province = self.load_district(province)
            for city in province['sub_districts']:
                for county in city['sub_districts']:
                    self.districts_list.append(county['district_code'])

    @retry(retry=retry_if_exception_type(asyncio.TimeoutError))
    async def get_page_num(self, district_code, year):
        url = self.settings['list_url'].format(district_code, year, 1)

        # get_page
        with async_timeout.timeout(self.settings['timeout']):
            async with self.session.get(url) as response:
                html = ET.HTML(await response.text())
                page_num = html.xpath("//select[@id='selectPage']/option[last()]/text()")
                if len(page_num) != 0:
                    return int(page_num[0])
                else:
                    return 0

    @retry(retry=retry_if_exception_type(asyncio.TimeoutError))
    async def get_report_id(self, district_code, page_id, year):
        url = self.settings['list_url'].format(district_code, year, page_id)
        with async_timeout.timeout(self.settings['timeout']):
            async with self.session.get(url) as response:
                html = ET.HTML(await response.text())
                self.report_list.update([ (res[23:29], res[30:39]) for res in html.xpath("//tr[@class='STYLE19']/td[3]/a/@href") ])
        return

    async def crawl(self, district_code, year):
        logger.info("crawling report id for district {0} in year {1}".format(district_code, year))
        page_num = await self.get_page_num(district_code, year)
        if page_num == 0:
            return
        tasks = [ self.get_report_id(district_code, page_id+1, year) for page_id in range(page_num) ]
        await asyncio.wait(tasks)
        logger.info("crawl report id for district {0} in year {1} successfully".format(district_code, year))

    async def start(self):
        print("Loading district code...")
        self.load_districts()
        print("Loading district code successfully.")

        tasks = list()
        for year in self.settings['years']:
            for district_code in self.districts_list:
                tasks.append(self.crawl(district_code, year))
        try:
            [ await f for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)) ]
        except Exception as e:
            logger.error("A fatal error occured when crawling report id! Reason: {}".format(e))
            print('A fatal error occured when crawling report! Reason: {}'.format(e))

            exit()
        return self.report_list

