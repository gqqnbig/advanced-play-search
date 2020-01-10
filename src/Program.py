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
			rating = float(re.search('\d\.\d', ariaLabel)[0])
		except:
			rating = None

		print('appName={0},  rating={1}, inAppPurchases={2}, containsAds={3}'.format(appName, rating, inAppPurchases, containsAds))


process = CrawlerProcess(settings={
	# don't have to output log to the console.
	# https://docs.scrapy.org/en/latest/topics/settings.html#log-enabled
	# 'LOG_ENABLED': False
})

process.crawl(AppInfoSpider)
process.start()  # the script will block here until the crawling is finished
