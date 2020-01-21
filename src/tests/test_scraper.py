import io
import os
import sqlite3
import subprocess
import sys

testFolder = os.path.dirname(os.path.abspath(__file__))

def test_scraper():
	dbFilePath = os.path.join(testFolder, '../src/data/db.sqlite3')
	if os.path.exists(dbFilePath):
		os.remove(dbFilePath)

	if sys.platform == 'win32':
		args = ['python', 'Program.py']
	else:
		args = ['./Program.py']
	args.extend(['pytest'])
	subprocess.run(args, cwd=os.path.join(testFolder, '../src/scraper'))

	assert os.path.exists(dbFilePath), "Database file is not created."

	connection = sqlite3.connect(dbFilePath)
	cursor = connection.cursor()
	cursor.execute('select count(*) from App')
	assert cursor.fetchone()[0] == 3, 'Expecte to collect 3 apps.'
