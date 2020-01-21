from django.http import HttpResponse
from django.shortcuts import render

from django.db import connection

import requests
import os

from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess


def index(request):
	context = {}
	with connection.cursor() as cursor:
		cursor.execute('select count(*) from app')
		context['appCount'] = cursor.fetchone()[0]

	return render(request, 'index.html', context)


process = CrawlerProcess(settings={
	#'LOG_ENABLED': False,
	'ITEM_PIPELINES': {
		'pipeline.DatabasePipeline': 300,
	}
})


def keyword_search(request):
	keyword = request.POST['keyword']

	url = 'http://play.google.com/store/search?q=%s&c=apps' % keyword
	page = requests.get(url)
	soup = BeautifulSoup(page.text, 'html.parser')
	app_box = soup.select('div[class*=Ktdaqe ] a[href] div[class][title]')
	app_urls = []
	for i in app_box:
		app_urls.append("http://play.google.com%s" % i.parent['href'])

	os.system("./Program.py -p %s" % ",".join(app_urls))

	return render(request, 'index.html', {'urls': app_urls, 'previous_keyword': keyword})


