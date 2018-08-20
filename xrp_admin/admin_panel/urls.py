"""xrp_admin URL Configuration

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

app_name = 'admin_panel'

urlpatterns = [

    # Login Screen - /admin_panel/
    url(r'^login_page/$', views.login_page, name='login_page'),

    #Log Out - /admin_panel/log_out
    url(r'^log_out/(?P<reason>.*)/$', views.log_out, name='log_out'),


    ### Admin - Starts

    # Admin Home Page - /admin_panel/admin_home
    url(r'^admin_home/$', views.admin_home, name='admin_home'),

    # Add Panel User - /admin_panel/admin_home/admin_add_panel_user
    url(r'^admin_home/admin_add_panel_user/$', views.admin_add_panel_user, name='admin_add_panel_user'),

    # Edit URL - /admin_panel/admin_home/admin_edit_url
    url(r'^admin_home/admin_edit_url/$', views.admin_edit_url, name='admin_edit_url'),

    ### Admin - Ends

    ### Super Admin - Starts

    # Admin Home Page - /admin_panel/super_admin_home
    url(r'^super_admin_home/$', views.super_admin_home, name='super_admin_home'),

    # Specific User Details - /admin_panel/super_admin_home/<user name>
    url(r'^super_admin_home/(?P<user_name>.*)/$', views.super_admin_user_details, name='super_admin_user_details'),

    # Add App User - /admin_panel/admin_home/super_add_app_user
    url(r'^admin_home/super_add_app_user/$', views.super_add_app_user, name='super_add_app_user'),

    # Add Panel User - /admin_panel/admin_home/super_add_panel_user
    url(r'^admin_home/super_add_panel_user/$', views.super_add_panel_user, name='super_add_panel_user'),

    ### Super Admin - Ends


]
