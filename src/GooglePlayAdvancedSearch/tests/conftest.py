import os

import pytest

import GooglePlayAdvancedSearch.tests.testUtils as testUtils


@pytest.fixture
def dbFilePath():
	return os.path.join(testUtils.getTestFolder(), '../../data/db.sqlite3')
