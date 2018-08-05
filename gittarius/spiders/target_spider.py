from scrapy import Request, Spider
from urllib.parse import urlencode
import json


class TargetSpider(Spider):
    """this is a spider aiming target's web page"""
    name = 'TargetSpider'
    targetURL = 'https://redsky.target.com/v1/plp/search/?'

    def __init__(self):
        self._header = {
            'user-agent': 'Mozilla/5.0 '
            '(Windows NT 10.0; Win64; x64) AppleWebKit/'
            '537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        }
        self._parameters = {
            'count': 24,
            'offset': 0,
            'category': '5xtg6',
            'faceted_value': '5zktyZ5zl7w',
            'default_purchasability_filter': 'true',
            'puis': 'true',
            'visitorId': '0164E6A4D998020186B558915E6A521E',
            'pageId': '/c/5xtg6',
            'channel': 'web',
            'store_ids': '2088',
        }

    def getParameters(self):
        self._parameters['offset'] += self._parameters['count']
        return self._parameters

    def start_requests(self):
        return [
            Request(
                TargetSpider.targetURL +
                urlencode(self._parameters))]

    def parse(self, response):
        responseDict = json.loads(response.text)
        try:
            for item in responseDict['search_response']['items']['Item']:
                yield item
        except Exception as e:
            pass

        try:
            totalPages = 0
            currentPage = 0
            for meta in responseDict['search_response']['metaData']:
                if meta['name'] == 'totalPages':
                    totalPages = int(meta['value'])
                if meta['name'] == 'currentPage':
                    currentPage = int(meta['value'])
            if currentPage < totalPages:
                yield {'log***': [currentPage, totalPages]}
                yield Request(TargetSpider.targetURL +
                              urlencode(self.getParameters()))
        except Exception as e:
            pass
