# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv
import os
import uuid

from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import models
from django.http import JsonResponse

from MySQLdb import connect, escape_string


def sql_attachment_path(instance, filename):
    return 'static/documents/sql/{!s}.sql'.format(uuid.uuid4())

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
    user = models.ForeignKey('etl.User', on_delete=models.CASCADE, blank=True,
        null=True)
    table_name = models.CharField(max_length=144, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    db_server = models.ForeignKey('etl.DBServer', on_delete=models.CASCADE,
        blank=True, null=True)
    reference_sheet = models.CharField(max_length=144, blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True, blank=True, null=True)
    raw_file = models.FileField(
        upload_to='static/documents/raw/{0}/'.format(uuid.uuid4()))
    sql_file = models.FileField(upload_to=sql_attachment_path)

    variables = None
    default_header = None
    shape = None
    dataframe = None
    head = None

    def get_id(self):
        '''Returns ID'''
        return self.id

    def instantiate_table(self):
        self._set_table_name(self._get_filename())
        self._set_dataframe(self._get_raw_file())
        self._set_head()

    def get_json(self):
        '''Returns JSON-formatted data from CSV to template'''
        row_id = 1
        data = []
        for head in self._get_head():
            for col, val in head.iteritems():
                data.append(
                    {'id': row_id, 'name': col, 'text': '<br>'.join(val)})
                row_id += 1
        return {'table_name': self._get_table_name(), 'data': data}

    def get_sql(self, col_list, datatype_list):
        '''Creates SQL query for CSV'''
        self._set_variables_w_type(col_list, datatype_list)
        self._set_sql_file()

    def get_sql_file(self):
        '''Retruns path to generated SQL file'''
        return '/{0}'.format(self.sql_file.name)

    def _set_head(self):
        self.head = [{name: []} for name in self._get_default_header()]
        for row in self._get_dataframe()[:5]:
            for i,col in enumerate(row):
                key = self.head[i].keys()[0]
                self.head[i][key].append(col)

    def _get_head(self):
        return self.head

    def _set_default_header(self):
        self.default_header = ['column_{!s}'.format(col) 
            for col in range(self.get_shape()[1])]

    def _set_custom_header(self, header):
        self.default_header = header

    def _get_default_header(self):
        if not self.default_header:
            self._set_default_header()
        return self.default_header

    def _set_variables_w_type(self, col_list, datatype_list):
        self.variables = [{self._sanitize_column_name(col_list[i]): 
            self._validate_datatype(datatype_list[i])} 
            for i in range(len(col_list))]

    def _get_variables_w_types(self):
        return self.variables

    def _get_variables(self):
        return [pair.keys()[0] for pair in self.variables]

    def _get_types(self):
        return [pair.values()[0] for pair in self.variables]

    def _get_header(self, data):
        return csv.Sniffer().has_header(data)

    def _get_rows(self, data):
        return csv.reader(data)

    def _set_dataframe(self, csv_file):
        csv_file.open()
        data = csv_file
        rows = self._sanitize_rows(list(self._get_rows(data)))
        string = str(''.join(
            ['\"{!s}\"'.format('\",\"'.join(row)) for row in rows[:5]]))
        self._set_shape(rows, rows[0])
        if self._get_header(string) == True:
            self._set_custom_header(rows[0])
            self.dataframe = rows[1:]
        else:
            self.dataframe = rows
        csv_file.close()

    def _set_shape(self, rows, columns):
        self.shape = (len(rows), len(columns))

    def _get_shape(self):
        return self.shape

    def _get_dataframe(self):
        return self.dataframe

    def _get_formatted_pair(self, key, value):
        return ', {!s} {!s}'.format(
            str(key),
            str(value))

    def _get_formatted_variables(self):
        return str(''.join([self._get_formatted_pair(key, value) 
            for item in self._get_variables_w_types() 
            for key, value in item.iteritems()]))

    def _get_create_script(self):
        return 'CREATE TABLE {!s} (id INT{!s});'.format(
            self._get_table_name(),
            self._get_formatted_variables())

    def _get_variable_list(self):
        return '({!s})'.format(
            ', '.join(self._get_variables()))

    def _get_value_list(self, row):
        return '(\"{!s}\")'.format(
            '\", \"'.join(row))

    def _generate_insert_script(self):
        for row in self._get_dataframe():
            yield 'INSERT INTO {!s} {!s} VALUES {!s};'.format(
                self._get_table_name(),
                self._get_variable_list(),
                self._get_value_list(row))

    def _get_insert_script(self):
        for script in self._generate_insert_script():
            return script

    def _set_sql_file(self):
        self.sql_file.save('temp.sql', ContentFile(self._get_sql_string()))

    def _get_sql_string(self):
        sql_string = '{!s}\n'.format(self._get_create_script())
        for script in self._generate_insert_script():
            sql_string += '{!s}\n'.format(script)
        return sql_string

    def _replace_spaces(self, string):
        return string.replace(' ', '_')

    def _truncate_string(self, string, max_length):
        return string[:max_length]

    def _escape_string(self, string):
        return escape_string(string)

    def _sanitize_column_name(self, string):
        return self._escape_string(
            self._replace_spaces(
            self._truncate_string(string, 128)))

    def _sanitize_datatype(self, string):
        return self._escape_string(
            self._replace_spaces(
                string))

    def _sanitize_datapoint(self, string):
        return self._escape_string(string)

    def _sanitize_rows(self, rowlist):
        return [[self._sanitize_datapoint(
            datapoint) for datapoint in row] 
            for row in rowlist]

    def _check_datatype(self, string):
        return string

    def _validate_datatype(self, string):
        return self._check_datatype(self._sanitize_datatype(string))

    def _set_table_name(self, name):
        self.table_name = name.split('.')[0]
        self.save(update_fields=['table_name'])

    def _get_table_name(self):
        return self.table_name

    def _get_raw_file(self):
        return self.raw_file

    def _get_filename(self):
        return os.path.basename(self._get_raw_file().name)

class DBServer(models.Model):
    host = models.CharField(max_length=144)
    username = models.CharField(max_length=144)
    password = models.CharField(max_length=144)
    
    class Meta:
        verbose_name = 'DBServer'

    def __unicode__(self):
        return '{0}'.format(self.host)