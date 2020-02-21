import os
import subprocess
import sys
import time

import psutil
import pytest
import requests


def getTestFolder():
	return os.path.dirname(os.path.abspath(__file__))


def startWebsite(test):
	if sys.platform == 'win32':
		args = ['python', 'manage.py']
	else:
		args = ['./manage.py']
	args.extend(['runserver', '8090'])

	if 'PYTHONIOENCODING' not in os.environ or os.environ['PYTHONIOENCODING'] != 'UTF8':
		os.environ['PYTHONIOENCODING'] = 'UTF8'

	p = None
	try:
		p = subprocess.Popen(args, cwd=os.path.join(getTestFolder(), '../django'))
		print('web server pid=' + str(p.pid))
		time.sleep(1)

		waitTime = 2
		while True:
			try:
				response = requests.get('http://localhost:8090', verify=True)
				if test:
					test()
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

def runScraper(args):
	if sys.platform == 'win32':
		mainArgs = ['python', 'Program.py']
	else:
		mainArgs = ['./Program.py']
	mainArgs.extend(args)
	if 'PYTHONIOENCODING' not in os.environ or os.environ['PYTHONIOENCODING'] != 'UTF8':
		os.environ['PYTHONIOENCODING'] = 'UTF8'
	return subprocess.run(mainArgs, cwd=os.path.join(getTestFolder(), '../scraper'))
