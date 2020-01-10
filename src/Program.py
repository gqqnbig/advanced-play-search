import re
import scrapy

from scrapy.crawler import CrawlerProcess


class AppInfoSpider(scrapy.Spider):
	name = "brickset_spider"
	start_urls = ['https://play.google.com/store/apps/details?hl=en&id=com.mojang.minecraftpe']

	def parse(self, response):
		h1=response.css("h1[itemprop=name]")
		appName = h1.css("*::text").get()

		inAppPurchases= h1.xpath('../..').xpath("div[contains(.//text(),'Offers in-app purchases')]").get() is not None

		try:
			# the first match is the rating box.
			ariaLabel = response.css('c-wiz div[aria-label][role=img]::attr(aria-label)').get()
			rating = float(re.search('\d\.\d', ariaLabel)[0])
		except:
			rating = None



		print('appName={0},  rating={1}, inAppPurchases={2}'.format(appName, rating, inAppPurchases))


process = CrawlerProcess(settings={
	'FEED_FORMAT': 'json',
	'FEED_URI': 'items.json',
	# don't have to output log to the console.
	# https://docs.scrapy.org/en/latest/topics/settings.html#log-enabled
	# 'LOG_ENABLED': False
})

process.crawl(AppInfoSpider)
process.start()  # the script will block here until the crawling is finished
