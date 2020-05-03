import os

import pytest
import requests

import GooglePlayAdvancedSearch.tests.testUtils as testUtils

"""
Test the website using regular python/requests without executing JavaScript or advanced browsing features.

If you need to execute JavaScript for testing, write tests in test_selenium.py. 
"""

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



def test_localization(websiteUrl):
	response = requests.get(websiteUrl,headers={'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6'})
	assert '高级搜索' in response.text

	response = requests.get(websiteUrl)
	assert '高级搜索' not in response.text


def test_djangoTagNotLeaking(websiteUrl):
	response = requests.get(websiteUrl)
	assert '{% ' not in response.text

	response = requests.get(websiteUrl + "/search?q=")
	assert '{% ' not in response.text


# Allow the file to be run by itself, not in the pytest environment.
# It's for easy development.
if __name__ == "__main__":
	test_websiteEmptyStart()
