import os
import pytest
import sys

from collections import Counter

testFolder = os.path.dirname(os.path.abspath(__file__))

# import local packages
sys.path.append(os.path.join(testFolder, '../web'))
import web.view


def test_searchNoMatchKeyword():
	web.view.searchGooglePlay('worldworldworldworldellohellohellohello')


def test_searchNoDuplicate():
	result = web.view.searchGooglePlay('youtube')

	duplicates = [(item,count) for item, count in Counter(result).items() if count > 1]
	if len(duplicates):
		pytest.fail(f'view.searchGooglePlay returns duplicate results: {duplicates}', False)
