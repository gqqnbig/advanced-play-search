import os
import re
import requests
import sys

from django.db import connection
from django.shortcuts import render
from json import loads as jsonLoads

# import local packages
sys.path.append('..')
from scraper.Models import AppItem


def index(request):
	context = {}
	with connection.cursor() as cursor:
		cursor.execute('select count(*) from app')
		context['appCount'] = cursor.fetchone()[0]

	return render(request, 'index.html', context)


def keyword_search(request):
	keyword = request.POST['keyword']

	url = 'http://play.google.com/store/search?q=%s&c=apps' % keyword
	page = requests.get(url)

	# "key: 'ds:3'" is not reliable.
	matches = re.findall(r'<script.*?>AF_initDataCallback\(\s*{.*?data:function\(\){return\s+(\[.+?\])\s*}\s*}\s*\)\s*;\s*</script>', page.text, flags=re.DOTALL)
	data = jsonLoads(matches[-1])
	data = data[0][1]

	app_ids = []
	while True:
		appsData = data[0][0][0]
		print(f'Load {len(appsData)} apps.')
		for app in appsData:
			appInfo = AppItem()
			appInfo['appName'] = app[2]
			appInfo['id'] = app[12][0]
			appInfo['rating'] = app[6][0][2][1][1]
			if app[7]:
				appInfo['install_fee'] = float(re.search(r'\d+\.\d*', app[7][0][3][2][1][0][2])[0])
			else:
				appInfo['install_fee'] = 0
			print(appInfo)
			app_ids.append(appInfo['id'])

		# save the apps
		if data[0][0][-2]:
			pageToken = data[0][0][-2][1]
		else:
			break

		print('continue searching')
		response = requests.post(r'https://play.google.com/_/PlayStoreUi/data/batchexecute?rpcids=qnKhOb&hl=en',
								 headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
								 data={'f.req': r'[[["qnKhOb","[[null,[[10,[10,50]],true,null,[96,27,4,8,57,30,110,79,11,16,49,1,3,9,12,104,55,56,51,10,34,31,77],[null,null,null,[[[[7,31],[[1,52,43,112,92,58,69,31,19,96]]]]]]],null,\"'
												+ pageToken
												+ r'\"]]",null,"generic"]]]'})
		package = jsonLoads(response.text[response.text.index('\n') + 1:])
		data = jsonLoads(package[0][2])

	print(f'total results: {len(app_ids)}')

	context = {}
	context['app_ids'] = app_ids
	context['previous_keyword'] = keyword
	os.system(('python ' if sys.platform == 'win32' else '') + "../scraper/Program.py -p %s" % ",".join(app_ids))
	with connection.cursor() as cursor:
		cursor.execute('select count(*) from app')
		context['appCount'] = cursor.fetchone()[0]

	return render(request, 'index.html', context)
