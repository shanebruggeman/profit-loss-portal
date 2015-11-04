import unittest
import parse

testdata_file = "test/example_parse_data.txt"
test_maketake_file = "test/example_maketake.txt"
test_exchange = "Box"
box_add_liquidity = '-0.25'
box_take_liquidity = '0.30'

# check to see that all the db-insert fields are available
transaction_required_values = [
	'TransactTime',
	'PutOrCall',
	'MsgType',
	'UnderlyingSymbol',
	'StrikePrice',
	'Price',
	'OrderQty',
	'Commission',
	'maketake_fee'
]

class TestParser(unittest.TestCase):

	def test_parsed_data_contains_all_necessary_attributes(self):
		parsed_result = parse.parse_transactions(testdata_file, test_maketake_file, test_exchange)

		for trans in parsed_result:
			for field in transaction_required_values:
				assert(field in trans.properties)

	def test_parsed_data_has_correct_maketake_fee(self):
		parsed_result = parse.parse_transactions(testdata_file, test_maketake_file, test_exchange)

		for trans in parsed_result:
			isBuying = trans.properties['PutOrCall'] == 1
			
			if isBuying:
				self.assertEqual(box_add_liquidity, trans.properties['maketake_fee'])
			else:
				self.assertEqual(box_take_liquidity, trans.properties['maketake_fee'])

	def deliberately_fail(self):
		self.assertTrue(False)

if __name__ == '__main__':
    unittest.main()