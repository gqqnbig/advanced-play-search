import os
import sys
from collections import Counter

import pytest

testFolder = os.path.dirname(os.path.abspath(__file__))

# import local packages
sys.path.append(os.path.join(testFolder, '../web'))
import GooglePlayAdvancedSearch.django.web.apiHelper as apiHelper



def test_searchNoDuplicate():
	result = apiHelper.searchGooglePlay('youtube')
	assert len(result) > 0, "Failed to find any match for keyword 'youtube'."
	duplicates = [(item, count) for item, count in Counter(result).items() if count > 1]
	if len(duplicates):
		pytest.fail(f'view.searchGooglePlay returns duplicate results: {duplicates}', False)


def test_searchKeywordEscpaing():
	result = apiHelper.searchGooglePlay('calculator&type=swimming')
	assert any('swimming' in app['name'] for app in result), '"calculator&type=swimming" should be considered as a single keyword. Results matching swimming are expected.'


if __name__ == '__main__':
	test_searchKeywordEscpaing()
