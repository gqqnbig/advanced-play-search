#!/usr/bin/env python3

import re
import scrapy

from scrapy.crawler import CrawlerProcess


class AppInfoSpider(scrapy.Spider):
	name = "brickset_spider"
	start_urls = ['https://play.google.com/store/apps/details?hl=en&id=com.mojang.minecraftpe',
				  'https://play.google.com/store/apps/details?hl=en&id=com.sega.sonic1px']

	def parse(self, response):
		h1 = response.css("h1[itemprop=name]")
		appName = h1.css("*::text").get()

		parentBox = h1.xpath('../..')
		inAppPurchases = parentBox.xpath("div[text()[contains(.,'Offers in-app purchases')]]").get() is not None
		containsAds = parentBox.xpath("div[text()[contains(.,'Contains Ads')]]").get() is not None
		try:
			# the first match is the rating box.
			ariaLabel = response.css('c-wiz div[aria-label][role=img]::attr(aria-label)').get()
			rating = float(re.search(r'\d\.\d', ariaLabel)[0])
		except:
			rating = None

		print(f'appName={appName},  rating={rating}, inAppPurchases={inAppPurchases}, containsAds={containsAds}')

		r = scrapy.FormRequest(r'https://play.google.com/_/PlayStoreUi/data/batchexecute?rpcids=xdSrCf&f.sid=324256068901206895&hl=en',
							headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
							formdata={'f.req':r'[[["xdSrCf","[[null,[\"com.sega.sonic1px\",7],[]]]",null,"1"]]]'},
							callback=self.callback,
							errback=self.errback)
		yield r

	def errback(self, failure):
		print(failure)

	def callback(self, response):
		print(response.text)










process = CrawlerProcess(settings={
	# don't have to output log to the console.
	# https://docs.scrapy.org/en/latest/topics/settings.html#log-enabled
	# 'LOG_ENABLED': False
})

process.crawl(AppInfoSpider)
process.start()  # the script will block here until the crawling is finished
