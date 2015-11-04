import unittest
import parse

testdata_file = "test/example_parse_data.txt"
test_maketake_file = "test/example_maketake.txt"

transaction_required_values = [
	'TransactTime',
	'PutOrCall',
	'settle',
	'entry',
	'trade',
	'ticket_number',
	'buy_sell',
	'commission'
]

class TestParser(unittest.TestCase):

	def test_parsed_data_contains_all_necessary_attributes(self):
		parsed_result = parse.parse_transactions(testdata_file, test_maketake_file, "Bat")

	def test_make_take_levels_are_appropriately_nested(self):
		pass

if __name__ == '__main__':
    unittest.main()