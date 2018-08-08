"""cryptowallet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from . import views

app_name = 'crypto'

urlpatterns = [
    url(r'^$', views.home, name='home'),

    # All Accounts - /accounts/
    url(r'^accounts/$', views.accounts, name='accounts'),

    # Accounts Details - /accounts/<account>/
    url(r'^accounts/(?P<account>0x[a-fA-F0-9]+)/$', views.account_details, name='account_details'),

    # Accounts Details - /new_account/
    url(r'^new_account/$', views.new_account, name='new_account'),

    #create_new_account
    # url(r'^new_account/(?P<password>[a-fA-F0-9]+)/$', views.create_new_account, name='create_new_account'),

    # Tranasaction
    url(r'^new_account/send_transaction$', views.send_transaction, name='send_transaction'),
]
