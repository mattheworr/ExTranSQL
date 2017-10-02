# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    ip = models.CharField(max_length=39)
    status = models.CharField(max_length=10)
    occupation = models.CharField(max_length=50)
    industry = models.CharField(max_length=50)
    company = models.CharField(max_length=50)
    date_registered = models.DateTimeField()

class Table(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    table_name = models.CharField(max_length=144)
    date_created = models.DateTimeField(auto_now_add=True)
    db_server = models.CharField(max_length=144)
    reference_sheet = models.CharField(max_length=144)
    last_modefied = models.DateTimeField(auto_now=True)
