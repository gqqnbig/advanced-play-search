# CS 188 Project - Google Play Advanced Search

![](https://github.com/cs188-software-design-security-w20/project-random/workflows/Python%20application/badge.svg)

## Install
Run `pip install -r requirements.txt` to install the dependencies. If you see conflicts, like "something has requirements xxx but you'll have xxx", you will need to update your pip.

## Test
Run `pytest --rootdir=src/tests` in project root.

If you want to run a single test file, use `pytest src/tests/test_scraper.py` or check [pytest documentation](https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests)

If you see warnings like "the imp module is deprecated in favour of importlib", add option `--disable-pytest-warnings`.

## Execute

Run `python manage.py runserver` in `src/web` folder for the website.

Run `python Program.py` in `src/scraper` folder for the web scraper.

Run server:
(cs188) root@server:/project-random/src/web# nohup uwsgi --uid 1003 --gid 1004 --socket /tmp/GooglePlayAdvancedSearch.sock --module GooglePlayAdvancedSearch.wsgi --chmod-socket=666 &> /tmp/django.log &

## Related Projects
https://github.com/facundoolano/google-play-scraper/ It's a Node.js scraper to get data from Google Play. It's a Nodejs library and provides some RESTful API support. This project helped us understand some Google Play behavior.


