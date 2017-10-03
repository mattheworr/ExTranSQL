# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ip = models.CharField(max_length=39)
    status = models.CharField(max_length=10, blank=True)
    occupation = models.CharField(max_length=30, blank=True)
    industry = models.CharField(max_length=30, blank=True)
    company = models.CharField(max_length=30, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    date_registered = models.DateTimeField(blank=True, null=True)

class Table(models.Model):
    user = models.ForeignKey('etl.User', on_delete=models.CASCADE)
    table_name = models.CharField(max_length=144)
    date_created = models.DateTimeField(auto_now_add=True)
    db_server = models.ForeignKey('etl.DBServer', on_delete=models.CASCADE)
    reference_sheet = models.CharField(max_length=144)
    last_modified = models.DateTimeField(auto_now=True)

class DBServer(models.Model):
    host = models.CharField(max_length=144)
    username = models.CharField(max_length=144)
    password = models.CharField(max_length=144)
    
    class Meta:
        verbose_name = 'DBServer'

    def __unicode__(self):
        return "%s" % self.host