import sys
import re
import unittest
import parser
from parser import *

testdata_file = "test_data.txt"
test_maketake_file = "test_maketake.txt"

class TestParser(unittest.TestCase):

	def test_true(self):
		self.assertTrue(True)

	def test_false(self):
		self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()