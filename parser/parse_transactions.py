import os
import sys
import maketake_utility
from reference.fix_tables import fix_fields_table, fix_msg_types_table, sidevalues_table
from parse_maketake import MakeTakeParser


class Transaction(object):
    def __init__(self, base_string):
        self.base_string = base_string
        self.properties = {}

        self.parse_fix_pairs()
        self.properties['Commission'] = '-1.00'

    def __str__(self):
        return str(self.properties)

    def __repr__(self):
        return self.__str__()

    def parse_fix_pairs(self):
        parsed_string = self.base_string

        # each transaction always begins with this prefix
        pairs_start = parsed_string.find('8=FIX')
        pairs_string = parsed_string[pairs_start:]

        # all transaction attributes are split by this delimiter
        pairs = pairs_string.split('')

        # grab all the attribute pairs in the data file
        # numbers will come in the form of a tag number and a corresponding value
        pair_dict = {}
        for entry in pairs:
            if entry == ' ' or entry == '':
                continue

            split_pair = entry.split('=')

            if len(split_pair) != 2:
                continue

            try:
                # key is the left value, the tag number
                key = split_pair[0]
                # vlalue is the right value and can be anything
                value = split_pair[1]
                # store the information away and move to the next attribute
                pair_dict[key] = value
            except Exception as e:
                print 'could not add key value pair to transaction data'
                print e

        # add all the properties to the Transaction object, translating as we go
        # from our reference conversion tables
        for key in pair_dict:
            # only add attributes that we know about
            if key in fix_fields_table:
                # grab the key's translation and its value in the pairs list
                key_label = fix_fields_table[key]
                value = pair_dict[key]
                # set the transaction's property
                self.properties[key_label] = value

        # print self.properties;

        # look up the message type, which will be a string value
        msg_type_val = self.properties['MsgType']

        # use the message val to translate it to a meaningful string,
        # using the message types table
        self.transaction_type = fix_msg_types_table[msg_type_val]

    # return the relevant property from the transaction
    def get(self, key):
        return str(self.properties[key])


# trigger parsing the maketake file
def parse_maketake(data_file):
    parser = MakeTakeParser()
    return parser.parse_maketake(data_file)


###
# Take in the account name (number) and the text to parse for valid transactions.
# Output a set of valid transactions
##
def parse_transactions(account_name, data_filetext):
    unparsed_transactions = data_filetext.split('\n')

    # parse all transactions for all valid lines in the data file
    parsed_transactions = []
    for unparsed in unparsed_transactions:
        # avoid lines with comments, irrelevant information, or empty lines
        if '#' in unparsed or not unparsed.strip() or ('SetStatus' in unparsed):
            continue

        # build a transaction object with the line as the input
        # this is the where the majority of the data parsing is done
        parsed = Transaction(unparsed)
        parsed_transactions.append(parsed)

    # only allow single order transactions, at least for now
    allowed_transactions = ['D']
    valid_parsed_transactions = [item for item in parsed_transactions if
                                 item.properties['MsgType'] in allowed_transactions]

    # Maketake fee lookup
    for valid_transaction in valid_parsed_transactions:
        properties = valid_transaction.properties
        side = properties['Side']
        exchange = properties['ExDestination']

        # liquidity is being added if true, else it is taking liquidity
        liquidity_bool = bool(side == '2')

        # Manage the maketake portion. Maketake fees are initially set by the parser, and are updated when a new
        # maketake is uploaded. This could be handled by the front-end, but that would slow down the creation of
        # reports. Instead we opted to handle the semi-rare event of changes to the maketakes at upload-time.
        maketake_filetext = maketake_utility.find_maketake(account_name, valid_transaction)

        # At least a start-up maketake should exist, so don't forget to have at least one available at the start
        if not maketake_filetext:
            print "No valid maketake was found for the transaction's transaction time"
            print valid_transaction
            return []

        # Parse the maketake file, search for the appropriate fee, and set the fee on the transaction
        maketake_fee_searcher = MakeTakeParser().parse_maketake(maketake_filetext)
        found_maketake_fee = maketake_fee_searcher.lookup(exchange, liquidity_bool)
        valid_transaction.properties['maketake_fee'] = found_maketake_fee

    # return the list of valid transactions parsed from the data file
    return valid_parsed_transactions


# start here
def main(exec_args):

    # account name is the number on the account & data_location is a valid path from the project root
    account_name = exec_args[1] if len(exec_args) > 0 else None
    data_location = exec_args[2] if len(exec_args) > 1 else None

    if not account_name:
        print "No account name received as parameter to parser (needed for maketake)"
    if not data_location:
        print "No data file location received as parameter to transaction parser."

    if not account_name or not data_location:
        raise Exception("Invalid arguments to the parser")

    # grab the information from the file at the passed filepath
    data_filetext = None

    if os.path.exists(data_location):
        data_filetext = open(data_location, 'r').read()

    parsed_results = parse_transactions(account_name, data_filetext)

    # print_results_nicely(parsed_results)

    return parsed_results


# something to show the results nicely
def print_results_nicely(results):
    print str(len(results)) + ' results'
    for transaction in results:
        print transaction
        print '\n'


if __name__ == '__main__':
    main(sys.argv)
