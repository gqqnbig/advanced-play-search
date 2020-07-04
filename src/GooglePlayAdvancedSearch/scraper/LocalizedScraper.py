#!/usr/bin/env python3

import io
import logging
import os
import re
import time
import argparse

import OpenSSL
import scrapy
import sys
import urllib.parse as urlParse

from scrapy.crawler import CrawlerProcess
from json import loads as jsonLoads

from scrapy.exceptions import CloseSpider

sys.path.append("../..")
import GooglePlayAdvancedSearch.Errors
from GooglePlayAdvancedSearch.Models import AppItem
from GooglePlayAdvancedSearch import DBUtils


class LocalizedAppInfoSpider(scrapy.Spider):
	name = "LocalizedAppInfoSpider"

	def __init__(self):
		parser = argparse.ArgumentParser()
		parser.add_argument('ids', type=str, nargs='+', help='App ids to be scraped')
		parser.add_argument('--language', type=str, help='Scrape app info in this language')
		parser.add_argument('--selenium', action='store_false', help='whether to use selenium to retrieve web page')

		args = parser.parse_args()
		self.targetAppIds = args.ids
		# if len(self.targetAppIds)==0:
		# 	self.targetAppIds = ['com.mojang.minecraftpe', 'com.sega.sonic1px', 'com.tencent.mm',
		# 						 'com.freecamchat.liverandomchat', 'com.matchdating.meetsingles']
		self.__language = args.language
		if re.fullmatch(r'\w{2}(-\w{2,})', self.__language) is None:
			raise Exception(f'{self.__language} is not valid value for --language. The country part must be lower case, the locale part is optional and must be UPPER case. Eg. zh, zh-TW,')

		self.__seleniumAvailable = args.selenium
		self.__appAccessor = DBUtils.AppAccessor()

	def start_requests(self):
		url = 'https://play.google.com/store/apps/details?hl=' + self.__language + '&id='
		for _url in [url + id for id in self.targetAppIds]:
			yield scrapy.Request(url=_url, callback=self.parse)

	def parse(self, response):
		id = urlParse.parse_qs(urlParse.urlparse(response.url).query)['id'][0]

		h1 = response.css("h1[itemprop=name]")
		name = h1.css("*::text").get()

		self.__appAccessor.setLocalizedName(id, self.__language, name)

	def closed(self, reason):
		del self.__appAccessor



if '--pytest' in sys.argv and sys.platform == 'win32' and sys.stdout.encoding == 'cp936':
	# com.sega.sonic1px has unicode characters. Without this fix, if run in pytest, the print statement throws exception.
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

process = CrawlerProcess(settings={
	# don't have to output log to the console.
	# https://docs.scrapy.org/en/latest/topics/settings.html#log-enabled
	# 'LOG_ENABLED': False
	'LOG_LEVEL': 'WARNING',
	'ITEM_PIPELINES': {
		# 'pipeline.DatabasePipeline': 300,
		# 'myproject.pipelines.JsonWriterPipeline': 800 #another pipline
	},
	'DOWNLOADER_CLIENTCONTEXTFACTORY': 'scrapy.core.downloader.contextfactory.BrowserLikeContextFactory',
})

exitCode = 0

process.crawl(LocalizedAppInfoSpider)
process.start()  # the script will block here until the crawling is finished

sys.exit(exitCode)
