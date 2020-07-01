#!/usr/bin/env python3
import os
import sqlite3


# def clearUpBooleanColumns(cursor, columnNames):
# 	for pid, permission in permissions:
# 		cursor.execute(f'select 1 from app where {permission}=1')
# 		if cursor.fetchone() is None:
# 			# the permission is not used
# 			cursor.execute(f'alter table app drop column {GooglePlayAdvancedSearch.DBUtils.delimiteDBIdentifier(permission)}')
# 			connection.commit()

MAX_RECORD_DAYS = 14
APP_FRESH_DAYS = 7

if __name__ == "__main__":
	connection = sqlite3.connect(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/db.sqlite3'))
	cursor = connection.cursor()
	cursor.execute("delete from app where updateDate<date('now','-" + str(APP_FRESH_DAYS) + " days')")
	print(f'removed {cursor.rowcount} apps cached since {APP_FRESH_DAYS} days ago.')

	cursor.execute("delete from Search where [date]<date('now','-" + str(MAX_RECORD_DAYS) + " days')")
	print(f'removed {cursor.rowcount} search records since {MAX_RECORD_DAYS} days ago.')

	connection.commit()
	connection.close()

# We may want to remove unused permissions or categories.
# However SQLite doesn't support drop columns.
# if removedCount > 0:
# 	permissions = GooglePlayAdvancedSearch.DBUtils.getAllPermissions(cursor)
