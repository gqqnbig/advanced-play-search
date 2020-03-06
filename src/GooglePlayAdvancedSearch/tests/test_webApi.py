import os
import sqlite3

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
			app['appName'] = 'matched keyword'
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


def test_searchPermissionFilter():
	testUtils.startWebsite(callback_searchPermissionFilter)


def test_searchCategoryFilter():
	testUtils.startWebsite(callback_searchCategoryFilter)


def test_searchResultUpperBound():
	testUtils.startWebsite(callback_searchResultUpperBound)


if __name__ == "__main__":
	test_searchPermissionFilter()
	test_searchCategoryFilter()
