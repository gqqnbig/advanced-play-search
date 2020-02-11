import os
import sys

from django.db import connection
from django.http import HttpResponse
from django.http import JsonResponse

# import local packages
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))
import GooglePlayAdvancedSearch.DBUtils


def getAppCount(request):
	with connection.cursor() as cursor:
		count = GooglePlayAdvancedSearch.DBUtils.getAppCountInDatabase(cursor)
		response = HttpResponse(count, content_type="text/plain")

		response['Cache-Control'] = "private, max-age=3600"
		return response


def getPermissions(request):
	with connection.cursor() as cursor:
		permissions = GooglePlayAdvancedSearch.DBUtils.getAllPermissions(cursor)
		response = JsonResponse(permissions, safe=False)
		response['Cache-Control'] = "private, max-age=" + str(len(permissions) * len(permissions))
		return response


def getCategories(request):
	with connection.cursor() as cursor:
		categories = GooglePlayAdvancedSearch.DBUtils.getAllCategories(cursor)
		response = JsonResponse(categories, safe=False)
		response['Cache-Control'] = "private, max-age=" + str(len(categories) * len(categories))
		return response
