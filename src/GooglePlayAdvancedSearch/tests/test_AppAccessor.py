import os
import sqlite3

import pytest

import GooglePlayAdvancedSearch.tests.testUtils as testUtils

from GooglePlayAdvancedSearch.DBUtils import AppAccessor
from GooglePlayAdvancedSearch.Models import AppItem


def test_getCompleteAppInfoPartial():
	app = AppItem()
	app['name'] = 'test app'
	app['id'] = 'testid'
	app['rating'] = 1
	app['install_fee'] = 0
	app['app_icon'] = ''

	appAccessor = AppAccessor(10)
	appAccessor.insertOrUpdateApp(app, 0)

	assert appAccessor.getCompleteAppInfo('testid') is None, "Database only has partial info."


def test_getCompleteAppInfoStale(dbFilePath):
	if os.path.exists(dbFilePath):
		try:
			os.remove(dbFilePath)
		except PermissionError as e:
			pytest.skip(str(e))

	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()
	try:
		app = AppItem()
		app['name'] = 'test app'
		app['id'] = 'testid'
		app['rating'] = 1
		app['install_fee'] = 0
		app['app_icon'] = ''
		app['inAppPurchases'] = True
		app['containsAds'] = False
		app['num_reviews'] = 1000
		app['install_fee'] = 0
		app['permissions'] = []
		app['categories'] = []

		appAccessor = AppAccessor(10)
		appAccessor.insertOrUpdateApp(app, 0)

		assert appAccessor.getCompleteAppInfo('testid')['rating'] == 1

		cursor.execute("update app set updateDate='2000-01-01' where id='testid'")
		connection.commit()
		assert appAccessor.getCompleteAppInfo('testid') is None, "App data are stale, getCompleteAppInfo should return null."
	finally:
		cursor.execute("delete from app where id='testid'")


def test_searchAppsStale(dbFilePath):
	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()

	try:
		app = AppItem()
		app['name'] = 'test app'
		app['id'] = 'testid'
		app['rating'] = 1
		app['install_fee'] = 0
		app['app_icon'] = ''

		appAccessor = AppAccessor(10)
		appAccessor.insertOrUpdateApp(app, 0)

		cursor.execute("update app set updateDate='2000-01-01' where id='testid'")
		connection.commit()
		assert next((a for a in appAccessor.searchApps('test app') if a['id'] == 'testid'), None) is None, "test app was updated on 2000-01-01, it should appear in search result."
	finally:
		cursor.execute("delete from app where id='testid'")
