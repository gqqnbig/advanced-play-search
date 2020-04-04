import os
import re
import requests
import sys

from django.db import connection
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.cache import cache_control
from json import loads as jsonLoads
from typing import List, Dict, Union
from urllib.parse import urlparse

# import local packages
import GooglePlayAdvancedSearch.Errors
from GooglePlayAdvancedSearch.DBUtils import AppAccessor

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))
import GooglePlayAdvancedSearch.DBUtils
from GooglePlayAdvancedSearch.Models import AppItem


@cache_control(max_age=3600)
def getAppCount(request):
	with connection.cursor() as cursor:
		count = GooglePlayAdvancedSearch.DBUtils.getAppCountInDatabase(cursor)
		response = HttpResponse(count, content_type="text/plain")

		return response


def getPermissions(request):
	with connection.cursor() as cursor:
		permissions = GooglePlayAdvancedSearch.DBUtils.getAllPermissions(cursor)

		# json doesn't allow integer keys. Remember to handle that in the html.
		response = JsonResponse(permissions, safe=False)
		response['Cache-Control'] = "private, max-age=" + str(len(permissions) * len(permissions))
		return response


def getCategories(request):
	with connection.cursor() as cursor:
		categories = GooglePlayAdvancedSearch.DBUtils.getAllCategories(cursor)
		response = JsonResponse(categories, safe=False)
		response['Cache-Control'] = "private, max-age=" + str(len(categories) * len(categories))
		return response


def search(request):
	keyword = request.GET['q']
	excludedPIds = [int(n) for n in request.GET.get('pids', '').split(',') if n != '']

	excludedCIds = [int(n) for n in request.GET.get('cids', '').split(',') if n != '']

	try:
		appAccessor = AppAccessor(1)
		appInfos = appAccessor.searchApps(keyword)

		needCompleteInfo = determineAppInfoCompleteness(request)

		if needCompleteInfo:
			appInfos = getCompleteAppInfo([a['id'] for a in appInfos])

		if len(excludedPIds):
			appInfos = [a for a in appInfos if isExcluded(a['permissions'], excludedPIds) == False]
		if len(excludedCIds):
			appInfos = [a for a in appInfos if isExcluded(a['categories'], excludedCIds) == False]


		# If we cannot find 200 matches from our database, we try to find more matches from Google.
		if len(appInfos) < 200:
			appInfos2 = searchGooglePlay(keyword)
			if needCompleteInfo:
				appInfos2 = getCompleteAppInfo([a['id'] for a in appInfos2])
			if len(excludedPIds):
				appInfos2 = [a for a in appInfos2 if isExcluded(a['permissions'], excludedPIds) == False]
			if len(excludedCIds):
				appInfos2 = [a for a in appInfos2 if isExcluded(a['categories'], excludedCIds) == False]


			appInfoIds = {a['id'] for a in appInfos}
			appInfos.extend([a for a in appInfos2 if a['id'] not in appInfoIds])

		sortType = request.GET.get('sort')
		if sortType == 'rlh':  # rating low to high
			appInfos = sorted(appInfos, key=lambda a: a['rating'])
		elif sortType == 'rhl':  # rating high to low
			appInfos = sorted(appInfos, key=lambda a: a['rating'], reverse=True)
		elif sortType == 'plh':  # number of permissions low to high
			appInfos = sorted(appInfos, key=lambda a: len(a['permissions']))
		elif sortType == 'phl':  # number of permissions low to high
			appInfos = sorted(appInfos, key=lambda a: len(a['permissions']), reverse=True)

		response = JsonResponse({'apps': [dict(a) for a in appInfos]}, safe=False)
		response['Cache-Control'] = "private, max-age=3600"
		return response
	except requests.exceptions.SSLError as e:
		# In getCompleteAppInfo, we throw our own SSLError where we don't have request object.
		if e.request:
			url = urlparse(e.request.url)
			return JsonResponse({'error': f'Searching is aborted because secure connection to https://{url.netloc} is compromised.\nAttacker is attacking us, but we didn\'t leak your data!'})
		else:
			return JsonResponse({'error': f'Searching is aborted because secure connection is compromised.\nAttacker is attacking us, but we didn\'t leak your data!'})


def determineAppInfoCompleteness(request):
	"""
	If user filter by permissions or sort by the number of permission, we must return the complete app information.
	"""
	if request.GET.get('pids'):
		return True
	if request.GET.get('cids'):
		return True
	if request.GET.get('sort') == 'phl' or request.GET.get('sort') == 'plh':
		return True
	else:
		with connection.cursor() as cursor:
			permissions = GooglePlayAdvancedSearch.DBUtils.getAllPermissions(cursor)
			if len(permissions) == 0:
				return True
	return False

