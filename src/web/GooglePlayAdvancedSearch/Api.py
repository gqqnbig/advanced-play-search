import os
import sys

from django.db import connection
from django.http import HttpResponse

from GooglePlayAdvancedSearch.shared.dbUtils import getAppCountInDatabase

def getAppCount(request):
	with connection.cursor() as cursor:
		count = getAppCountInDatabase(cursor)
		response = HttpResponse(count, content_type="text/plain")

		response['Cache-Control'] = "private, max-age=3600"
		return response
