import os
import sqlite3
import urllib

import pytest
import requests

import GooglePlayAdvancedSearch.DBUtils
import GooglePlayAdvancedSearch.tests.testUtils as testUtils
from GooglePlayAdvancedSearch.Models import AppItem


def callback_searchPermissionFilter(websiteUrl):
	# com.tencent.mm uses permission 'read the contents of your USB storage'
	# We exclude this permission in the search, and make sure the result doesn't have com.tencent.mm.

	testUtils.runScraper(['--pytest', '-p', 'com.tencent.mm'])

	dbFilePath = os.path.join(testUtils.getTestFolder(), '../../data/db.sqlite3')
	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()
	permissions = GooglePlayAdvancedSearch.DBUtils.getAllPermissions(cursor)
	pid = next((k for k, v in permissions.items() if 'read the contents of your USB storage' in v), None)

	response = requests.get(websiteUrl + '/Api/Search?q=wechat&pids=' + str(pid), verify=True)
	text = response.text
	assert 'com.tencent.mm' not in text, "Search for wechat without storage permission. The search result should not have wechat."

	response = requests.get(websiteUrl + '/Api/Search?q=wechat', verify=True)
	text = response.text
	assert 'com.tencent.mm' in text, "Search for wechat allowing storage permission. The search result not have wechat."


def callback_searchCategoryFilter(websiteUrl):
	# com.facebook.katana uses category 'Social'
	# we exclude this category in the search, and make sure the result doesn't have com.facebook.katana.

	testUtils.runScraper(['--pytest', '-p', 'com.facebook.katana'])

	dbFilePath = os.path.join(testUtils.getTestFolder(), '../../data/db.sqlite3')
	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()
	categories = GooglePlayAdvancedSearch.DBUtils.getAllCategories(cursor)
	cid = next((k for k, v in categories.items() if 'Social' in v), None)

	response = requests.get(websiteUrl + '/Api/Search?q=facebook&cids=' + str(cid), verify=True)
	text = response.text
	assert 'com.facebook.katana' not in text, "Search for facebook without Social category. The search result should not have it."

	response = requests.get(websiteUrl + '/Api/Search?q=facebook', verify=True)
	text = response.text
	assert 'com.facebook.katana' in text, "Search for facebook allowing Social category. The search result should have it."


def callback_searchResultUpperBound(websiteUrl):
	dbFilePath = os.path.join(testUtils.getTestFolder(), '../../data/db.sqlite3')
	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()
	try:
		appAccessor = GooglePlayAdvancedSearch.DBUtils.AppAccessor()
		insertedCount = GooglePlayAdvancedSearch.DBUtils.MAX_SELECT + 1
		for i in range(insertedCount):
			app = AppItem()
			app['id'] = 'GooglePlayAdvancedSearch.testApp' + str(i)
			app['name'] = 'matched keyword'
			app['rating'] = 0
			app['install_fee'] = 0
			app['app_icon'] = ''

			appAccessor.insertOrUpdateApp(app)
		del appAccessor

		cursor.execute("select count(*) from App where id like 'GooglePlayAdvancedSearch.testApp%'")
		assert int(cursor.fetchone()[0]) >= insertedCount, f"failed to insert {insertedCount} rows."

		response = requests.get(websiteUrl + '/Api/Search?q=matched%20keyword', verify=True)
		data = response.json()
		assert len(data['apps']) <= GooglePlayAdvancedSearch.DBUtils.MAX_SELECT, f"At most returns {GooglePlayAdvancedSearch.DBUtils.MAX_SELECT}, actually returns {len(data['apps'])}."
	finally:
		cursor.execute('delete from App where id like :id', {'id': 'GooglePlayAdvancedSearch.testApp%'})


def callback_notReadingStaleInfo(websiteUrl):
	dbFilePath = os.path.join(testUtils.getTestFolder(), '../../data/db.sqlite3')

	lastException = None
	tryCount = 0
	while tryCount < 2:
		tryCount += 1
		try:
			connection = sqlite3.connect(dbFilePath)
			cursor = connection.cursor()
			cursor.execute('select id, name from App where rating>1 limit 1')
			app = cursor.fetchone()
			if app is None:
				raise FileExistsError('cannot find an app with rating 1 for testing purpose.')

			cursor.execute("update App set updateDate=2000-01-01, rating=1 where id=:id", {'id': app[0]})
			connection.commit()
			response = requests.get(websiteUrl + '/Api/Search?q=' + urllib.parse.quote(app[1]))
			data = response.json()

			newApp = next(a for a in data['apps'] if a['id'] == app[0])
			assert newApp['rating'] > 1, f"The rating of {app[1]} should be > 1 because the old rating was added on 2000-01-01."
			return
		except FileExistsError as e:
			lastException = e
		except sqlite3.OperationalError as e:
			# maybe the database is empty. We need to load something
			lastException = e

		requests.get(websiteUrl + '/Api/Search?q=facebook')
	pytest.skip(str(lastException))


def test_searchPermissionFilter():
	testUtils.startWebsite(callback_searchPermissionFilter)


def test_searchCategoryFilter():
	testUtils.startWebsite(callback_searchCategoryFilter)


def test_searchResultUpperBound():
	testUtils.startWebsite(callback_searchResultUpperBound)


def test_notReadingStaleInfo():
	testUtils.startWebsite(callback_notReadingStaleInfo)


if __name__ == "__main__":
	test_notReadingStaleInfo()
