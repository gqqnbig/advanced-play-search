import os
import sys

import django.http

from django.db import connection
from django.shortcuts import render

# import local packages
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))
import GooglePlayAdvancedSearch.DBUtils


def index(request):
	context = {}
	with connection.cursor() as cursor:
		context['categories'] = GooglePlayAdvancedSearch.DBUtils.getAllCategories(cursor)
		context['permissions'] = GooglePlayAdvancedSearch.DBUtils.getAllPermissions(cursor)

	context['ShowRecentSearch'] = True
	return render(request, 'index.html', context)


def keyword_search(request: django.http.HttpRequest):
	context = {}
	context['isSearch'] = True
	context['refetchAppCount'] = True
	context['subtitle'] = request.GET.get('q', '').strip()
	return render(request, 'index.html', context)


