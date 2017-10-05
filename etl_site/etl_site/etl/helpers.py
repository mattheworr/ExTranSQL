import csv 

class sql_table():
	variables = []
	observations = []
	dataframe = None
	table_name = None

	def set_table_name(self, name):
		self.table_name = name

	def get_table_name(self):
		return self.table_name

	def set_variable_type(self, variable, data_type):
		self.variables.append({variable: data_type})

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

	def set_row(self, row):
		self.observations.append(dict(zip(get_variables(), row)))

	def set_all_rows(self, rows):
		for row in self.get_dataframe():
			self.set_row(row)

	def set_dataframe(self, csv_file):
		with open(csv_file) as data:
			has_header = csv.Sniffer().has_header(data.read(1024))
			rows = csv.reader(data)
			if has_header == True:
				next(rows, None)
			self.dataframe = list(rows)

	def get_dataframe(self):
		return self.dataframe

	def get_formatted_variables(self):
		formatted = ''
		for item in self.get_variables_w_types():
			for key, value in item.iteritems():
				pair = ', ' + str(key) + ' ' + str(value)
				formatted += pair
		return formatted

	def get_create_script(self):
		return ('CREATE TABLE ' + 
			self.get_table_name() + ' (id INT' + 
			self.get_formatted_variables() + ');')

	def get_variable_list(self):
		return ('(\"' + 
			'\", \"'.join(self.get_variables()) + '\")')

	def get_value_list(self, row):
		return ('(\"' + 
			'\", \"'.join(row) + '\")')

	def generate_insert_script(self):
		for row in self.get_dataframe():
			yield ('INSERT INTO ' + 
				self.get_table_name() + 
				self.get_variable_list() + ' VALUES ' + 
				self.get_value_list(row) + ';')

	def get_insert_script(self):
		for script in self.generate_insert_script():
			return script

	def export_txt(self):
		with open('111aaa.txt','w') as file:
			file.write(self.get_create_script())
			file.write('\n')
			for script in self.generate_insert_script():
				file.write(script)
				file.write('\n')

'''
["tripduration","starttime","stoptime","start station id","start station name","start station latitude","start station longitude","end station id","end station name","end station latitude","end station longitude","bikeid","usertype","birth year","gender"]
["INT","TIMESTAMP","TIMESTAMP","VARCHAR(5)","VARCHAR(100)","FLOAT","FLOAT","VARCHAR(5)","VARCHAR(100)","FLOAT","FLOAT","VARCHAR(6)","VARCHAR(20)","DATE","BOOLEAN"]
'''

'''
CREATE TABLE table_name (
	id INT,
	variable1 data_type1,
	variable2 data_type2,
	variable3 data_type3
);

INSERT INTO table_name (variable1, variable2, variable3) 
VALUES ('value1', 'value2', 'value3');
'''