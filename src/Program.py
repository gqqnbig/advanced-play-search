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

		r = scrapy.Request(r'https://play.google.com/_/PlayStoreUi/data/batchexecute?rpcids=xdSrCf&f.sid=324256068901206895&bl=boq_playuiserver_20200108.06_p0&hl=en&authuser&soc-app=121&soc-platform=1&soc-device=1&_reqid=244757&rt=c',
						   method='POST',
							headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
										"Origin": "https://play.google.com",
										"Referer": "https://play.google.com/",
										"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
										"X-Same-Domain": "1"
										},
							body='f.req=%5B%5B%5B%22xdSrCf%22%2C%22%5B%5Bnull%2C%5B%5C%22com.sega.sonic1px%5C%22%2C7%5D%2C%5B%5D%5D%5D%22%2Cnull%2C%221%22%5D%5D%5D&',
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
