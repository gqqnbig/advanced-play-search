import GooglePlayAdvancedSearch.DBUtils


class DatabasePipeline(GooglePlayAdvancedSearch.DBUtils.AppAccessor):

	def __init__(self, connectionString):
		super().__init__(0)

	@classmethod
	def from_crawler(cls, crawler):
		# cls is the class itself, ie. DatabasePipeline
		return cls(connectionString=crawler.settings.get('connectionString'))

	def process_item(self, item, spider):
		self.insertOrUpdateApp(item, self._AppAccessor__freshDays)
		return item

	def open_spider(self, spider):
		l = ','.join(['\'' + id + '\'' for id in spider.targetAppIds])
		freshAppIds = [r[0] for r in self._AppAccessor__cursor.execute(f"select id from app where julianday('now')-julianday(updateDate)<{self._AppAccessor__freshDays} and id in ({l})")]
		if len(freshAppIds) > 0:
			print(f"Request to scrape these apps:\n{spider.targetAppIds}\n")
			spider.targetAppIds = sorted(set(spider.targetAppIds) - set(freshAppIds))
			print(f"But some are fresh, so only scrape {spider.targetAppIds}")
		else:
			print(f'scrape these apps:\n{spider.targetAppIds}')

	def close_spider(self, spider):
		pass
