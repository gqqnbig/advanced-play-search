import os
import pytest
import sys

from collections import Counter

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