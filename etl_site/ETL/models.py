# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class User(models.Model):
	email = models.CharField()
	ip = models.CharField()
	signup_date = models.DateTimeField(auto_now_add=True)
	status = models.CharField()
	first_name = models.CharField()
	last_name = models.CharField()
	password = models.CharField()
	occupation = models.CharField()
	industry = models.CharField()
	company = models.CharField()
	registration_date = models.DateTimeField()
	last_login = models.DateTimeField()

class Table(models.Model):
	id_user = models.IntegerField()
	table_name = models.CharField()
	date_created = models.DateTimeField(auto_now_add=True)
	db_server = models.CharField()
	reference_sheet = models.CharField()
	last_modefied = models.DateTimeField(auto_now=True)
