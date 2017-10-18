import csv
from MySQLdb import connect, escape_string
from django.http import JsonResponse
from .models import Table as table_model
from django.core.files.base import ContentFile
import codecs
import os

class sql_table():
	variables = []
	observations = []
	default_header = []
	shape = (0,0)
	dataframe = None
	table_name = None
	connected = False
	ref_id = None
	model_object = None
	head = []

	def __init__(self, model_object):
		self.model_object = model_object
		self.set_ref_id(self.model_object.get_id())
		self.set_table_name(self.model_object.get_filename())
		self.set_dataframe(self.model_object.get_raw_file())
		self.set_head()

	def get_json(self):
		row_id = 1
		data = []
		for head in self.get_head():
			for col, val in head.iteritems():
				data.append(
					{'id': row_id, 'name': col, 'text': '<br>'.join(val)})
				row_id += 1
		return {'table_name': self.get_table_name(), 'data': data}

	def get_sql(self, table_name, col_list, datatype_list):
		self.set_table_name(table_name)
		self.get_model_object().update_table_name(self.get_table_name())
		for i,e in enumerate(col_list):
			self.set_variable_type(col_list[i], datatype_list[i])
		self.export_txt()

	def set_head(self):
		for name in self.get_default_header():
			self.head.append({name: []})
		print self.head
		for row in self.get_dataframe()[:5]:
			for i,col in enumerate(row):
				key = self.head[i].keys()[0]
				self.head[i][key].append(col)

	def get_head(self):
		return self.head	

	def set_ref_id(self, id_num):
		#self.validate_ref_id()
		self.ref_id = id_num
	'''
	def validate_ref_id(self):
		if self.get_ref_id != None:
			raise Exception('ID already exists')
	'''
	def get_ref_id(self):
		return self.ref_id

	def set_table_name(self, name):
		self.table_name = name.split('.')[0]

	def get_table_name(self):
		return self.table_name

	def set_default_header(self):
		for col in range(self.get_shape()[1]):
			self.default_header.append('column_{0}'.format(col))

	def set_custom_header(self, header):
		self.default_header = header

	def get_default_header(self):
		if not self.default_header:
			self.set_default_header()
		return self.default_header

	def set_variable_type(self, variable, data_type):
		self.variables.append(
			{self.clean_column_name(variable): self.clean_datatype(data_type)})

	def get_variables_w_types(self):
		return self.variables

	def get_variables(self):
	    names = []
	    for pair in self.variables:
	        names.append(pair.keys()[0])
	    return names

	def get_types(self):
	    values = []
	    for pair in self.variables:
	        values.append(pair.values()[0])
	    return values

	def set_dict(self, keys, values):
		return dict(zip(keys, values))

	def set_row(self, row):
		self.observations.append(
			self.set_dict(
				self.get_variables(), row))

	def set_all_rows(self, rows):
		for row in self.get_dataframe():
			self.set_row(row)

	def get_header(self, data):
		return csv.Sniffer().has_header(data)

	def get_rows(self, data):
		return csv.reader(data)

	def set_dataframe(self, csv_file):
		csv_file.open()
		data = csv_file
		rows = list(self.get_rows(data))
		string = ''
		for row in rows[:5]:
			string += '\"{0}\"'.format('\",\"'.join(row))
		self.set_shape(rows, rows[0])
		if self.get_header(string) == True:
			self.set_custom_header(rows[0])
			self.dataframe = rows[1:]
		else:
			self.dataframe = rows
		csv_file.close()

	def set_shape(self, rows, columns):
		self.shape = (len(rows), len(columns))

	def get_shape(self):
		return self.shape

	def get_dataframe(self):
		return self.dataframe

	def get_formatted_pair(self, key, value):
		return ', {0} {1}'.format(
			str(key),
			str(value))

	def get_formatted_variables(self):
		formatted = ''
		for item in self.get_variables_w_types():
			for key, value in item.iteritems():
				formatted += self.get_formatted_pair(key, value)
		return formatted

	def get_create_script(self):
		return 'CREATE TABLE {0} (id INT{1});'.format(
			self.get_table_name(),
			self.get_formatted_variables())

	def get_variable_list(self):
		return '({0})'.format(
			', '.join(self.get_variables()))

	def get_value_list(self, row):
		return '(\"{0}\")'.format(
			'\", \"'.join(row))

	def generate_insert_script(self):
		for row in self.get_dataframe():
			yield 'INSERT INTO {0} {1} VALUES {2};'.format(
				self.get_table_name(),
				self.get_variable_list(),
				self.get_value_list(row))

	def get_insert_script(self):
		for script in self.generate_insert_script():
			return script

	def get_model_object(self):
		if self.model_object is None:
			self.model_object = table_model.objects.get(self.get_ref_id())
		return self.model_object

	def export_txt(self):
		file_string = '{0}\n'.format(self.get_create_script())
		for script in self.generate_insert_script():
			file_string += '{0}\n'.format(script)
		model = self.get_model_object()
		model.set_export_file('temp.sql', ContentFile(file_string))
		model.save()

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

	def replace_spaces(self, string):
		return string.replace(' ', '_')

	def truncate_string(self, string, max_length):
		return string[:max_length]

	def escape_string(self, string):
		return escape_string(string)

	def clean_column_name(self, string):
		return self.escape_string(
			self.replace_spaces(
			self.truncate_string(string, 128)))

	def clean_datatype(self, string):
		return string

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

	def export_sql_string(self):
		file_string = '{0}\n'.format(self.get_create_script())
		for script in self.generate_insert_script():
			file_string += '{0}\n'.format(script)
		return file_string

'''
["tripduration","starttime","stoptime","start station id","start station name","start station latitude","start station longitude","end station id","end station name","end station latitude","end station longitude","bikeid","usertype","birth year","gender"]
["INT","TIMESTAMP","TIMESTAMP","VARCHAR(5)","VARCHAR(100)","FLOAT","FLOAT","VARCHAR(5)","VARCHAR(100)","FLOAT","FLOAT","VARCHAR(6)","VARCHAR(20)","DATE","BOOLEAN"]
'''

'''
CREATE TABLE table_name (
	id INT,
	variable0 data_type0,
	variable1 data_type1,
	variable2 data_type2
);

INSERT INTO table_name (variable0, variable1, variable2) 
VALUES ('value0', 'value1', 'value2');
'''