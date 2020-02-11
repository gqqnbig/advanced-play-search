import os
import sys

from django.db import connection
from django.http import HttpResponse

# import local packages
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../..'))
from GooglePlayAdvancedSearch.DBUtils import getAppCountInDatabase

def getAppCount(request):
	with connection.cursor() as cursor:
		count = getAppCountInDatabase(cursor)
		response = HttpResponse(count, content_type="text/plain")

		response['Cache-Control'] = "private, max-age=3600"
		return response
