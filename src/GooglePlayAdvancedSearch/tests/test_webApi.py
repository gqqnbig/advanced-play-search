import os
import sqlite3

import requests

import GooglePlayAdvancedSearch.DBUtils
import GooglePlayAdvancedSearch.tests.testUtils as testUtils


def callback_searchPermissionFilter():
	# com.tencent.mm uses permission 'read the contents of your USB storage'
	# We exclude this permission in the search, and make sure the result doesn't have com.tencent.mm.

	testUtils.runScraper(['--pytest', '-p', 'com.tencent.mm'])

	dbFilePath = os.path.join(testUtils.getTestFolder(), '../../data/db.sqlite3')
	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()
	permissions = GooglePlayAdvancedSearch.DBUtils.getAllPermissions(cursor)
	pid = next((k for k, v in permissions.items() if 'read the contents of your USB storage' in v), None)

	response = requests.get('http://localhost:8090/Api/Search?q=wechat&pids=' + str(pid), verify=True)
	text = response.text
	assert 'com.tencent.mm' not in text, "Search for wechat without storage permission. The search result should not have wechat."

	response = requests.get('http://localhost:8090/Api/Search?q=wechat', verify=True)
	text = response.text
	assert 'com.tencent.mm' in text, "Search for wechat allowing storage permission. The search result not have wechat."


def test_searchPermissionFilter():
	testUtils.startWebsite(callback_searchPermissionFilter)

if __name__ == "__main__":
	test_searchPermissionFilter()