import sys
sys.path.append('../')
sys.path.append("/Users/watersdr/Documents/Github/profit-loss-portal/")
sys.path.append("/Users/watersdr/Documents/Github/profit-loss-portal/parser")
from app import db
from models import *
import datetime
from sqlalchemy.sql import extract

# sys.path.append('../parser')
import parse
from datetime import datetime
import re

def main(exec_args):
	# Arguments:
	# 	1) Name of the invoked python file. Does not apply here as we're not running this from the terminal
	# 	2) Transaction data file. This contains all the transactions to parse and insert in this run of the script
	# 	3) Maketake file. This holds all of the relevant fees for the given exchange
	# 	4) Exchange. Right now it's hard coded, but some time it will automatically be added to the parsed result
	res = parse.main(["", (open("example_parse_data.txt",'r')).read(), (open ("example_maketake.txt", 'r')).read(), "Box"])

	#Add to this list for creating transactions, (CURRENTLY ONLY SEND ORDERS)
	allowedMessages = 'D'
	for trans in res:
		# only messages that we know how to parse are going into the database
		if trans.get('MsgType') in allowedMessages:
			print 'Adding transaction to database!'
			try:
				# take the parsed transaction fields and create something to store in the database
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
				settle = datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S.%f" )
				sec_sym = trans.get('UnderlyingSymbol') + ' ' + ('CALL ' if bs==1 else 'PUT ') + day+ settle.strftime("%b")+year[2:] + ' ' + trans.get('StrikePrice') + ' (C)'
				entry = settle
				trade = settle
				ticket_number = "UNKNOWN TICKET NUMBER"
				if bs == 1:
					buy_sell='Buy'
				else:
					buy_sell='Sell'

				commission = float(trans.get('Commission'))

				# if we parsed it the transaction is not an opening position
				parsed_transaction = Transaction(account_id, exchange_id, price, units, sec_sym, settle, entry, trade, ticket_number, buy_sell, commission, False)

				existingPosition = StockPosition.query.filter(extract('year', StockPosition.date) == year).filter(extract('month', StockPosition.date) == month).filter(extract('day', StockPosition.date) == day).first()

				# this option has not been traded today
				if existingPosition == None:
					# priorPosition = StockPosition.query.filter(StockPosition.account_id == account_id).filter(StockPosition.symbol == sec_sym).orderBy(StockPosition.date).first()
					priorPosition = StockPosition.query.filter(StockPosition.account_id == account_id).filter(StockPosition.symbol == sec_sym).order_by(StockPosition.date.desc()).first()
					print priorPosition

					# there is no prior position, because this option has never been traded, and the parsed transaction will be part of the first position
					if priorPosition == None:
						print 'no prior position'
						# make a 0 value trade to start a net position, mark it as "True", this is an opening position
						baseStartPosition = Transaction(account_id, exchange_id, -1, 0, sec_sym, settle, entry, trade, ticket_number, buy_sell, commission, True)
						firstStockPosition = StockPosition(sec_sym, entry)

						# add the starting position and the first day trade to the new position
						firstStockPosition.all_transactions.append(baseStartPosition)
						firstStockPosition.all_transactions.append(parsed_transaction)

						db.session.add(firstStockPosition)
						db.session.commit()

					# prior position is available, and we have no position (yet) for the parsed transaction's day and symbol
					else:
						print 'prior position, no active position'
						# take the net values from the old position and represent them as a summed transaction of all that has occurred before this day
						positionSumTransaction = sumPosition(priorPosition)

						# the new day has the net value of the old position and the newly parsed entry
						newDayPosition = StockPosition(sec_sym, entry)
						newDayPosition.all_transactions.append(positionSumTransaction)
						newDayPosition.all_transactions.append(parsed_transaction)

						db.session.add(newDayPosition)
						db.session.commit()

				# this option has been traded today
				else:
					print 'existing position'
					existingPosition.all_transactions.append(parsed_transaction)
					db.session.commit()


			except Exception as e:
				print e
				sys.exit(-1)

	db.session.commit()

# make a position that reflects the net of everything that came before it
def sumPosition(old_position):
	old_transactions = old_position.all_transactions

	first_old = old_transactions[0]

	# pull relevant information from the first old transaction
	sum_sec_sym = first_old.sec_sym
	sum_settle = first_old.settle
	sum_entry = first_old.entry
	sum_trade = first_old.trade
	sum_ticket_number = first_old.ticket_number
	sum_buy_sell = 'buy'

	# we care about price, units, and commission particularly
	total_price = 0
	total_units = 0
	total_commision = 0

	# find the net units, commision, and price
	for transaction in old_transactions:
		total_units += transaction.units

		if transaction.buy_sell == 'buy':
			total_price += transaction.price * transaction.units
		else:
			total_price += transaction.price * -1 * transaction.units

		total_commision += transaction.units * transaction.commission

	# average the commision and price
	sum_price = total_price / total_units
	sum_units = total_units
	sum_commision = total_commision / total_units

	# return the transaction representing everything that has happened before this date
	return Transaction(old_position.account_id, 'no-exchange', sum_price, sum_units, sum_sec_sym, sum_settle, sum_entry, sum_trade, sum_ticket_number, sum_buy_sell, sum_commision, True)

if __name__ == '__main__':
	main(sys.argv)