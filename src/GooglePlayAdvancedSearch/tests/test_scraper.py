import os
import sqlite3

import pytest

import GooglePlayAdvancedSearch.Errors
import GooglePlayAdvancedSearch.tests.testUtils as testUtils


def test_scrapeAppsWithExoticPermissions(dbFilePath):
	"""
	Scrape apps with no permissions, only other permissions, etc.
	Make sure scraper can correctly handle them.
	:return:
	"""

	testCases = {'kr.co.kcp.wechatpaycheckout',
				 'com.om.calc',
				 'com.appdevgenie.electronicscalculator',
				 'com.androidapps.unitconverter',
				 'com.i2mobil.minidb'
				 'com.dynamicg.homebuttonlauncher'
				 }

	if os.path.exists(dbFilePath):
		os.remove(dbFilePath)

	testUtils.runScraper(['--pytest', '-p', ','.join(testCases)])
	assert os.path.exists(dbFilePath), "Database file is not created."

	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()
	cursor.execute('select id from App')

	s = set([r[0] for r in cursor.fetchall()])
	connection.close()
	failedCases = testCases - s

	if len(failedCases) > 0:
		pytest.fail('Failed to scrape ' + ', '.join(failedCases))


def test_sslVerify():
	completed = testUtils.runScraper(['--pytest', '--bad-ssl-url', 'https://expired.badssl.com/'])
	assert completed.returncode == GooglePlayAdvancedSearch.Errors.sslErrorCode, 'Expect to detect invalid SSL certificate'
