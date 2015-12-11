import sys
sys.path.append("../")
sys.path.append("/Users/shanebruggeman/Documents/CodingProjects/profit-loss-portal/")
from models import *

print 'USER'
print User.query.all()
print 'ACCOUNT'
print Account.query.all()
print 'TRANSACTION'
print Transaction.query.all()
print 'EXCHANGE'
print Exchange.query.all()
print 'STOCKPOSITION'
positions = StockPosition.query.all()
for pos in positions:
	print pos
	trans = pos.all_transactions
	for tran in trans:
		print '\t' + str(tran)
