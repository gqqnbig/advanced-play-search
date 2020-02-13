import os
import sqlite3
import sys

from typing import Optional

import DBUtils


def doesTableExist(TABLE_NAME, cur):
	cur.execute("SELECT 1 FROM sqlite_master WHERE name =? and type='table'", (TABLE_NAME,))
	return cur.fetchone() is not None


def delimiteDBIdentifier(identifier: str) -> str:
	return '[' + identifier + ']'


class AppSaver:

	def __init__(self, freshDays=0):
		self.conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/db.sqlite3'))
		self.cursor = self.conn.cursor()

		self.freshDays = freshDays

		if doesTableExist('App', self.cursor):
			self.allPermissions = DBUtils.getAllPermissions(self.cursor)
			self.allCategories = DBUtils.getAllCategories(self.cursor)
		else:
			self.cursor.execute('''
		create table App(
		id text NOT NULL PRIMARY KEY, 
		name text NOT NULL, 
		rating real, 
		inAppPurchases integer NOT NULL, 
		containsAds integer NOT NULL,
		num_reviews integer,
		install_fee integer NOT NULL,
		updateDate text NOT NULL -- utc time
		)''')
			self.allPermissions = []
			self.allCategories = []
			self.conn.commit()

	def __del__(self):
		self.conn.close()

	def insertOrUpdateApp(self, item, freshDays: Optional[int] = None, allPermissions=None, allCategories=None, clearPermissionsSql=None, clearCategoriesSql=None):
		"""
		Insert or update an app.

		If an app exists, and its modified date is within freshDays to now, the method doesn't update it.

		"""

		assert allPermissions is not None or clearPermissionsSql is not None
		assert allCategories is not None or clearCategoriesSql is not None
		if clearCategoriesSql is None:
			clearCategoriesSql = ''.join([',' + delimiteDBIdentifier('category_' + p) + '=0' for p in allCategories])
		if clearPermissionsSql is None:
			clearPermissionsSql = ''.join([',' + delimiteDBIdentifier('permission_' + p) + '=0' for p in allPermissions])

		if freshDays is None:
			freshDays = self.freshDays

		sql = f'''
INSERT INTO App(id,name,rating,inAppPurchases,containsAds,num_reviews,install_fee,updateDate) VALUES (?,?,?,?,?,?,?,date('now'))
on conflict(id) do update set 
name=excluded.name,
rating=excluded.rating,
inAppPurchases=excluded.inAppPurchases,
containsAds=excluded.containsAds,
num_reviews=excluded.num_reviews,
install_fee=excluded.install_fee,
updateDate=date('now')
{clearPermissionsSql}
{clearCategoriesSql}
where julianday('now')-julianday(updateDate)>=?'''
		self.cursor.execute(sql, (
			item['id'],
			item['appName'],
			item['rating'],
			item['inAppPurchases'],
			item['containsAds'],
			item['num_reviews'],
			item['install_fee'],
			self.freshDays if freshDays is None else freshDays
		))

		for p in item['permissions']:
			self.setPermission(item['id'], p)

		for c in item['categories']:
			self.setCategory(item['id'], c)

		self.conn.commit()

	def setPermission(self, appId, permission):
		permission = "permission_" + permission
		try:
			self.cursor.execute(f'update App set {delimiteDBIdentifier(permission)}=1 where id=?', (appId,))
		except:
			try:
				self.cursor.execute(f'alter table App add {delimiteDBIdentifier(permission)} integer')
				print(f'Add permission column {delimiteDBIdentifier(permission)}')
				self.cursor.execute(f'update App set {delimiteDBIdentifier(permission)}=1 where id=?', (appId,))
			except Exception as ex:
				print(ex, file=sys.stderr)

	def setCategory(self, appId, c):
		c = "category_" + c
		try:
			self.cursor.execute(f'update App set {delimiteDBIdentifier(c)}=1 where id=?', (appId,))
		except:
			try:
				self.cursor.execute(f'alter table App add {delimiteDBIdentifier(c)} integer')
				print(f'Add category column {delimiteDBIdentifier(c)}')
				self.cursor.execute(f'update App set {delimiteDBIdentifier(c)}=1 where id=?', (appId,))
			except Exception as ex:
				print(ex, file=sys.stderr)


class DatabasePipeline(AppSaver):

	def __init__(self, connectionString):
		super().__init__(0)

	@classmethod
	def from_crawler(cls, crawler):
		# cls is the class itself, ie. DatabasePipeline
		return cls(connectionString=crawler.settings.get('connectionString'))

	def process_item(self, item, spider):
		self.insertOrUpdateApp(item, self.freshDays,
							   clearPermissionsSql=''.join([',' + delimiteDBIdentifier('permission_' + p) + '=0' for p in self.allPermissions]),
							   clearCategoriesSql=''.join([',' + delimiteDBIdentifier('category_' + p) + '=0' for p in self.allCategories]))
		return item

	def open_spider(self, spider):
		l = ','.join(['\'' + id + '\'' for id in spider.targetAppIds])
		freshAppIds = [r[0] for r in self.cursor.execute(f"select id from app where julianday('now')-julianday(updateDate)<{self.freshDays} and id in ({l})")]
		if len(freshAppIds) > 0:
			print(f"Request to scrape these apps:\n{spider.targetAppIds}\n")
			spider.targetAppIds = sorted(set(spider.targetAppIds) - set(freshAppIds))
			print(f"But some are fresh, so only scrape {spider.targetAppIds}")
		else:
			print(f'scrape these apps:\n{spider.targetAppIds}')

	def close_spider(self, spider):
		pass
