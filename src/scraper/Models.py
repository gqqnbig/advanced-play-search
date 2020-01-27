from scrapy import Item, Field


class AppItem(Item):
	appName = Field()
	id = Field()
	rating = Field()
	inAppPurchases = Field()
	containsAds = Field()
	permissions = Field()
	num_reviews = Field()
	install_fee = Field()
	categories = Field()