import csv
import os

from MySQLdb import connect, escape_string

from django.http import JsonResponse
from django.core.files.base import ContentFile

from .models import Table as table_model

class sql_table():
	variables = []
	observations = []
	default_header = []
	shape = (0, 0)
	dataframe = None
	table_name = None
	connected = False
	ref_id = None
	model_object = None
	head = []

	def __init__(self, model_object):
		self.model_object = model_object
		self._set_ref_id(self.model_object.get_id())
		self._set_table_name(self.model_object.get_filename())
		self._set_dataframe(self.model_object.get_raw_file())
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

	def get_sql(self, table_name, col_list, datatype_list):
		'''Creates SQL query for CSV'''
		self._set_table_name(table_name)
		self._get_model_object().set_table_name(self._get_table_name())
		for i,e in enumerate(col_list):
			self._set_variable_type(col_list[i], datatype_list[i])
		self._set_sql_file()

	def _set_head(self):
		for name in self._get_default_header():
			self.head.append({name: []})
		print self.head
		for row in self._get_dataframe()[:5]:
			for i,col in enumerate(row):
				key = self.head[i].keys()[0]
				self.head[i][key].append(col)

	def _get_head(self):
		return self.head

	def _set_ref_id(self, id_num):
		# self.validate_ref_id()
		self.ref_id = id_num

	'''
	def validate_ref_id(self):
		if self.get_ref_id != None:
			raise Exception('ID already exists')
	'''

	def _get_ref_id(self):
		return self.ref_id

	def _set_table_name(self, name):
		self.table_name = name.split('.')[0]

	def _get_table_name(self):
		return self.table_name

	def _set_default_header(self):
		for col in range(self.get_shape()[1]):
			self.default_header.append('column_{0}'.format(col))

	def _set_custom_header(self, header):
		self.default_header = header

	def _get_default_header(self):
		if not self.default_header:
			self._set_default_header()
		return self.default_header

	def _set_variable_type(self, variable, data_type):
		self.variables.append(
			{self._clean_column_name(
                variable): self._clean_datatype(data_type)})

	def _get_variables_w_types(self):
		return self.variables

	def _get_variables(self):
		names = []
		for pair in self.variables:
			names.append(pair.keys()[0])
		return names

	def _get_types(self):
		values = []
		for pair in self.variables:
			values.append(pair.values()[0])
		return values

	'''	
	def set_dict(self, keys, values):
		return dict(zip(keys, values))

	def set_row(self, row):
		self.observations.append(
			self.set_dict(
				self.get_variables(), row))

	def set_all_rows(self, rows):
		for row in self.get_dataframe():
			self.set_row(row)
	'''

	def _get_header(self, data):
		return csv.Sniffer().has_header(data)

	def _get_rows(self, data):
		return csv.reader(data)

	def _set_dataframe(self, csv_file):
		csv_file.open()
		data = csv_file
		rows = list(self._get_rows(data))
		string = ''
		for row in rows[:5]:
			string += '\"{0}\"'.format('\",\"'.join(row))
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
		return ', {0} {1}'.format(
			str(key),
			str(value))

	def _get_formatted_variables(self):
		formatted = ''
		for item in self._get_variables_w_types():
			for key, value in item.iteritems():
				formatted += self._get_formatted_pair(key, value)
		return formatted

	def _get_create_script(self):
		return 'CREATE TABLE {0} (id INT{1});'.format(
			self._get_table_name(),
			self._get_formatted_variables())

	def _get_variable_list(self):
		return '({0})'.format(
			', '.join(self._get_variables()))

	def _get_value_list(self, row):
		return '(\"{0}\")'.format(
			'\", \"'.join(row))

	def _generate_insert_script(self):
		for row in self._get_dataframe():
			yield 'INSERT INTO {0} {1} VALUES {2};'.format(
				self._get_table_name(),
				self._get_variable_list(),
				self._get_value_list(row))

	def _get_insert_script(self):
		for script in self._generate_insert_script():
			return script

	def _get_model_object(self):
		if self.model_object is None:
			self.model_object = table_model.objects.get(self._get_ref_id())
		return self.model_object

	def _set_sql_file(self):
		model = self._get_model_object()
		model.set_sql_file('temp.sql', ContentFile(self._get_sql_string()))
		model.save()

	def _get_sql_string(self):
		sql_string = '{0}\n'.format(self._get_create_script())
		for script in self._generate_insert_script():
			sql_string += '{0}\n'.format(script)
		return sql_string

	'''
	def connect_to_db(self):
		db = connect(
			host='dev.matthewjorr.com',
			port=3306,
			user='root',
			#passwd=ENTER_PASSWORD,
			db='testing')
		cursor = db.cursor()

	def set_connection(self, BOOLEAN):
		if self.get_connection() == False:
			self.connect_to_db()
			self.connected = True
		else:
			return 'Already connected to database.'

	def get_connection(self):
		return self.connected

	def post_to_db(self, script):
		if self.get_connection() == False:
			self.connect_to_db()
		cursor.execute(script)

	def create_new_table(self):
		self.post_to_db(self.get_create_script())
		for script in self.generate_insert_script():
			self.post_to_db(script)
	'''

	def _replace_spaces(self, string):
		return string.replace(' ', '_')

	def _truncate_string(self, string, max_length):
		return string[:max_length]

	def _escape_string(self, string):
		return escape_string(string)

	def _clean_column_name(self, string):
		return self._escape_string(
			self._replace_spaces(
			self._truncate_string(string, 128)))

	def _clean_datatype(self, string):
		# Coming soon
		return string

	'''
	def clean_data(self, string, datatype, dtparams):
		pass

	def validate_column_name(self, string):
		pass

	def validate_datatype(self, string):
		pass

	def get_query(self, string):
		pass

	def validate_query(self, string):
		pass

	def get_response(self, string):
		pass

	def translate_table_name(self, string):
		pass
		#self.get_ref_id()
	'''