from django.db import OperationalError


def getAppCountInDatabase(cursor):
	try:
		cursor.execute('select count(*) from app')
		return cursor.fetchone()[0]
	except OperationalError:  # no such table: app
		return 0