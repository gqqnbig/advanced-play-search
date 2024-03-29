import os
import pytest
import sqlite3
import time

import requests

import GooglePlayAdvancedSearch.DBUtils
import GooglePlayAdvancedSearch.tests.testUtils as testUtils
from GooglePlayAdvancedSearch.Models import AppItem


def test_searchWithPermission(websiteUrl, dbFilePath):
	# com.tencent.mm uses permission 'read the contents of your USB storage'
	# We exclude this permission in the search, and make sure the result doesn't have com.tencent.mm.

	testUtils.runScraper(['--pytest', '-p', 'com.tencent.mm'])
	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()
	permissions = GooglePlayAdvancedSearch.DBUtils.getAllPermissions(cursor)
	connection.close()
	pid = next((k for k, v in permissions.items() if 'read the contents of your USB storage' in v), None)

	response = requests.get(websiteUrl + '/Api/Search?q=wechat&pids=' + str(pid), verify=True)
	text = response.text
	assert 'com.tencent.mm' not in text, "Search for wechat without storage permission. The search result should not have wechat."

	response = requests.get(websiteUrl + '/Api/Search?q=wechat', verify=True)
	text = response.text
	assert 'com.tencent.mm' in text, "Search for wechat allowing storage permission. The search result not have wechat."


def test_searchWithCategory(websiteUrl, dbFilePath):
	# com.facebook.katana uses category 'Social'
	# we exclude this category in the search, and make sure the result doesn't have com.facebook.katana.

	testUtils.runScraper(['--pytest', '-p', 'com.facebook.katana'])
	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()
	categories = GooglePlayAdvancedSearch.DBUtils.getAllCategories(cursor)
	connection.close()
	cid = next((k for k, v in categories.items() if 'Social' in v), None)

	response = requests.get(websiteUrl + '/Api/Search?q=facebook&cids=' + str(cid), verify=True)
	text = response.text
	assert 'com.facebook.katana' not in text, "Search for facebook without Social category. The search result should not have it."

	response = requests.get(websiteUrl + '/Api/Search?q=facebook', verify=True)
	text = response.text
	assert 'com.facebook.katana' in text, "Search for facebook allowing Social category. The search result should have it."


def test_searchWithRatingInc(websiteUrl):
	resultCount = 1000
	for rating in range(-1, 5):
		response = requests.get(websiteUrl + '/Api/Search?q=Fundamentals%20Of%20Prosperity%20Free%20eBook%20%26%20Audio%20Book&rating=' + str(rating),
								cookies={'_gaload': 'ok'})
		try:
			data = response.json()
			data = data['apps']
		except Exception as e:
			pytest.fail(str(e) + f'\ndata={response.text}')

		assert len(data) <= resultCount, 'Rating goes higher, the search result should be less.'

		for app in data:
			assert app['rating'] > rating, f'App {app["name"]} does not match search condition.'


def test_searchWithRatingDec(websiteUrl):
	resultCount = -1
	for rating in range(4, -2):
		response = requests.get(websiteUrl + '/Api/Search?q=sms&rating=' + str(rating),
								cookies={'_gaload': 'ok'})
		try:
			data = response.json()['apps']
		except Exception as e:
			pytest.fail(str(e) + f'\ndata={response.text}')

		assert len(data) >= resultCount, 'Rating goes lower, the search result should be more.'

		for app in data:
			assert app['rating'] > rating, f'App {app["name"]} does not match search condition.'


def test_searchResultUpperBound(websiteUrl, dbFilePath):
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
		connection.commit()
		connection.close()


def test_recentSearches(websiteUrl, dbFilePath):
	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()

	try:
		cursor.execute("insert into Search(keyword, query, ip ,date) values('recentSearches-test1', '', 'pytest', datetime('now'))")
		for _ in range(10):
			cursor.execute("insert into Search(keyword, query, ip ,date) values('recentSearches-test2', '', 'pytest', '2010-01-01')")
		connection.commit()

		response = requests.get(websiteUrl + '/Api/RecentSearches')
		data = response.json()
		assert data[0]['keyword'] == 'recentSearches-test1', "Most recent search is recentSearches-test1, but the API does not return it."
	finally:
		cursor.execute("delete from Search where ip='pytest'")
		connection.commit()
		connection.close()


def test_sortByPriceWithoutDetail(websiteUrl):
	response = requests.get(websiteUrl + '/Api/Search?q=emoji&sort=flh')
	try:
		data = response.json()['apps']
	except Exception as e:
		pytest.fail(str(e) + f'\ndata={response.text}')

	assert data[0]['install_fee'] <= data[-1]['install_fee'], \
		f'Sort apps by price from low to high, but the price of the first app is {data[0]["install_fee"]}, the price of the last app is {data[-1]["install_fee"]}.'

	response = requests.get(websiteUrl + '/Api/Search?q=emoji&sort=fhl')
	data = response.json()['apps']
	assert data[0]['install_fee'] >= data[-1]['install_fee'], \
		f'Sort apps by price from high to low, but the price of the first app is {data[0]["install_fee"]}, the price of the last app is {data[-1]["install_fee"]}.'


def callback_testSearchTimingFromEmpty(websiteUrl):
	response = requests.get(websiteUrl + '/Api/SearchTiming')
	assert response.status_code == 200
	data = response.json()
	assert type(data['mean']) is int
	assert type(data['std']) is int

	time.sleep(20)  # for rate control
	requests.get(websiteUrl + '/Api/Search?q=game')
	response = requests.get(websiteUrl + '/Api/SearchTiming')
	assert response.status_code == 200
	data = response.json()
	assert type(data['mean']) is int
	assert type(data['std']) is int

	time.sleep(20)  # for rate control
	requests.get(websiteUrl + '/Api/Search?q=book')
	response = requests.get(websiteUrl + '/Api/SearchTiming')
	assert response.status_code == 200
	data = response.json()
	assert data['mean'] > 0
	assert data['std'] > 0  # in theory, std may be 0 for the two runs.


def test_searchTiming(dbFilePath):
	if os.path.exists(dbFilePath):
		os.remove(dbFilePath)

	testUtils.startWebsite(callback_testSearchTimingFromEmpty)


def test_sortByPrice(websiteUrl):
	response = requests.get(websiteUrl + '/Api/Search?q=database&sort=flh&ad=false')
	try:
		data = response.json()['apps']
	except Exception as e:
		pytest.fail(str(e) + f'\ndata={response.text}')

	p1 = data[0]['install_fee']
	if p1 is None:
		p1 = 0
	p2 = data[-1]['install_fee']
	if p2 is None:
		p2 = 0
	assert p1 <= p2, f'Sort apps by price from low to high, but the price of the first app is greater than the price of the last app.'

	response = requests.get(websiteUrl + '/Api/Search?q=database&sort=fhl&ad=false')
	try:
		data = response.json()['apps']
	except Exception as e:
		pytest.fail(str(e) + f'\ndata={response.text}')

	p1 = data[0]['install_fee']
	if p1 is None:
		p1 = 0
	p2 = data[-1]['install_fee']
	if p2 is None:
		p2 = 0
	assert p1 >= p2, f'Sort apps by price from high to low, but the price of the first app is less than the price of the last app.'
