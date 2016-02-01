import sys
sys.path.append('../parser')
import parse
import re

def compare(trans, dic):
	i=0
	while i< len(trans):

		lines=str(trans[i]).split(',')
		for line in lines:
			line=line.strip()
			if line.startswith('{'):
				line=line[1:]
			if line.endswith('}'):
				line=line[:-1]
			#print line
			trans_key=line.split(': ')[0][1:-1]
			trans_val=line.split(': ')[1][1:-1]
			dic_val=dic[i].get(trans_key)
			if dic_val != trans_val:
				return False

		i+=1
	return True

def heartbeat_test():
	result=parse.main('heartbeat.txt')
	hbr_str= [{'Commission': '-1.00', 'EncryptMethod': '0', 'BodyLength': '084', 'SenderCompID': '_SenderCompID', 'TargetCompID': '_TargetCompID', 'MsgSeqNum': '6255', 'BeginString': 'FIX.4.2', 'MsgType': 'A', 'CheckSum': '142', 'SendingTime': '20151006-02:52:50.765', 'HeartBtInt': '30'}, {'Commission': '-1.00', 'CheckSum': '148','BodyLength': '055', 'SenderCompID': 'XXXX', 'TargetCompID': 'YYYY', 'MsgSeqNum': '55006', 'BeginString': 'FIX.4.2', 'MsgType': '0', 'SendingTime': '20151006-02:52:57.702'}]

	if  compare(result, hbr_str)== True:
		return True
	else:
		print '\n'
		print str(result[0])
		print '\n'
		print str(hbr_str[0])

		
		return False

def send_order_test():
	result=parse.main('sendorder.txt')
	corr_str = [{'HandlInst': '1', 'StrikePrice': '25.00', 'OrderQty': '50', 'OpenClose': 'O','Commission': '-1.00', 'OrdType': '2', 'ExDestination': 'AMEXO', 'Price': '2.00', 'Side': '1', 'BeginString': 'FIX.4.2', 'TransactTime': '20151006-02:53:33.971', 'ClOrdID': '101', 'BodyLength': '242', 'SenderCompID': '_SenderCompID', 'MaturityMonthYear': '201606', 'PutOrCall': '1', 'MsgType': 'D', 'MaturityDay': '16','Rule80A(aka OrderCapacity)': 'I', 'TargetCompID': '_TargetCompID', 'MsgSeqNum': '6257', 'UnderlyingSymbol': 'BAC', 'SecurityType': 'OPT', 'TimeInForce': '0', 'OnBehalfOfCompID': 'PCUS', 'CheckSum': '200', 'SendingTime': '20151006-02:53:33.971', 'Symbol': 'BAC   160616C00025000'}]

	if  compare(result, corr_str)== True:
		return True
	else:
		print '\n'
		print str(result[0])
		print '\n'
		print str(corr_str[0])

		return False
def cancel_server_message_test():
	result=parse.main('cancel_server_message.txt')
	corr_str=[{'ExecType': '4', 'Commission': '-1.00', 'CheckSum': '225', 'BodyLength': '068', 'SenderCompID': 'XXXX', 'TargetCompID': 'YYYY', 'MsgSeqNum': '55009', 'BeginString': 'FIX.4.2', 'MsgType': '8', 'SendingTime': '20151006-02:53:48.165', 'ClOrdID': '101'}]

	if  compare(result, corr_str)== True:
		return True
	else:
		print '\n'
		print str(result[0])
		print '\n'
		print str(corr_str[0])

		return False
hb_success=heartbeat_test()
so_success=send_order_test()
cnc_serv_success=cancel_server_message_test()
assert(hb_success)
assert(so_success)
assert(cnc_serv_success)

print 'All tests pass!'
sys.exit(0)
