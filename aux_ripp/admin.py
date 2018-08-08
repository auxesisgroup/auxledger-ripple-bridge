# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models import User_Master,Address_Master,Transaction_Master

from django.contrib import admin

# Register your models here.
admin.site.register(User_Master)
admin.site.register(Address_Master)
admin.site.register(Transaction_Master)