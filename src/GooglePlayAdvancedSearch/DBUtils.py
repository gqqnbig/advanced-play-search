import os
import sqlite3
import sys

from typing import Optional


def getAppCountInDatabase(cursor):
	try:
		cursor.execute('select count(*) from app')
		return cursor.fetchone()[0]
	except:  # no such table: app
		return 0


def getAllPermissions(cursor):
	cursor.execute('Pragma table_info(App)')
	columns = cursor.fetchall()
	permissions = [c[1][11:] for c in columns if c[1].startswith("permission_")]
	return permissions


def getAllCategories(cursor):
	cursor.execute('Pragma table_info(App)')
	columns = cursor.fetchall()
	categories = [c[1][9:] for c in columns if c[1].startswith("category_")]
	return categories


def doesTableExist(TABLE_NAME, cur):
	cur.execute("SELECT 1 FROM sqlite_master WHERE name =? and type='table'", (TABLE_NAME,))
	return cur.fetchone() is not None


def delimiteDBIdentifier(identifier: str) -> str:
	return '[' + saveSqlValue(identifier) + ']'


def saveSqlValue(str: str):
	return str.replace('"', '').replace("'", '').replace('--', '')


class AppSaver:

	def __init__(self, freshDays=0):
		self.__conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data/db.sqlite3'))
		self.__cursor = self.__conn.cursor()

		self.__freshDays = freshDays

		if doesTableExist('App', self.__cursor):
			self.__allPermissions = getAllPermissions(self.__cursor)
			self.__allCategories = getAllCategories(self.__cursor)
		else:
			self.__cursor.execute('''
create table App(
id text NOT NULL PRIMARY KEY, 
name text NOT NULL, 
rating real, 
inAppPurchases integer, 
containsAds integer,
num_reviews integer,
install_fee integer NOT NULL,
updateDate text NOT NULL, -- utc time
app_icon text NOT NULL,
isPartialInfo integer not null
)''')
			self.__allPermissions = []
			self.__allCategories = []
			self.__conn.commit()

		self.__clearCategoriesSql = ''.join([',' + delimiteDBIdentifier('category_' + p) + '=0' for p in self.__allCategories])
		self.__clearPermissionsSql = ''.join([',' + delimiteDBIdentifier('permission_' + p) + '=0' for p in self.__allPermissions])

	def __del__(self):
		self.__conn.close()

	def insertOrUpdateApp(self, item, freshDays: Optional[int] = None) -> bool:
		"""
		Insert or update an app.

		If an app exists, and its modified date is within freshDays to now, the method doesn't update it.

		:param freshDays: a record is considered fresh within how many days. If it's None, the value from constructor is used.
		:return true if the database is updated. false if the database record is fresh, no need to update.
		"""

		if freshDays is None:
			freshDays = self.__freshDays

		valuesToInsert = []
		parameters = []

		isPartialInfo = False
		if 'inAppPurchases' in item:
			valuesToInsert.append('inAppPurchases')
			parameters.append(item['inAppPurchases'])
		else:
			isPartialInfo = True

		if 'containsAds' in item:
			valuesToInsert.append('containsAds')
			parameters.append(item['containsAds'])
		else:
			isPartialInfo = True

		if 'num_reviews' in item:
			valuesToInsert.append('num_reviews')
			parameters.append(item['num_reviews'])
		else:
			isPartialInfo = True

		sql = f'''
INSERT INTO App(id,name,rating,install_fee,app_icon,isPartialInfo,updateDate{''.join([',' + x for x in valuesToInsert])}) VALUES (?,?,?,?,?,?,date('now'){''.join([',?'] * len(valuesToInsert))})
on conflict(id) do update set 
name=excluded.name,
rating=excluded.rating,
install_fee=excluded.install_fee,
app_icon=excluded.app_icon,
isPartialInfo=excluded.isPartialInfo,
updateDate=excluded.updateDate
{''.join([',' + x + '=excluded.' + x for x in valuesToInsert])}
{self.__clearPermissionsSql}
{self.__clearCategoriesSql}
where julianday('now')-julianday(updateDate)>=?'''
		self.__cursor.execute(sql, (
			item['id'],
			item['appName'],
			item['rating'],
			item['install_fee'],
			item['app_icon'],
			isPartialInfo)
							  + tuple(parameters)
							  + (
								  self.__freshDays if freshDays is None else freshDays,
							  ))
		if self.__cursor.rowcount == 0:
			return False

		for p in item.get('permissions', []):
			self.__setPermission(item['id'], p)

		for c in item.get('categories', []):
			self.__setCategory(item['id'], c)

		self.__conn.commit()
		return True

	def __setPermission(self, appId, permission):
		permission = "permission_" + permission
		try:
			self.__cursor.execute(f'update App set {delimiteDBIdentifier(permission)}=1 where id=?', (appId,))
			self.__allPermissions.append(permission)
		except:
			try:
				self.__cursor.execute(f'alter table App add {delimiteDBIdentifier(permission)} integer')
				print(f'Add permission column {delimiteDBIdentifier(permission)}')
				self.__cursor.execute(f'update App set {delimiteDBIdentifier(permission)}=1 where id=?', (appId,))
				self.__allPermissions.append(permission)
			except Exception as ex:
				print(ex, file=sys.stderr)

	def __setCategory(self, appId, c):
		c = "category_" + c
		try:
			self.__cursor.execute(f'update App set {delimiteDBIdentifier(c)}=1 where id=?', (appId,))
			self.__allCategories.append(c)
		except:
			try:
				self.__cursor.execute(f'alter table App add {delimiteDBIdentifier(c)} integer')
				print(f'Add category column {delimiteDBIdentifier(c)}')
				self.__cursor.execute(f'update App set {delimiteDBIdentifier(c)}=1 where id=?', (appId,))
				self.__allCategories.append(c)
			except Exception as ex:
				print(ex, file=sys.stderr)
