from flask import Flask, jsonify, session, g
from flask.ext.sqlalchemy import SQLAlchemy
# from datetime import datetime, date, timedelta
from db_create import db, application
from models import *
import unittest
from viewmethods import *

TEST_USER_ID = 2

class TestViewMethods(unittest.TestCase):

	
	def test_getting_accounts(self):
		test_user = db.session.query(User).filter(User.user_id == TEST_USER_ID).first()
		accounts = db.session.query(Account).limit(2).all()
		test_user.accounts = accounts
		db.session.commit()

		accountList = get_accounts_for_user(TEST_USER_ID)
		self.assertEqual(len(accountList), 2)

		test_user.accounts = []
		db.session.commit()

	def test_making_admins(self):

		self.assertFalse(db.session.query(User).filter(User.user_id == TEST_USER_ID).first().admin)

		adminList = [TEST_USER_ID]
		make_admin(adminList)

		self.assertTrue(db.session.query(User).filter(User.user_id == TEST_USER_ID).first().admin)

		db.session.query(User).filter(User.user_id == TEST_USER_ID).update({User.admin: False})
		db.session.commit()

	def test_associate_accounts(self):
		test_user = db.session.query(User).filter(User.user_id == TEST_USER_ID).first()
		self.assertEqual(len(test_user.accounts), 0)

		accountList = [1,2]
		associate_accounts_to_user(TEST_USER_ID, accountList)
		
		self.assertEqual(len(test_user.accounts), 2)
		
		test_user.accounts = []
		db.session.commit()

	def test_get_transaction_for_chart(self):

		values_and_labels = get_transactions_for_chart(1, 'ashr')
		self.assertTrue(len(values_and_labels['values']) > 0)
		self.assertEqual(len(values_and_labels['values']), len(values_and_labels['labels']))


if __name__ == '__main__':
	unittest.main()