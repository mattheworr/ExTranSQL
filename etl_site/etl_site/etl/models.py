# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

def sql_attachment_path(instance, filename):
    return 'static/documents/sql/{0}.sql'.format(uuid.uuid4())

# Create your models here.
class User(AbstractUser):
    ip = models.CharField(max_length=39, null=True)
    status = models.CharField(max_length=10, blank=True, null=True)
    occupation = models.CharField(max_length=30, blank=True, null=True)
    industry = models.CharField(max_length=30, blank=True, null=True)
    company = models.CharField(max_length=30, blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    date_registered = models.DateTimeField(blank=True, null=True)

class Table(models.Model):
    user = models.ForeignKey('etl.User', on_delete=models.CASCADE, blank=True, null=True)
    table_name = models.CharField(max_length=144, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    db_server = models.ForeignKey('etl.DBServer', on_delete=models.CASCADE, blank=True, null=True)
    reference_sheet = models.CharField(max_length=144, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    raw_file = models.FileField(upload_to='static/documents/raw/{0}/'.format(uuid.uuid4()))
    export_file = models.FileField(upload_to=sql_attachment_path)

    def update_table_name(self, newname):
        self.table_name = newname
        self.save(update_fields=['table_name'])

    def get_table_name(self):
        return self.table_name

    def get_id(self):
        return self.id

    def get_raw_file(self):
        return self.raw_file

    def get_filename(self):
        return os.path.basename(self.raw_file.name)

    def set_export_file(self, name, query):
        self.export_file.save(name, query)

    def get_export_file(self):
        return '/{0}'.format(self.export_file.name)

class DBServer(models.Model):
    host = models.CharField(max_length=144)
    username = models.CharField(max_length=144)
    password = models.CharField(max_length=144)
    
    class Meta:
        verbose_name = 'DBServer'

    def __unicode__(self):
        return "%s" % self.host