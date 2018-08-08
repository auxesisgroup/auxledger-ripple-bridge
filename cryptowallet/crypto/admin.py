# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Account, Transaction
from django.contrib import admin

# Register your models here.
admin.site.register(Account)
admin.site.register(Transaction)
