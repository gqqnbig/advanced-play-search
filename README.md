# Google Play Advanced Search

![](https://github.com/gqqnbig/advanced-play-search/workflows/Python%20application/badge.svg)

The application is available at http://play.gqqnbig.me/.

Can't run the application? Check how [the application runs on GitHub Action Server](/.github/workflows/pythonapp.yml).

## Install
Run `pip install -r requirements.txt` to install the dependencies. If you see conflicts, like "something has requirements xxx but you'll have xxx", you will need to update your pip.

## Test
Run `pytest --rootdir=GooglePlayAdvancedSearch/tests` in the src folder.

If you want to run a single test file, use `pytest src/GooglePlayAdvancedSearch/tests/test_scraper.py` or check [pytest documentation](https://docs.pytest.org/en/latest/usage.html#specifying-tests-selecting-tests)

If you see warnings like "the imp module is deprecated in favour of importlib", add option `--disable-pytest-warnings`.

## Execute

Run `python manage.py runserver` in `src/web` folder for the website.

Run `python Program.py` in `src/scraper` folder for the web scraper.

Run server:
make sure to `conda activate cs188` first as root
(cs188) root@server:/project-random/src/GooglePlayAdvancedSearch/django# `nohup uwsgi --uid 1003 --gid 1004 --socket /tmp/GooglePlayAdvancedSearch.sock --module web.wsgi --chmod-socket=666 &> /tmp/django.log &`


## System Requirements
The project is best to run by Python 3.7. Ubuntu 19 comes with Python 3.7. If you are using other systems, eg. Ubuntu 16, whose repositories don't have Python 3.7, refrain from installing Python 3.7 because the official repositories not having Python 3.7 is for a reason. It's very likely that you are unable to install other dependencies, for instance sqlite 3.24+, django 3, etc.

Browsers supporting URLSearchParams, Chrome >=49, Edge>=17, Firefix>=29.

sqlite 3.24+. Check your version with 
```python
import sqlite3
sqlite3.sqlite_version
```
You may follow **install sqlite 3.31** section in [.github/workflows/pythonapp.yml](.github/workflows/pythonapp.yml).

## Deploy

Make use of the sparse checkout feature since Git 2.26.
```bash
git clone  --no-checkout --depth 1 https://github.com/gqqnbig/advanced-play-search.git
cd advanced-play-search
git sparse-checkout init --cone
git sparse-checkout add src
git sparse-checkout add deploy
git remote set-branches origin 'dev'
git fetch --all

sudo ln -s /var/www/play-search/deploy/systemd/system/play-search-staleAppRemover.service /lib/systemd/system/
sudo ln -s /var/www/play-search/deploy/systemd/system/play-search-staleAppRemover.timer /lib/systemd/system/
sudo ln -s /var/www/play-search/deploy/systemd/system/uwsgi-play-search.service /lib/systemd/system/

```

## Uninstall
```
rm /lib/systemd/system/play-search-staleAppRemover.service
rm /lib/systemd/system/play-search-staleAppRemover.timer
rm /lib/systemd/system/uwsgi-play-search.service
```


## Related Projects
https://github.com/facundoolano/google-play-scraper/ It's a Node.js scraper to get data from Google Play. It's a Nodejs library and provides some RESTful API support. This project helped us understand some Google Play behavior.

https://www.appbrain.com

https://playsearch.kaki87.net/ from https://android.stackexchange.com/a/202695/97993
