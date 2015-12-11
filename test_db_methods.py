from app import db
from models import *
import db_methods as dm
import datetime
import unittest

class TestDatabaseMethods(unittest.TestCase):
    def test_user(self):
        #Add, make sure the user is added
        test_user=User('TESTINGADD@test.com', 'PW', 'TESTDUDE', False)
        dm.insert(test_user)
        query=User.query.order_by(User.user_id.desc()).first()
        self.assertEqual(str(test_user), str(query))
        #if str(test_user) != str(query):
           # return False

        #delete, undo the add, and make sure successful
        dm.delete_user_by_id(test_user.user_id)
        query=User.query.filter_by(user_id=test_user.user_id).first()
        self.assertIsNone(query)
        #if query != None:
        #    return False
        #return True

    def test_account(self):
        #Add, make sure the Account is added
        test_acc=Account('TESTINGADDACCOUNT', 'TST', 99999.99)
        dm.insert(test_acc)
        query=Account.query.order_by(Account.account_id.desc()).first()
        self.assertEqual(str(test_acc), str(query))
        #if str(test_acc) != str(query):
            #return False

        #delete, undo the add, and make sure successful
        dm.delete_account_by_id(test_acc.account_id)
        query=Account.query.filter_by(account_id=test_acc.account_id).first()
        self.assertIsNone(query)
        #if query != None:
            #return False
        #return True

    def test_exchange(self):
        #Add, make sure the Exchange is added
        test_ex=Exchange('TEST')
        dm.insert(test_ex)
        query=Exchange.query.order_by(Exchange.exchange_id.desc()).first()
        self.assertEqual(str(test_ex), str(query))
        #if str(test_ex) != str(query):
            #return False

        #delete, undo the add, and make sure successful
        dm.delete_exchange_by_id(test_ex.exchange_id)
        query=Exchange.query.filter_by(exchange_id=test_ex.exchange_id).first()
        self.assertIsNone(query)
        #if query != None:
            #return False
        #return True

    def test_transaction(self):
        #Add, make sure the Tranaction is added
        acc=Account.query.first()
        ex=Exchange.query.first()
        date=datetime.datetime.now()
        test_trans=Transaction(acc.account_id, ex.exchange_id, 4.00, 400, 'TEST', date, date, date, 'TEST', 'TEST', -1.00, False)
        dm.insert(test_trans)
        query=Transaction.query.order_by(Transaction.transaction_id.desc()).first()
        self.assertEqual(str(test_trans), str(query))
        #if str(test_trans) != str(query):
            #return False

        #delete, undo the add, and make sure successful
        dm.delete_transaction_by_id(test_trans.transaction_id)
        query=Transaction.query.filter_by(transaction_id=test_trans.transaction_id).first()
        self.assertIsNone(query)
        #if query != None:
            #return False
        #return True

if __name__ == '__main__':
	unittest.main()
