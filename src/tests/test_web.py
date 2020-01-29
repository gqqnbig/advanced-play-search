import os
import subprocess
import sys
import time

import psutil
import pytest
import requests

testFolder = os.path.dirname(os.path.abspath(__file__))


def test_websiteEmptyStart():
	try:
		dbFilePath = os.path.join(testFolder, '../data/db.sqlite3')
		if os.path.exists(dbFilePath):
			os.remove(dbFilePath)
	except Exception as e:
		pytest.skip('what' + str(e))

	if sys.platform == 'win32':
		args = ['python', 'manage.py']
	else:
		args = ['./manage.py']
	args.extend(['runserver', '8090'])

	p = None
	try:
		p = subprocess.Popen(args, cwd=os.path.join(testFolder, '../web'))
		print('web server pid=' + str(p.pid))
		time.sleep(1)

		waitTime = 2
		while True:
			try:
				response = requests.get('http://localhost:8090')
				if response.status_code != 200:
					pytest.fail(str(response.status_code) + ' ' + response.reason)
				break
			except requests.exceptions.ConnectionError as e:
				if waitTime > 10:
					pytest.fail('Server is not up:\n' + str(e))
				time.sleep(waitTime)
				waitTime = waitTime * waitTime
	finally:
		if p:
			try:
				parent = psutil.Process(p.pid)
				for child in parent.children(recursive=True):
					child.kill()
				parent.kill()
			except Exception as e:
				print('Failed to kill web server processes.\n' + str(e))


# Allow the file to be run by itself, not in the pytest environment.
# It's for easy development.
if __name__ == "__main__":
	test_websiteEmptyStart()
