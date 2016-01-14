import sys
sys.path.append("../")
sys.path.append("/Users/shanebruggeman/Documents/CodingProjects/profit-loss-portal/")
from models import *

print 'USERS'
users = User.query.all()
for user in users:
    print user
print '\n---------------\n'

print 'ACCOUNTS'
accounts = Account.query.all()
for account in accounts:
    print account
print '\n---------------\n'

print 'TRANSACTIONS'
transactions = Transaction.query.all()
for transaction in transactions:
    print transaction
print '\n---------------\n'

print 'EXCHANGES'
exchanges = Exchange.query.all()
for exchange in exchanges:
    print exchange
print '\n---------------\n'

print 'STOCKPOSITIONS'
positions = StockPosition.query.all()
for pos in positions:
	print pos
	trans = pos.all_transactions
	for tran in trans:
		print '\t' + str(tran)