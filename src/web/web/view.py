from django.http import HttpResponse
from django.shortcuts import render

from django.db import connection


def index(request):
	context = {}
	with connection.cursor() as cursor:
		cursor.execute('select count(*) from app')
		context['appCount'] = cursor.fetchone()[0]

	return render(request, 'index.html', context)