def isExcluded(d: Dict, ids: List[int]):
	return any(excludedId in d for excludedId in ids)


def searchGooglePlay(keyword) -> List[AppItem]:
	url = 'https://play.google.com/store/search?q=%s&c=apps' % keyword
	page = requests.get(url, verify=True)

	# "key: 'ds:3'" is not reliable.
	matches = re.findall(r'<script.*?>AF_initDataCallback\(\s*{.*?data:function\(\){return\s+(\[.+?\])\s*}\s*}\s*\)\s*;\s*</script>', page.text, flags=re.DOTALL)
	data = jsonLoads(matches[-1])
	data = data[0][1]

	if not data:
		print("We couldn't find anything for your search.")
		return []

	appInfos = []

	appSaver = GooglePlayAdvancedSearch.DBUtils.AppAccessor(1)
	try:
		while True:
			appsData = data[0][0][0]
			print(f'Load {len(appsData)} apps.')
			for app in appsData:
				appId = app[12][0]
				if any(a['id'] == appId for a in appInfos):
					print(f'Duplicate app id {appId}.')
					continue

				appInfo = AppItem()
				appInfo['name'] = app[2]
				appInfo['id'] = appId
				appInfo['rating'] = app[6][0][2][1][1]
				appInfo['app_icon'] = app[1][1][0][3][2]
				if app[7]:
					appInfo['install_fee'] = float(re.search(r'\d+\.\d*', app[7][0][3][2][1][0][2])[0])
				else:
					appInfo['install_fee'] = 0
				print(appInfo['id'])

				appSaver.insertOrUpdateApp(appInfo)

				appInfos.append(appInfo)

			if data[0][0][-2]:
				pageToken = data[0][0][-2][1]
			else:
				break

			print('continue searching')
			response = requests.post(r'https://play.google.com/_/PlayStoreUi/data/batchexecute?rpcids=qnKhOb&hl=en',
									 headers={"Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"},
									 data={'f.req': r'[[["qnKhOb","[[null,[[10,[10,50]],true,null,[96,27,4,8,57,30,110,79,11,16,49,1,3,9,12,104,55,56,51,10,34,31,77],[null,null,null,[[[[7,31],[[1,52,43,112,92,58,69,31,19,96]]]]]]],null,\"'
													+ pageToken
													+ r'\"]]",null,"generic"]]]'},
									 verify=True)
			package = jsonLoads(response.text[response.text.index('\n') + 1:])
			data = jsonLoads(package[0][2])

	except:
		print('appsData:')
		print(appsData)
	return appInfos


def getCompleteAppInfo(app_ids: List[str]) -> List[AppItem]:
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

	appAccessor = AppAccessor(1)
	with connection.cursor() as cursor:
		# very important!
		# connection.cursor() gives django cursor, connection.cursor().connection.cursor() gives underlying sqlite cursor.
		# django cursor and sqlite cursor uses different parameter style!
		if GooglePlayAdvancedSearch.DBUtils.getAppCountInDatabase(cursor) > 0:
			# search database first pass. If the app isn't in database, leave it none. We will fill in the second pass.
			app_infos = {id: appAccessor.getCompleteAppInfo(id) for id in app_ids}
		else:
			app_infos = {id: None for id in app_ids}

	# search database second pass
	# for first-pass non-found apps, pass into scraper
	appsMissingInDatabase = [k for k, v in app_infos.items() if v is None]

	code2 = os.system(('python ' if sys.platform == 'win32' else '') + "../scraper/Program.py -p %s" % ",".join(appsMissingInDatabase))
	if hasattr(os, 'WEXITSTATUS') and os.WEXITSTATUS(code2) == GooglePlayAdvancedSearch.Errors.sslErrorCode \
		or not hasattr(os, 'WEXITSTATUS') and code2 == GooglePlayAdvancedSearch.Errors.sslErrorCode:
		raise requests.exceptions.SSLError()

	appAccessor = AppAccessor(1)
	scraper_fail_id = []
	for id in appsMissingInDatabase:
		tmp = appAccessor.getCompleteAppInfo(id)
		if tmp:
			app_infos[id] = tmp
		else:
			assert id in app_infos
			app_infos[id] = {'id': id}  # if scraper fails, just pass "id" to appDetails to display
			scraper_fail_id.append(id)

	print("Scraper failed %d times: %s" % (len(scraper_fail_id), ", ".join(scraper_fail_id)))
	print(f'total results: {len(app_ids)}')
	print("There were %d ids not in our database or stale. %d are now added" % (len(appsMissingInDatabase), len(appsMissingInDatabase) - len(scraper_fail_id)))

	assert None not in app_infos.values(), "Every app id returned from Google should have an app detail."
	return list(app_infos.values())
