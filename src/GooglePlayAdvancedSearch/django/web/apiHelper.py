import re

import requests

from json import loads as jsonLoads
from typing import List

import GooglePlayAdvancedSearch.DBUtils
from GooglePlayAdvancedSearch.Models import AppItem


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