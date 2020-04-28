"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url
from django.urls import path

from . import view
from . import Api


urlpatterns = [
	path(r'', view.index, name='homepage'),
	path(r'search', view.keyword_search, name='keyword_search'),
	path(r'Api/AppCount', Api.getAppCount, name='Api/AppCount'),
	url(r'^Api/Permissions', Api.getPermissions, name='Api/Permissions'),
	url(r'^Api/Categories', Api.getCategories, name='Api/Categories'),
	url(r'^Api/Search', Api.search, name='Api/Search'),
	url(r'Api/Version', Api.version),
	path(r'Api/RecentSearches',Api.recentSearches, name='Api/RecentSearches'),
]
