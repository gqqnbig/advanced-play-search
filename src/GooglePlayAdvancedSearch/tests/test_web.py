import os
import pytest
import requests

import GooglePlayAdvancedSearch.tests.testUtils as testUtils

testFolder = os.path.dirname(os.path.abspath(__file__))


def callback_testResponse():
	response = requests.get('http://localhost:8090')
	if response.status_code != 200:
		pytest.fail(str(response.status_code) + ' ' + response.reason)


def test_websiteEmptyStart():
	try:
		dbFilePath = os.path.join(testFolder, '../../data/db.sqlite3')
		if os.path.exists(dbFilePath):
			os.remove(dbFilePath)
	except Exception as e:
		pytest.skip(str(e))

	testUtils.startWebsite(callback_testResponse)


# Allow the file to be run by itself, not in the pytest environment.
# It's for easy development.
if __name__ == "__main__":
	test_websiteEmptyStart()
