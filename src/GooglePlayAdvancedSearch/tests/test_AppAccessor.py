from GooglePlayAdvancedSearch.DBUtils import AppAccessor
from GooglePlayAdvancedSearch.Models import AppItem


def test_getCompleteAppInfoPartial():
	app = AppItem()
	app['name'] = 'test app'
	app['id'] = 'testid'
	app['rating'] = 1
	app['install_fee'] = 0
	app['app_icon'] = ''

	appAccessor = AppAccessor()
	appAccessor.insertOrUpdateApp(app)

	assert appAccessor.getCompleteAppInfo('testid') is None, "Database only has partial info."
