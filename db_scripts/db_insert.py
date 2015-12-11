import sys
sys.path.append('../')
sys.path.append("/Users/shanebruggeman/Documents/CodingProjects/profit-loss-portal/")
sys.path.append("/Users/shanebruggeman/Documents/CodingProjects/profit-loss-portal/parser")
from app import db
from models import *
import datetime

sys.path.append('../parser')
import parse
from datetime import datetime
import re

def main(exec_args):
	# res = parse.main('./parser/testdata1.txt')
	res = parse.main(["", "example_parse_data.txt", "example_maketake.txt", "Box"])

	#Add to this list for creating transactions, (CURRENTLY ONLY SEND ORDERS)
	allowedMessages = 'D'
	for trans in res:
		if trans.get('MsgType') in allowedMessages:
			print 'Adding transaction to database!'
			try:
				date=trans.get('TransactTime')
				year=date[:4]
				month=date[4:6]
				day=date[6:8]
				ttime=re.split("-", date)[1]
				date_str=year+'/'+month+'/'+day+' '+ttime
				bs=trans.get('PutOrCall')

				account_id = 1
				exchange_id = 1
				price = float(trans.get('Price'))
				units = int(trans.get('OrderQty'))
				sec_sym = trans.get('UnderlyingSymbol') + ' ' + ('CALL ' if bs==1 else 'PUT ') + day+ date_obj.strftime("%b")+year[2:] + ' ' + trans.get('StrikePrice') + ' (C)'
				settle = datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S.%f" )
				entry = settle
				trade = settle
				ticket_number = "UNKNOWN TICKET NUMBER"
				if bs == 1:
					buy_sell='Buy'
				else:
					buy_sell='Sell'

				commission = float(trans.get('Commission'))

				# all parsed transactions are not opening positions
				parsed_transaction = Transaction(account_id, exchange_id, price, units, sec_sym, settle, entry, trade, ticket_number, buy_sell, commission, False)

				existingPosition = StockPosition.query.filter(StockPosition.account_id == account_id).filter(StockPosition.date == entry).filter(StockPosition.symbol == sec_sym).first()

				# this option has not been traded today
				if existingPosition == None:
					priorPosition = StockPosition.query.filter(StockPosition.account_id == account_id).filter(StockPosition.symbol == sec_sym).orderBy(StockPosition.date).first()

					# there is no prior position, because this option has never been traded, and the parsed transaction will be part of the first position
					if priorPosition == None:
						# make a 0 value trade to start a net position, mark it as "True", this is an opening position
						baseStartPosition = Transaction(account_id, exchange_id, -1, 0, sec_sym, settle, entry, trade, ticket_number, buy_sell, commission, True)
						firstStockPosition = StockPosition(sec_sym, entry)

						# add the starting position and the first day trade to the new position
						firstStockPosition.all_transactions.append(baseStartPosition)
						firstStockPosition.all_transactions.append(parsed_transaction)

						db.session.add(firstStockPosition)

					# prior position is available, and we have no position (yet) for the parsed transaction's day and symbol
					else:
						# take the net values from the old position and represent them as a summed transaction of all that has occurred before this day
						positionSumTransaction = sumPosition(priorPosition)

						# the new day has the net value of the old position and the newly parsed entry
						newDayPosition = StockPosition(sec_sym, entry)
						newDayPosition.all_transactions.append(positionSumTransaction)
						newDayPosition.all_transactions.append(parsed_transaction)

						db.session.add(newDayPosition)

				# this option has been traded today
				else:
					existingPosition.all_transactions.append(parsed_transaction)


			except Exception as e:
				print e
				sys.exit(-1)

	db.session.commit()

if __name__ == '__main__':
	main(sys.argv)