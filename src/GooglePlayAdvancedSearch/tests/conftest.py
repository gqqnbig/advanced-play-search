import os
import subprocess
import sys
import time

import psutil
import pytest
import requests

import GooglePlayAdvancedSearch.tests.testUtils as testUtils


def websiteUrlCore():
	try:
		response = requests.get('http://localhost:8000', verify=True)
		yield 'http://localhost:8000'
		return
	except requests.exceptions.ConnectionError as e:
		pass

	if sys.platform == 'win32':
		args = ['python', 'manage.py']
	else:
		args = ['./manage.py']
	args.extend(['runserver', '--noreload', '8090'])

	if 'PYTHONIOENCODING' not in os.environ or os.environ['PYTHONIOENCODING'] != 'UTF8':
		os.environ['PYTHONIOENCODING'] = 'UTF8'

	p = None
	try:
		p = subprocess.Popen(args, cwd=os.path.join(testUtils.getTestFolder(), '../django'))
		print('web server pid=' + str(p.pid))
		time.sleep(1)

		waitTime = 2
		while True:
			try:
				response = requests.get('http://localhost:8090', verify=True)
				yield 'http://localhost:8090'
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


@pytest.fixture
def dbFilePath():
	return os.path.join(testUtils.getTestFolder(), '../../data/db.sqlite3')


@pytest.fixture
def websiteUrl():
	g = websiteUrlCore()
	yield next(g)
	next(g, None)
