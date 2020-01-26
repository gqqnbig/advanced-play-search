# CS 188 Project - Google Play Advanced Search
## Install
Run `pip install -r requirements.txt` to install the dependencies. If you see conflicts, like "something has requirements xxx but you'll have xxx", you will need to update your pip.

## Test
Run `pytest --root src/tests` in project root.

## Execute

Run `python manage.py runserver` in `src/web` folder for the website.

Run `python Program.py` in `src/scraper` folder for the web scraper.


# CS 188 Project Proposal

## Team name: Random

## 1. Team Membership:
    - Weikeng Yang - 405346443
    - Yingzhe Hu - 505366341
    - Qiqi Gu - 604253019
    - Dongyao Liang - 705313832
    - Shuhua Zhan - 705190671

## 2. Project Topic: Google Play App Filter

## 3. Project Description:
The project is a website searching apps on Google Play. It enhances the searching and filtering functions on Google Play so that users are able to filter apps by their permissions, whether they have ads, whether they have in-app purchase, free or paid, etc. Further, our website is able to sort apps by the number of permissions, price, stars, downloads, sort of metrics to facilitate use case “search free sqlite database app with no ads with only storage read/write permissions, sorted by rating”.
For gathering the app information, we will implement a web scraper which saves the app data into database. The web scraper will be written in Python3, as Python2 is out of official support, and we expect to save the data to SQLite3 or MySQL database. The backend of the website may be implemented in Python as well. The frontend will embrace JavaScript possibly with some frontend framework, eg. React. For simplicity, we will deploy the web scraper and the website on the same machine with Python. The machine will be running Linux or Windows system.
If we have time, we will try to implement an Android app for our Google Play App Filter. 

## 4. Privacy and security issues:

Our web scraper follows links on Google Play and intakes app data. We have to make sure not to follow malicious links or run malicious (JavaScript) code from the web. When saving app data to database, we need to prevent SQL injection as well.The search bar of our website is a big security risk. We have to code carefully to prevent SQL injection. When a user eventually find a desired app, our website will take him to the official Google Play page, during this process, we should be careful not to pass additional information to Google, protecting user’s privacy. Our website shall support HTTPS that protects users’ privacy and ensures content integrity.As of our Android app, we foresee that the app needs to acquire users’ permissions such as viewing WIFI connections, accessing pictures and videos. We should not require excessive permissions to reduce our attack surfaces. 
    
## 5. Schedule 

| Week     | Task           | 
| -------|:----------------------------:| 
| 1     | Scrape single app data | 
| 2     |Scrape apps on Google Play  |  
| 3     | Store app data into database, project design document  |    
|4      |Build website                            |
|5      |Query database from website|
|6      |Polish website UI          |
|7      |Optimize code, project prototype|

## 6. Assignments:
 - Weikeng Yang -
Database (subject to change)
 - Yingzhe Hu - 
Database (subject to change)
 - Qiqi Gu - 
Website (subject to change)
 - Dongyao Liang - 
Website (subject to change)
 - Shuhua Zhan -
Scraper (subject to change)

