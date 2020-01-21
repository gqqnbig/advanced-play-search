#!/usr/bin/env python3

import re
import scrapy
import sys
import urllib.parse as urlParse

from scrapy.crawler import CrawlerProcess
from json import loads as jsonLoads

from pipeline import AppItem


class AppInfoSpider(scrapy.Spider):
	name = "brickset_spider"
	start_urls = ['https://play.google.com/store/apps/details?hl=en&id=com.mojang.minecraftpe',
				  'https://play.google.com/store/apps/details?hl=en&id=com.sega.sonic1px',
				  'https://play.google.com/store/apps/details?id=com.tencent.mm']

	def parse(self, response):
		appInfo = AppItem()
		appInfo['id'] = urlParse.parse_qs(urlParse.urlparse(response.url).query)['id'][0]

		h1 = response.css("h1[itemprop=name]")
		appInfo['appName'] = h1.css("*::text").get()

		parentBox = h1.xpath('../..')
		appInfo['inAppPurchases'] = parentBox.xpath("div[text()[contains(.,'Offers in-app purchases')]]").get() is not None
		appInfo['containsAds'] = parentBox.xpath("div[text()[contains(.,'Contains Ads')]]").get() is not None
		try:
			# the first match is the rating box.
			ariaLabel = response.css('c-wiz div[aria-label][role=img]::attr(aria-label)').get()
			appInfo['rating'] = float(re.search(r'\d\.\d', ariaLabel)[0])
		except:
			appInfo['rating'] = None

		try:
			ariaLabel_review = parentBox.css('span[aria-label]::attr(aria-label)').get()
			appInfo['num_reviews'] = int(ariaLabel_review.split(' ')[0].replace(',', ''))
		except:
			appInfo['num_reviews'] = None

		ariaLabel_fee = parentBox.xpath('following-sibling::*').css('span button[aria-label]::attr(aria-label)').get()
		if(ariaLabel_fee == "Install"):
			appInfo['install_fee'] = 0
		else:
			appInfo['install_fee'] = float(re.search(r'\d+\.\d*', ariaLabel_fee)[0])


		r = scrapy.FormRequest(r'https://play.google.com/_/PlayStoreUi/data/batchexecute?rpcids=xdSrCf&hl=en',
							   headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
							   formdata={'f.req': r'[[["xdSrCf","[[null,[\"' + appInfo['id'] + r'\",7],[]]]",null,"1"]]]'},
							   # not use cb_kwargs because it's only passed to callback, no errback.
							   meta={'appInfo': appInfo},
							   callback=self.permissions_retrieved,
							   errback=self.errback)
		yield r

	def errback(self, failure):
		appInfo = failure.request.meta['appInfo']
		print(f'appName={appInfo.appName},  rating={appInfo.rating}, inAppPurchases={appInfo.inAppPurchases}, '
		      f'containsAds={appInfo.containsAds}, number of reviews={appInfo["num_reviews"]}, permissions=Not available')

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

		print(f'appName={appInfo["appName"]},  rating={appInfo["rating"]}, inAppPurchases={appInfo["inAppPurchases"]}, containsAds={appInfo["containsAds"]}, '
		      f'number of reviews={appInfo["num_reviews"]},  install_fee={appInfo["install_fee"]}')
		print(f'permissions={permissions}')
		appInfo['permissions']=permissions
		yield appInfo




process = CrawlerProcess(settings={
	# don't have to output log to the console.
	# https://docs.scrapy.org/en/latest/topics/settings.html#log-enabled
	# 'LOG_ENABLED': False
	'ITEM_PIPELINES' :{
	   'pipeline.DatabasePipeline': 300,
	   # 'myproject.pipelines.JsonWriterPipeline': 800 #another pipline
	}
})

process.crawl(AppInfoSpider)
process.start()  # the script will block here until the crawling is finished
