#coding:utf-8
import asyncio
import aiohttp
import lxml.etree as ET
import tqdm

#from pipeline import reportPipeline

class reportSpider(object):
    def __init__(self, settings, report_list, xpath, districts_json, session):
        self.settings = settings
        self.report_list = report_list
        self.session = session
        self.xpath = xpath
        self.districts_json = districts_json

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

    async def crawl(self, district_code, report_id):
        url = self.settings['report_url'].format(district_code, report_id)
        res = list()

        # get district
        district_name = self.get_district_name(district_code)

        async with self.session.get(url) as response:
            html = ET.HTML(await response.text())
            for argument in self.settings['arguments']:
                if argument == u'省':
                    res.append(district_name[0])
                elif argument == u'市':
                    res.append(district_name[1])
                elif argument == u'县':
                    res.append(district_name[2])
                else:
                    res.append(html.xpath("{}/text()".format(self.xpath[argument])))
            print(res)
        return res

    async def start(self):
        tasks = [ self.crawl(report[0], report[1]) for report in self.report_list ]
        [ await f for f in tqdm.tqdm(asyncio.as_completed(tasks), total=len(tasks)) ]


