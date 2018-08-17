# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals
from django.db import models

# Admin Tables
class Login_Master(models.Model):
    user_name = models.CharField(max_length=500)
    password = models.CharField(max_length=500)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user_name


class Panel_Master(models.Model):
    application_user = models.CharField(max_length=100)
    panel_user_name = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    mobile = models.CharField(max_length=100)

    # Override String Representation
    def __str__(self):
        return self.panel_user_name