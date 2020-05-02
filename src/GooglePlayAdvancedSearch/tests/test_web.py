import os
import pytest
import re
import requests
import shutil
import time

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

import GooglePlayAdvancedSearch.tests.testUtils as testUtils

testFolder = os.path.dirname(os.path.abspath(__file__))


def callback_testResponse(websiteUrl):
	response = requests.get(websiteUrl, verify=True)
	if response.status_code != 200:
		pytest.fail(str(response.status_code) + ' ' + response.reason)


def test_websiteEmptyStart(dbFilePath):
	try:
		if os.path.exists(dbFilePath):
			os.remove(dbFilePath)
	except Exception as e:
		pytest.skip(str(e))

	testUtils.startWebsite(callback_testResponse)


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

		driver.get(websiteUrl+'/search?q=')
		time.sleep(2)
		assert '&lt;/html&gt;' not in driver.page_source, 'Even if API returns 500 error code, the search page should not show the raw response.'



def test_ApiErrorNotLeaking():
	apiFilePath= os.path.join(testFolder, '../django/web/Api.py')
	backup=apiFilePath+".bk"
	shutil.copyfile(apiFilePath,backup)

	try:
		with open(apiFilePath, 'r+') as file:
			data = file.read()
			data= re.sub(r"(^def\s.+:[\r\n][\r\n]?)",r"\1\traise Exception()\n",data, flags=re.MULTILINE)
			file.seek(0)
			file.write(data)
			file.truncate()

		testUtils.startWebsite(callback_testApiErrorNotLeaking)
	finally:
		os.remove(apiFilePath)
		shutil.move(backup,apiFilePath)



# Allow the file to be run by itself, not in the pytest environment.
# It's for easy development.
if __name__ == "__main__":
	test_websiteEmptyStart()
