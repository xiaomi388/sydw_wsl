#coding:utf-8
import atexit
import asyncio
import aiohttp
import async_timeout
import lxml.etree as ET
import tqdm
from tenacity import *

from pipeline import reportPipeline
from logger_helper import logger


class reportSpider(object):
    def __init__(self, settings, report_list, xpath, districts_json, session):
        self.settings = settings
        self.report_list = report_list
        self.session = session
        self.xpath = xpath
        self.districts_json = districts_json
        self.report_pipeline = reportPipeline(settings['parameters'])
        self.counter = dict()
        atexit.register(self.save_list)

    def save_list(self):
        if not len(self.report_list) == 0:
            with open('.job', 'w') as f:
                f.write('\n'.join([ "{0},{1}".format(i[0], i[1]) for i in self.report_list ]))

    def get_district_name(self, district_code):
        index = self.districts_json['index'][district_code]
        ret = [u'未定义', u'未定义', u'未定义']
        province = self.districts_json['districts'][index[0]]
        city = province['sub_districts'][index[1]] if index[1] != -1 else None
        county = city['sub_districts'][index[2]] if index[2] != -1 else None
        ret[0] = province['province_name']
        ret[1] = city['city_name'] if city is not None else u'未定义'
        ret[2] = county['county_name'] if county is not None else u'未定义'
        return ret

    @retry(retry=retry_if_exception_type(asyncio.TimeoutError))
    async def crawl(self, district_code, report_id):
        while self.session._connector._limit - len(self.session._connector._waiters) - len(self.session._connector._acquired) <= 0:
            await asyncio.sleep(1)
        # record counter
        if report_id in self.counter:
            self.counter[report_id] += 1 
        else:
            self.counter[report_id] = 0
        if self.counter[report_id] == self.settings['max_attempts']:
            print("attempt {} reachs max_attempts, failed".format(report_id))
            del self.counter[report_id]
            return 

        url = self.settings['report_url'].format(district_code, report_id)
        arguments = list()

        # get district
        district_name = self.get_district_name(district_code)

        with aiohttp.Timeout(self.settings['timeout']):
            async with self.session.get(url) as response:
                html = ET.HTML(await response.text())
                for parameter in self.settings['parameters']:
                    if parameter == u'省':
                        arguments.append(district_name[0])
                    elif parameter == u'市':
                        arguments.append(district_name[1])
                    elif parameter == u'县':
                        arguments.append(district_name[2])
                    else:
                        argument = html.xpath("{}/text()".format(self.xpath[parameter]))
                        if argument:
                            arguments.append(argument[0])
                        else:
                            arguments.append('')
                self.report_pipeline.save(arguments)
        del self.counter[report_id]
        self.report_list.remove((district_code, report_id))

    async def start(self):
        tasks = [ self.crawl(report[0], report[1]) for report in self.report_list ]
        try:
            [ await f for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)) ]
        except Exception as e:
            logger.error('A fatal error occured when crawling report! Reason: {}'.format(e))
            print('A fatal error occured when crawling report! Reason: {}'.format(e))
            exit()
