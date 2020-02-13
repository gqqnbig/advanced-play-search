def getAllPermissions(cursor):
	cursor.execute('Pragma table_info(App)')
	columns = cursor.fetchall()
	permissions = [c[1][11:] for c in columns if c[1].startswith("permission_")]
	return permissions


def getAllCategories(cursor):
	cursor.execute('Pragma table_info(App)')
	columns = cursor.fetchall()
	categories = [c[1][9:] for c in columns if c[1].startswith("category_")]
	return categories
