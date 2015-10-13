# regular expressions
import re

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

		self.properties['Price'] = self.ternary_dict_select(pair_dict, '44')
		self.properties['Side'] = self.ternary_dict_select(pair_dict, '54')
		self.properties['Symbol'] = self.ternary_dict_select(pair_dict, '55')
		self.properties['OrderQty'] = self.ternary_dict_select(pair_dict, '38')
		self.properties['TransactTime'] = self.ternary_dict_select(pair_dict, '60')

	def ternary_dict_select(self, pair_dict, item_number):
		return pair_dict[item_number] if item_number in pair_dict else None

transaction_fields = {}

fixtable = {
	8   : "BeginString",
	9   : "BodyLength",
	10  : "CheckSum",
	11  : "ClOrdID",
	34  : "MsgSeqNum",
	35  : "MsgType",
	38  : "OrderQty",
	44  : "Price",
	49  : "SenderCompID",
	52  : "SendingTime",
	54  : "Side", # 1 = buy, 2 = sell, 5 = sell short
	56  : "TargetCompID",
	59  : "TimeInForce",
	60  : "TransactTime",
	77  : "OpenClose",
	98  : "EncryptMethod",
	108 : "HeartBtInt",
	115 : "OnBehalfOfCompID",
	167 : "SecurityType",
	200 : "MaturityMonthYear",
	201 : "PutOrCall",
	202 : "StrikePrice",
	205 : "MaturityDay",
	311 : "UnderlyingSymbol"
}


def parse_file():
	data = open('testdata1.txt', 'r').read()
	data_lines = data.split('\n')

	results = []
	for line in data_lines:
		if '#' in line or not line.strip():
			continue

		print line
		my_transaction = Transaction(line)
		results.append(my_transaction)

	return results

print parse_file()

if __name__ == '__main__':
	pass