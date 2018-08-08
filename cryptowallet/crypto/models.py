# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Account(models.Model):
    username = models.CharField(max_length=250)
    email = models.CharField(max_length=250,unique=False)
    password = models.CharField(max_length=1000000)
    address = models.CharField(max_length=500)

    # Override String Representation
    def __str__(self):
        return self.email + ' ' + self.address


class Transaction(models.Model):
    from_address = models.CharField(max_length=2500)
    to_address = models.CharField(max_length=2500)
    amount = models.CharField(max_length=2500)
    txid = models.CharField(max_length=2500)
    confirmation = models.IntegerField(default=-1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.from_address + ' - ' + self.to_address + ' : ' + self.amount

    def clean(self):
        if self.confirmation > 7:
            raise Exception('Value should be less than 6')