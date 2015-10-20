import parse
import sys
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
	return False

def cancel_server_message_test():
	return False

hb_success=heartbeat_test()

if hb_success == False:
	print 'ERROR WITH HEARTBEAT PARSING'
	sys.exit()

so_success=send_order_test()

if so_success == False:
	print 'ERROR WITH SEND_ORDER PARSING'
	sys.exit()

cnc_serv_success=cancel_server_message_test()

if cnc_serv_success == False:
	print 'ERROR WITH CANCEL SERVER MESSAGE PARSING'
	sys.exit()
