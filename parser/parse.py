# regular expressions
import re
import sys
from reference.fix_tables import fix_fields_table, fix_msg_types_table, sidevalues_table

class OptionRowHolder(object):
	def __init__(self):
		self.all_tabs = []
		top_props = ['top', '  ', 'top', '   ', '(top add fee)', '  ', '(top take fee)', '', 'top']
		top_tab = StockRow(top_props)
		self.all_tabs.append(top_tab)

	def __str__(self):
		return str(self.all_tabs)

	def __repr__(self):
		return str(self)

	def size(self):
		return len(self.all_tabs)

	def get_first(self):
		return self.all_tabs[0]

	def lookup(self, exchange, isAddingLiquidity):
		for tab in self.all_tabs:
			if tab.properties["name"] == exchange:
				fee = "add_fee" if isAddingLiquidity else "take_fee"
				
				return tab.properties[fee]

		return False

	def add(self, stock_row):
		last_added_tab = self.all_tabs[len(self.all_tabs) - 1]
		last_added_tabval = last_added_tab.get_tabval()

		next_added_tabval = stock_row.get_tabval()
		parent_tab = {}

		# if the last added tab was nested deeper than the incoming one
		indent_in = next_added_tabval > last_added_tabval

		# if the last added tab was nested less deeply than the incoming one
		indent_back = next_added_tabval < last_added_tabval
		
		# if the last added tab was nested equally as deep as the incoming one
		indent_same = next_added_tabval == last_added_tabval

		# a deeper nesting indicates the last added tab was the parent
		if indent_in:
			parent_tab = last_added_tab

		# less deep or equal nesting implies an earlier parent than the last added
		if indent_back or indent_same:

			# start at the back and move towards the front until the list's tab item is less deeply nested
			i = len(self.all_tabs) - 1
			parent_tab = self.all_tabs[i]
			parent_tab_val = parent_tab.get_tabval()

			# continue until we hit a less tabbed entry.
			# (the zero'eth entry is guaranteed to be less than)
			while i >= 0 and parent_tab_val >= next_added_tabval:
				parent_tab = self.all_tabs[i]
				parent_tab_val = parent_tab.get_tabval()
				i = i - 1

		# retrieve the added tab's name and add them to the parent
		stock_name = stock_row.properties["name"]

		# adding the entry to the parent
		parent_tab.children[stock_name] = stock_row

		# always add the added tab to the list of tabs
		self.all_tabs.append(stock_row)

		# always return the overall built object
		return self.all_tabs[0]

class StockRow(object):
	def __init__(self, line_parts):
		self.line_parts = line_parts
		self.parent = None
		self.properties = {}
		self.children = {}
		self.parse(line_parts)

	def get_tabval(self):
		return self.properties["tabval"]

	def parse(self, line_parts):
		make_take = 0
		option_name = 2
		add_liquidity_fee = 4
		take_liquidity_fee = 6
		tabbed_space = 7
		attributes_pos = 8

		tabbing = line_parts[tabbed_space]
		tabval = len(tabbing) / 4

		maketake = line_parts[make_take]
		op_name = line_parts[option_name]
		add_fee = line_parts[add_liquidity_fee]
		take_fee = line_parts[take_liquidity_fee]

		properties = {
			"name": op_name,
			"maketake": maketake,
			"add_fee": add_fee,
			"take_fee": take_fee,
			"tabval": tabval
		}

		self.properties = properties

	def set_parent(self, parent):
		self.parent = parent

	def __str__(self):
		return str(self.properties)

	def __repr__(self):
		return str(self)


class MakeTakeParser(object):

	def __init__(self):
		pass

	def __str__(self):
		return str(self.properties)

	def __repr__(self):
		return str(self)

	def parse_maketake(self, file):
		base_string = file.read()
		lines = base_string.split('\n')

		properties = {}
		count = 0

		word_map = []

		for line in lines:
			if '#' in line or not line.strip():
				continue

			words = []
			build_word = ''
			index = 0

			for char in line:
				if len(build_word):
					if index == len(line) - 1:
						words.append(build_word + char)

					if build_word[0] == ' ' and char != ' ':
						words.append(build_word)
						build_word = char
						index = index + 1
						continue

					if build_word[0] != ' ' and char == ' ':
						words.append(build_word)
						build_word = char
						index = index + 1
						continue
					
				index = index + 1
				build_word = build_word + char

			word_map.append(words)

		holder = OptionRowHolder()

		for line in word_map:
			tab = StockRow(line)
			holder.add(tab)

		return holder

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
			if entry == ' ' or entry == '':
				continue

			split_pair = entry.split('=')
			
			if len(split_pair) != 2:
				continue

			try:
				key = split_pair[0]
				value = split_pair[1]
				pair_dict[key] = value
			except Exception as e:
				print 'could not add key value pair to transaction data'
				print e

		for key in pair_dict:

			if key in fix_fields_table:
				key_label = fix_fields_table[key]
				value = pair_dict[key]
				self.properties[key_label] = value

		# look up the message type and set it on the transaction
		msg_type_val = self.properties['MsgType']
		self.transaction_type = fix_msg_types_table[msg_type_val]
		# self.properties['MsgType'] = fix_msg_types_table[msg_type_val]

	def ternary_dict_select(self, pair_dict, item_number):
		return pair_dict[item_number] if item_number in pair_dict else None

	def get(self, key):
		return str(self.properties[key])


def parse_maketake(data_file):
	data = open(data_file, 'r')
	parser = MakeTakeParser()
	return parser.parse_maketake(data)

def parse_transactions(transaction_file, maketake_file, exchange):
	transaction_data = open(transaction_file, 'r').read()
	transaction_lines = transaction_data.split('\n')
	maketake = parse_maketake(maketake_file)

	results = []
	for line in transaction_lines:
		if '#' in line or not line.strip() or ('SetStatus' in line):
			continue

		next_transaction = Transaction(line)
		results.append(next_transaction)

	# maketake_data = open(maketake_file, 'r').read()

	allowed_transactions = ['D']
	transactions_found = [item for item in results if item.properties['MsgType'] in allowed_transactions]

	for t in transactions_found:
		tside = t.properties['Side']
		isAddingLiquidity = tside == 2
		t.properties['maketake_fee'] = maketake.lookup(exchange, isAddingLiquidity)

	return transactions_found

def main(fName):
	arg_filename = sys.argv[1]

	all_transactions = parse_transactions(arg_filename, 'maketake_rules.txt', "Box")
	
	for line in all_transactions:
		# pass
		print line
		print '\n'

	# tab_holder = parse_maketake('maketake_rules.txt')
	# print tab_holder.lookup('IseProEtfSpecials', True)

if __name__ == '__main__':
	main(sys.argv[1])
