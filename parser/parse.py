# regular expressions
import re
import sys
from fixfields import fix_fields_table
from fixmsgtypes import fix_msg_types_table

class Transaction(object):

	def __init__(self, base_string):
		self.base_string = base_string
		self.properties = {}

		self.parse_fix_pairs()
		self.properties['Commission'] = '-1.00'

	def __str__(self):
		return str(self.properties)

	def __repr__(self):
		return self.__str__()

	def parse_fix_pairs(self):
		parsed_string = self.base_string
		
		pairs_start = parsed_string.find('8=FIX')
		pairs_string = parsed_string[pairs_start:]
		pairs = pairs_string.split('')

		pair_dict = {}
		for entry in pairs:
			if entry == ' ':
				continue
			split_pair = entry.split('=')
			key = split_pair[0]
			value = split_pair[1]
			pair_dict[key] = value

		for key in pair_dict:
			key_label = fix_fields_table[key]
			value = pair_dict[key]
			self.properties[key_label] = value

		# look up the message type and set it on the transaction
		msg_type_val = self.properties['MsgType']
		self.transaction_type = fix_msg_types_table[msg_type_val]

	def ternary_dict_select(self, pair_dict, item_number):
		return pair_dict[item_number] if item_number in pair_dict else None

# check out what the setstatus is doing
def parse_file(data_file):
	data = open(data_file, 'r').read()
	data_lines = data.split('\n')

	results = []
	for line in data_lines:
		if '#' in line or not line.strip() or ('SetStatus' in line):
			continue

		my_transaction = Transaction(line)
		results.append(my_transaction)

	return results

def main(fName):
	parsed_result = parse_file(fName)
	return parsed_result
	for result in parsed_result:
		# print len(result.properties)
		if len(result.properties) == 1:
			# print result.properties
			# print result.base_string
			continue
		print result

if __name__ == '__main__':
	main(sys.argv[1])
