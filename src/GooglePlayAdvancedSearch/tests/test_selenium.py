import os
import re
import shutil
import sqlite3
import sys
import time

import pytest
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

import GooglePlayAdvancedSearch.DBUtils
import GooglePlayAdvancedSearch.tests.testUtils as testUtils

testFolder = os.path.dirname(os.path.abspath(__file__))

# import packages in sibling folders
sys.path.append(os.path.join(testFolder, '../web'))
import GooglePlayAdvancedSearch.django.web.apiHelper as apiHelper


def test_RecentSearchDateOnFirefox(dbFilePath, websiteUrl):
	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()

	if GooglePlayAdvancedSearch.DBUtils.doesTableExist('Search', cursor):
		cursor.execute('delete from Search')
	else:
		cursor.execute(apiHelper.getSqlCreateTableSearch())

	cursor.execute('insert into Search Values("students","q=students","127.0.0.1","1989-06-04 04:00:00")')
	connection.commit()

	options = Options()
	options.headless = True
	with Firefox(options=options) as driver:
		driver.get(websiteUrl)
		time.sleep(2)
		innerText = driver.execute_script("return document.getElementById('recentSearches').innerText")
		assert '1989' in innerText and '6' in innerText, "Recent searches is expected to show a search on 1989-06-04"


def test_RateLimitWithoutGA(websiteUrl):
	options = Options()
	options.headless = True
	with Firefox(options=options) as driver:
		driver.delete_all_cookies()

		# without loading Google Analysis, the 4th load of search API causes error.
		driver.get(websiteUrl + '/Api/Search?q=')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&&')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&&&')
		assert 'Rate limit reached.' in driver.page_source


def test_RateLimitWithGA(websiteUrl):
	options = Options()
	options.headless = True
	with Firefox(options=options) as driver:
		driver.delete_all_cookies()
		driver.get(websiteUrl + '/search?q=')
		time.sleep(2)
		driver.get(websiteUrl + '/Api/Search?q=')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&&')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&&&')
		assert 'Rate limit reached.' not in driver.page_source


def test_keywordNull(websiteUrl):
	options = Options()
	options.headless = True
	try:
		with Firefox(options=options) as driver:
			driver.get(websiteUrl)
			driver.find_element_by_css_selector('label input[type=checkbox]').click()
			driver.find_element_by_css_selector('#searchBox a').click()

			assert 'q=null' not in driver.current_url
	except NoSuchElementException as e:
		pytest.skip(f'Unable to find required element {str(e)}')


def callback_testApiErrorNotLeaking(websiteUrl):
	options = Options()
	options.headless = True
	with Firefox(options=options) as driver:
		driver.get(websiteUrl)
		# get function returns when the page is loaded. However, there are javascript events listening the onload event, and run after this.
		# Therefore we have to wait additional time.
		time.sleep(2)
		# driver.save_screenshot('test_ApiErrorNotLeaking.png')
		assert '&lt;/html&gt;' not in driver.page_source, 'Even if API returns 500 error code, the home page should not show the raw response.'

		driver.get(websiteUrl + '/search?q=')
		time.sleep(2)
		assert '&lt;/html&gt;' not in driver.page_source, 'Even if API returns 500 error code, the search page should not show the raw response.'


def test_ApiErrorNotLeaking():
	apiFilePath = os.path.join(testFolder, '../django/web/Api.py')
	backup = apiFilePath + ".bk"
	shutil.copyfile(apiFilePath, backup)

	try:
		with open(apiFilePath, 'r+') as file:
			data = file.read()
			data = re.sub(r"(^def\s.+:[\r\n][\r\n]?)", r"\1\traise Exception()\n", data, flags=re.MULTILINE)
			file.seek(0)
			file.write(data)
			file.truncate()

		testUtils.startWebsite(callback_testApiErrorNotLeaking)
	finally:
		os.remove(apiFilePath)
		shutil.move(backup, apiFilePath)


if __name__ == '__main__':
	test_RateLimitWithGA('http://127.0.0.1:8000')
