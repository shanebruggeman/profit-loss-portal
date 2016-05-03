import os
import datetime

maketake_upload_location = "maketake_uploads/"


# look for the correct maketake file for the given transaction (determined from TransactTime)
def find_maketake(account_name, transaction):
    # cut off the hours / minutes / seconds from the transact time
    time = transaction.properties['TransactTime'].split('-')[0]

    parse_date = make_date(time)

    uploaded_maketakes = os.listdir(maketake_upload_location)

    corresponding_maketake = None

    for maketake in uploaded_maketakes:

        # we've found something that matches
        if (corresponding_maketake != None):
            break

        # check only uploads uploaded by the passed user
        if not account_name in maketake:
            continue

        uploadDates = parse_file_date(maketake)
        uploadFromDate = uploadDates[0]
        uploadToDate = uploadDates[1]

        hasFrom = uploadFromDate != ''
        hasTo = uploadToDate != ''

        # something has gone wrong in the file storing name scheme
        if not hasFrom and not hasTo:
            raise "There is a file that doesn't follow the naming convention in maketake uploads"

        # the stored maketake has a range in which it's valid
        if hasFrom and hasTo:
            between = (uploadFromDate <= parse_date) and (uploadToDate >= parse_date)
            if between:
                print 'isBetween'
                corresponding_maketake = maketake
            continue

        # the stored maketake has no end specified
        if hasFrom:
            isAfter = (uploadFromDate <= parse_date)
            if isAfter:
                print 'isAfter'
                corresponding_maketake = maketake

        # the stored maketake has no start specified
        if hasTo:
            isBefore = (uploadToDate >= parse_date)
            if isBefore:
                print 'isBefore'
                corresponding_maketake = maketake

    # return the maketake file's text if found, else None
    found_maketake_text = None

    if corresponding_maketake != None:
        checkpath = maketake_upload_location + corresponding_maketake

        print 'Checkpath = ' + checkpath

        found_maketake_text = open(maketake_upload_location + corresponding_maketake, 'r').read()

    return found_maketake_text


# files are formatted as: <USER>_<FROM_DATE>-<TO_DATE>.txt, where from & to dates are not necessary, but the punctuation is
def parse_file_date(date_string):
    user_half = date_string.split('_')[0]
    date_half = date_string.split('_')[1]

    date_parts = date_half.split('-')
    fromPart = date_parts[0]
    toPart = date_parts[1][:-4]

    fromDate = make_date(fromPart)
    toDate = make_date(toPart)

    return [fromDate, toDate]


# takes a YYYY/MM/DD string and converts it to a date object
def make_date(date_string):
    # nothing passed in
    if date_string == '':
        return ''

    yearParsed = int(date_string[:4])
    monthParsed = int(date_string[4:6])
    dayParsed = int(date_string[6:])
    date_obj = datetime.date(yearParsed, monthParsed, dayParsed)
    return date_obj


def encode_file_date(name, from_date, to_date):
    validFrom = (from_date != None)
    validTo = (to_date != None)

    if not validFrom and not validTo:
        raise "Cannot encode filenames missing both from and to dates"

    fromPart = ''

    if validFrom:
        y = '{0:04d}'.format(from_date.year)
        m = '{0:02d}'.format(from_date.month)
        d = '{0:02d}'.format(from_date.day)
        fromPart = y + m + d

    toPart = ''

    if validTo:
        y = '{0:04d}'.format(to_date.year)
        m = '{0:02d}'.format(to_date.month)
        d = '{0:02d}'.format(to_date.day)
        toPart = y + m + d

    return name + "_" + fromPart + '-' + toPart
