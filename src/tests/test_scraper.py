import io
import os
import pytest
import sqlite3
import subprocess
import sys

testFolder = os.path.dirname(os.path.abspath(__file__))


def test_scrapeAppsWithExoticPermissions():
	"""
	Scrape apps with no permissions, only other permissions, etc.
	Make sure scraper can correctly handle them.
	:return:
	"""

	testCases = {'com.om.calc',
				 'com.appdevgenie.electronicscalculator',
				 'com.androidapps.unitconverter',
				 'com.videos.freemusic.song.mp3.musicplayer.mv'}

	dbFilePath = os.path.join(testFolder, '../data/db.sqlite3')
	if os.path.exists(dbFilePath):
		os.remove(dbFilePath)

	if sys.platform == 'win32':
		args = ['python', 'Program.py']
	else:
		args = ['./Program.py']
	args.extend(['--pytest', '-p', ','.join(testCases)])
	subprocess.run(args, cwd=os.path.join(testFolder, '../scraper'))

	assert os.path.exists(dbFilePath), "Database file is not created."

	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()
	cursor.execute('select id from App')

	s = set([r[0] for r in cursor.fetchall()])
	failedCases = testCases - s

	if len(failedCases) > 0:
		pytest.fail('Failed to scrape ' + ', '.join(failedCases))
