import unittest
from viewmethods import *

class TestViewMethods(unittest.TestCase):

  def test_getting_accounts(self):

    accountList = get_accounts_for_user(2)
    self.assertEqual(len(accountList), 3)
    self.assertEqual(accountList[0].initials, 'WVC')

if __name__ == '__main__':
    unittest.main()