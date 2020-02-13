import os
import re
import requests
import sys

from django.db import connection
from django.shortcuts import render
from json import loads as jsonLoads
from typing import List

# import local packages
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
from Models import AppItem
from web.shared.dbUtils import getAppCountInDatabase


def index(request):
	context = {}
	(context['categories'], context['permissions']) = getPermissionCategory()
	return render(request, 'index.html', context)


def keyword_search(request):
	context = {}
	keyword = request.POST['keyword']
	context['previous_keyword'] = keyword
	context['refetchAppCount'] = True

	app_ids = searchGooglePlay(keyword)

	context['app_infos'] = getAppInfo(app_ids)
	(context['categories'], context['permissions']) = getPermissionCategory()

	return render(request, 'index.html', context)


def searchGooglePlay(keyword):
	url = 'https://play.google.com/store/search?q=%s&c=apps' % keyword
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
			appId = app[12][0]
			if appId in app_ids:
				print(f'Duplicate app id {appId}.')
				continue

			appInfo = AppItem()
			appInfo['appName'] = app[2]
			appInfo['id'] = appId
			appInfo['rating'] = app[6][0][2][1][1]
			if app[7]:
				appInfo['install_fee'] = float(re.search(r'\d+\.\d*', app[7][0][3][2][1][0][2])[0])
			else:
				appInfo['install_fee'] = 0
			print(appInfo['id'])

			app_ids.append(appId)

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
	return app_ids


def getAppInfo(app_ids: List[str]):
	"""
	search the app_ids in database or retrieve from Google Play.

	run scraper against the apps that are not in our database
	if scraper failed for some app_id, their corresponding app_info will have only app_id

	:param app_ids: list of app_id
	:return:    list of dictionary(set). each set represents the app_info of the corresponding app_id,
                the return list have the same length as the input list
	"""

	if len(app_ids) == 0:
		return []

	# https://stackoverflow.com/a/39537308/746461
	# Python 3.6 and up keeps dict insertion order.
	# Python 3.7 formalizes it to a language specification.
	if sys.version_info < (3, 6):
		# sys.version_info is a named tuple. https://docs.python.org/3/glossary.html#term-named-tuple
		print(f'Python {tuple(sys.version_info)} may not keep dictionary insertion order. Upgrade to at least version 3.6.', file=sys.stderr)

	with connection.cursor() as cursor:
		if getAppCountInDatabase(cursor) > 0:
			# search database first pass. If the app isn't in database, leave it none. We will fill in the second pass.
			app_infos = {id: getAppInfoInDatabase(cursor, id) for id in app_ids}
		else:
			app_infos = {id: None for id in app_ids}

	# search database second pass
	# for first-pass non-found apps, pass into scraper
	appsMissingInDatabase = [k for k, v in app_infos.items() if v is None]
	os.system(('python ' if sys.platform == 'win32' else '') + "../scraper/Program.py -p %s" % ",".join(appsMissingInDatabase))

	scraper_fail_id = []
	with connection.cursor() as cursor:
		for id in appsMissingInDatabase:
			tmp = getAppInfoInDatabase(cursor, id)
			if tmp:
				app_infos[id] = tmp
			else:
				assert id in app_infos
				app_infos[id] = {'id': id}  # if scraper fails, just pass "id" to appDetails to display
				scraper_fail_id.append(id)

	print("Scraper failed %d times: %s" % (len(scraper_fail_id), ", ".join(scraper_fail_id)))
	print(f'total results: {len(app_ids)}')
	print("There were %d ids not in our database. %d are now added" % (len(appsMissingInDatabase), len(appsMissingInDatabase) - len(scraper_fail_id)))

	assert None not in app_infos.values(), "Every app id returned from Google should have an app detail."
	return app_infos.values()


def getAppInfoInDatabase(cursor, id):
	"""
	Find app id in database. If found, return the data, otherwise return null.
	"""

	cursor.execute("SELECT name,rating,num_reviews,install_fee,inAppPurchases,app_icon FROM App WHERE id=:id", {"id": id})
	tmp = cursor.fetchone()
	if tmp:
		return {
			'name': tmp[0],
			'rating': tmp[1],
			'num_reviews': tmp[2],
			'install_fee': tmp[3],
			'inAppPurchases': tmp[4],
			'id': id,
			'app_icon': tmp[5]

		}
	else:
		return None


def getPermissionCategory():
	with connection.cursor() as cursor:
		cursor.execute('Pragma table_info(App)')
		columns = cursor.fetchall()
		columnNames = [c[1] for c in columns]
		categories = []
		permissions = []
		for i in columnNames:
			if i.startswith("category_"):
				categories.append(i[9:])
			if i.startswith("permission_"):
				permissions.append(i[11:])

		assert getAppCountInDatabase(cursor) == 0 or len(categories) + len(permissions) > 0, "There are apps in database, but there are no categories or permissions."
		return (categories, permissions)
