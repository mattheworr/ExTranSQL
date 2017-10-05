import csv 

class sql():
	variables = []
	obervations = []

	def add_variable(self, variable, data_type):
		self.variables.append({variable: data_type})

	def get_names_only(self):
		return list(self.variables.keys())

	def add_row(self, row):
		self.observations.append(dict(zip(get_names_only(), row)))

	def add_rows(self, rows)
		for row in self.add_raw_data(csv_file):
			self.add_row(row)

	def add_raw_data(self, csv_file):
		with open(csv_file) as data:
			has_header = csv.Sniffer().has_header(data.read(1024))
			rows = csv.reader(data)
			if has_header == True:
				next(rows, None)
			return list(rows)

	def script(self):
		pass

