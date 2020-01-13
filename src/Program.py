#!/usr/bin/env python3

import re
import scrapy
import sys
import urllib.parse as urlParse

from scrapy.crawler import CrawlerProcess
from types import SimpleNamespace
from json import loads as jsonLoads


class AppInfoSpider(scrapy.Spider):
	name = "brickset_spider"
	start_urls = ['https://play.google.com/store/apps/details?hl=en&id=com.mojang.minecraftpe',
				  'https://play.google.com/store/apps/details?hl=en&id=com.sega.sonic1px',
				  'https://play.google.com/store/apps/details?id=com.tencent.mm']

	def parse(self, response):
		appId = urlParse.parse_qs(urlParse.urlparse(response.url).query)['id'][0]

		appInfo = SimpleNamespace()

		h1 = response.css("h1[itemprop=name]")
		appInfo.appName = h1.css("*::text").get()

		parentBox = h1.xpath('../..')
		appInfo.inAppPurchases = parentBox.xpath("div[text()[contains(.,'Offers in-app purchases')]]").get() is not None
		appInfo.containsAds = parentBox.xpath("div[text()[contains(.,'Contains Ads')]]").get() is not None
		try:
			# the first match is the rating box.
			ariaLabel = response.css('c-wiz div[aria-label][role=img]::attr(aria-label)').get()
			appInfo.rating = float(re.search(r'\d\.\d', ariaLabel)[0])
		except:
			appInfo.rating = None

		r = scrapy.FormRequest(r'https://play.google.com/_/PlayStoreUi/data/batchexecute?rpcids=xdSrCf&hl=en',
							   headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
							   formdata={'f.req': r'[[["xdSrCf","[[null,[\"' + appId + r'\",7],[]]]",null,"1"]]]'},
							   # not use cb_kwargs because it's only passed to callback, no errback.
							   meta={'appInfo': appInfo},
							   callback=self.permissions_retrieved,
							   errback=self.errback)
		yield r

	def errback(self, failure):
		appInfo = failure.request.meta['appInfo']
		print(f'appName={appInfo.appName},  rating={appInfo.rating}, inAppPurchases={appInfo.inAppPurchases}, containsAds={appInfo.containsAds}, permissions=Not available')

	# print(failure)

	def permissions_retrieved(self, response):
		appInfo = response.meta['appInfo']
		data = jsonLoads(response.text[response.text.index('\n') + 1:])
		permissionData = jsonLoads(data[0][2])

		permissions = []

		# permissionData[0] is grouped permissions.
		if len(permissionData) > 0:
			for g in permissionData[0]:
				for p in g[2]:
					permissions.append(p[1])

		# permissionData[1] is other permissions.
		if len(permissionData) > 1:
			for p in permissionData[1][0][2]:
				permissions.append(p[1])

		# permissionData[2] is miscellaneous permissions.
		if len(permissionData) > 2:
			for p in permissionData[2]:
				permissions.append(p[1])

		if len(permissionData) > 3:
			print('Unknown data in permission block.\npermissionData={}'.format(permissionData), file=sys.stderr)

		print(f'appName={appInfo.appName},  rating={appInfo.rating}, inAppPurchases={appInfo.inAppPurchases}, containsAds={appInfo.containsAds}')
		print(f'permissions={permissions}')


process = CrawlerProcess(settings={
	# don't have to output log to the console.
	# https://docs.scrapy.org/en/latest/topics/settings.html#log-enabled
	# 'LOG_ENABLED': False
})

process.crawl(AppInfoSpider)
process.start()  # the script will block here until the crawling is finished
