import os
import time

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

testFolder = os.path.dirname(os.path.abspath(__file__))


def test_RateLimitWithoutGA(websiteUrl):
	options = Options()
	options.headless = True
	with Firefox(options=options) as driver:
		driver.delete_all_cookies()

		# without loading Google Analysis, the 4th load of search API causes error.
		driver.get(websiteUrl + '/Api/Search?q=')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&&')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&&&')
		assert 'Rate limit reached.' in driver.page_source


def test_RateLimitWithGA(websiteUrl):
	options = Options()
	options.headless = True
	with Firefox(options=options) as driver:
		driver.delete_all_cookies()
		driver.get(websiteUrl + '/search?q=')
		time.sleep(2)
		driver.get(websiteUrl + '/Api/Search?q=')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&&')
		assert 'Rate limit reached.' not in driver.page_source
		driver.get(websiteUrl + '/Api/Search?q=&&&')
		assert 'Rate limit reached.' not in driver.page_source


if __name__ == '__main__':
	test_RateLimitWithGA('http://127.0.0.1:8000')
