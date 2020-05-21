import GooglePlayAdvancedSearch.DBUtils


class DatabasePipeline(GooglePlayAdvancedSearch.DBUtils.AppAccessor):

	def __init__(self, connectionString):
		super().__init__()

	@classmethod
	def from_crawler(cls, crawler):
		# cls is the class itself, ie. DatabasePipeline
		return cls(connectionString=crawler.settings.get('connectionString'))

	def process_item(self, item, spider):
		self.insertOrUpdateApp(item)
		return item

	def open_spider(self, spider):
		l = ','.join(['\'' + id + '\'' for id in spider.targetAppIds])
		existingAppIds = [r[0] for r in self._AppAccessor__cursor.execute(f"select id from app where isPartialInfo=0 and id in ({l})")]
		# app information may not be up to date. It is staleAppRemover's job to remove old apps.
		if len(existingAppIds) > 0:
			print(f"Request to scrape these apps:\n{spider.targetAppIds}")
			spider.targetAppIds = sorted(set(spider.targetAppIds) - set(existingAppIds))
			print(f"But some exist, so only scrape {spider.targetAppIds}")
		else:
			print(f'scrape these apps:\n{spider.targetAppIds}')

	def close_spider(self, spider):
		pass
