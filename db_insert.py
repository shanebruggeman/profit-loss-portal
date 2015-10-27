from app import db
from models import *
import datetime
import sys
sys.path.append('./parser')
import parse


res = parse.main('./parser/testdata1.txt')


#Add to this list for creating transactions
allowedMessages = 'D'
for trans in res:
	if trans.get('MsgType') in allowedMessages:
		print 'Adding transaction to database!'
		try:
			date=trans.get('TransactTime')
			bs=trans.get('PutOrCall')
			if bs == 1:
				buy_sell='Buy'
			else:
				buy_sell='Sell'
			new_trans=Transaction(0,0,float(trans.get('Price')), int(trans.get('OrderQty')),trans.get('UnderlyingSymbol'), date, date, date, trans.get('Symbol'), buy_sell, float(trans.get('Commission')))
			db.session.add(new_trans)
		except:
			sys.exit(-1)
db.session.commit()
