import sqlite3
import sys


def doesTableExist(TABLE_NAME, cur):
	cur.execute("SELECT 1 FROM sqlite_master WHERE name =? and type='table'", (TABLE_NAME,))
	return cur.fetchone() is not None

def delimiteDBIdentifier(identifier: str) -> str:
	return '[' + identifier + ']'

class DatabasePipeline(object):

	def __init__(self, connectionString):
		pass

	@classmethod
	def from_crawler(cls, crawler):
		# cls is the class itself, ie. DatabasePipeline
		return cls(connectionString=crawler.settings.get('connectionString'))

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

	def process_item(self, item, spider):
		self.cursor.execute('select 1 from App where id=?', (item['id'],))
		if self.cursor.fetchone() is not None:
			return item

		sql = "INSERT INTO App(id,name,rating,inAppPurchases,containsAds,num_reviews, install_fee) VALUES (?,?,?,?,?,?,?)"
		self.cursor.execute(sql, (
			item['id'],
			item['appName'],
			item['rating'],
			item['inAppPurchases'],
			item['containsAds'],
			item['num_reviews'],
			item['install_fee']
		))

		for p in item['permissions']:
			self.setPermission(item['id'], p)

		for c in item['categories']:
			self.setCategory(item['id'], c)

		self.conn.commit()
		return item

	def open_spider(self, spider):
		self.conn = sqlite3.connect('../data/db.sqlite3')
		self.cursor = self.conn.cursor()
		if doesTableExist('App', self.cursor) is False:
			self.cursor.execute('''
create table App(
id text NOT NULL PRIMARY KEY, 
name text NOT NULL, 
rating real, 
inAppPurchases integer NOT NULL, 
containsAds integer NOT NULL,
num_reviews integer,
install_fee integer NOT NULL
)''')
			self.conn.commit()

	def close_spider(self, spider):
		self.conn.close()
