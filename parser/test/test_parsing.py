import unittest
import sys
sys.path.append('../')
import parse


class TestDataParsing(unittest.TestCase):

	def test_single_order_transactions(self):
		testdata_file = open("example_parse_data.txt", "r").read()
		test_maketake_file = open("example_maketake.txt", "r").read()
		test_exchange = "Ase"

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

		# side = 1
		answer1 = {
			'TransactTime': '20151006-02:53:33.971',
			'PutOrCall': '1',
			'MsgType': 'D',
			'UnderlyingSymbol': 'BAC',
			'StrikePrice': '25.00',
			'Price': '2.00',
			'OrderQty': '50',
			'Commission': '-1.00',
			'maketake_fee': '2.00'
		}

		# side = 2
		answer2 = {
			'TransactTime': '20151006-02:54:19.924',
			'PutOrCall': '1',
			'MsgType': 'D',
			'UnderlyingSymbol': 'BAC',
			'StrikePrice': '25.00',
			'Price': '2.05',
			'OrderQty': '50',
			'Commission': '-1.00',
			'maketake_fee': '1.00'
		}

		# side = 2
		answer3 = {
			'TransactTime': '20151006-02:54:34.389',
			'PutOrCall': '1',
			'MsgType': 'D',
			'UnderlyingSymbol': 'BAC',
			'StrikePrice': '25.00',
			'Price': '2.05',
			'OrderQty': '50',
			'Commission': '-1.00',
			'maketake_fee': '1.00'
		}

		# side = 1
		answer4 = {
			'TransactTime': '20151006-02:54:48.801',
			'PutOrCall': '1',
			'MsgType': 'D',
			'UnderlyingSymbol': 'BAC',
			'StrikePrice': '25.00',
			'Price': '2.00',
			'OrderQty': '50',
			'Commission': '-1.00',
			'maketake_fee': '2.00'
		}


		# side = 2
		answer5 = {
			'TransactTime': '20151006-02:55:16.129',
			'PutOrCall': '1',
			'MsgType': 'D',
			'UnderlyingSymbol': 'BAC',
			'StrikePrice': '25.00',
			'Price': '2.05',
			'OrderQty': '50',
			'Commission': '-1.00',
			'maketake_fee': '1.00'
		}

		# side = 1
		answer6 = {
			'TransactTime': '20151006-02:55:27.730',
			'PutOrCall': '1',
			'MsgType': 'D',
			'UnderlyingSymbol': 'BAC',
			'StrikePrice': '25.00',
			'Price': '2.00',
			'OrderQty': '50',
			'Commission': '-1.00',
			'maketake_fee': '2.00'
		}

		# side = 2
		answer7 = {
			'TransactTime': '20151006-02:55:36.577',
			'PutOrCall': '1',
			'MsgType': 'D',
			'UnderlyingSymbol': 'BAC',
			'StrikePrice': '25.00',
			'Price': '2.05',
			'OrderQty': '50',
			'Commission': '-1.00',
			'maketake_fee': '1.00'
		}

		answers = [answer1, answer2, answer3, answer4, answer5, answer6, answer7]
		parsed_result = parse.parse_transactions(testdata_file, test_maketake_file, test_exchange)

		# check to see all fields are in the answer
		for valid_transaction in parsed_result:
			for field in transaction_required_values:
				self.assertTrue(field in valid_transaction.properties)

		# check to see that all parsed values match the test cases
		for test_number in range(0, len(answers)):
			parsed_transaction = parsed_result[test_number]
			test_case_correct_answer = answers[test_number]

			for field in test_case_correct_answer:
				self.assertTrue(parsed_transaction.properties[field] == test_case_correct_answer[field])


	def test_maketake_fee_lookup(self):
		test_maketake_file = open("example_maketake.txt", "r").read()

		# exchange name
		# adding liquidity (left)
		# taking liquidity (right)
		maketake_tests = {
			'Stock':                ['0.00', '0.00'],
			'NonStock':             ['9.99', '9.99'],
			'Ase':                  ['1.00', '2.00'],
			'AseCust':              ['0.00', '0.00'],
			'AsePro':               ['0.20', '0.20'],
			'Bat':                  ['-0.25', '0.30'],
			'Box':                  ['-0.25', '0.30'],
			'BoxNickel':            ['0.65', '0.45'],
			'CboCust':              ['0.00', '0.00'],
			'CboPro':               ['0.20', '0.20'],
			'IseCust':              ['0.00', '0.00'],
			'IseCustEtfSpecials':   ['0.00', '0.12'],
			'IseCustEtfSingle':     ['0.18', '0.18'],
			'IseCustIndex':         ['0.00', '0.00'],
			'IseCustIndexSingle':   ['0.18', '0.18'],
			'IsePro':               ['0.10', '0.28'],
			'IseProEtfQs':          ['0.10', '0.25'],
			'IseProEtfSpecials':    ['0.10', '0.00'],
			'IseProEtfSingle':      ['0.20', '0.18'],
			'IseProIdxOpt':         ['0.20', '0.20'],
			'IseProIdxOptSingle':   ['0.18', '0.18'],
			'NdqCust':              ['-0.36', '0.45'],
			'NdqCustEqOptNickel':   ['-0.20', '0.45'],
			'NdqCustEtfSpecials':   ['-0.20', '0.25'],
			'NdqCustIdxOpt':        ['-0.10', '0.50'],
			'NdqPro':               ['-0.36', '0.45'],
			'NdqProEqOptNickel':    ['-0.20', '0.45'],
			'NdqProEtfSpecials':    ['-0.36', '0.45'],
			'NdqProIdxOpt':         ['-0.10', '0.50'],
			'Nys':                  ['-0.25', '0.45'],
			'PhsCust':              ['0.00', '0.00'],
			'PhsCustEtfSpecials':   ['-0.20', '0.25'],
			'PhsCustIdxOpt':        ['0.35', '0.35'],
			'PhsPro':               ['0.20', '0.40'],
			'PhsProEtfSpecials':    ['-0.20', '0.40'],
			'PhsProIdxOpt':         ['0.20', '0.20']
		}

		tested_parser = parse.parse_maketake(test_maketake_file)

		# test each exchange in the test set
		for exchange in maketake_tests:
			add_fee = True
			take_fee = False

			# lookup the add and take fees in the test parser
			parsed_answer_add = tested_parser.lookup(exchange, add_fee)
			parsed_answer_take = tested_parser.lookup(exchange, take_fee)

			# lookup the add and take fees in the answers
			correct_answer_add = maketake_tests[exchange][0]
			correct_answer_take = maketake_tests[exchange][1]

			# verify the solution matches the answer for each exchange
			self.assertEqual(parsed_answer_add, correct_answer_add)
			self.assertEqual(parsed_answer_take, correct_answer_take)

if __name__ == '__main__':
    unittest.main()
