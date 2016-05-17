import os
from datetime import date
from datetime import timedelta
from shutil import copyfile

maketake_upload_location = "maketake_uploads/"


# look for the correct maketake file for the given transaction (determined from TransactTime)
def find_maketake(account_name, transaction):
    print 'Finding maketake for account name ' + str(account_name)
    if hasattr(transaction, 'properties'):
	print "not DB"
        time = transaction.properties['TransactTime'].split('-')[0]
        print time
    else:
        print "DB TRNA"
	print transaction.settle
	time1 = str(transaction.settle)
	time2 = time1.split(' ')[0]
	print time2
        time = "".join(str(transaction.settle).split(' ')[0].split('-'))
        print time
    parse_date = make_date(time)

    uploaded_maketakes = os.listdir(maketake_upload_location)
    print 'These maketakes are available:'
    print uploaded_maketakes

    corresponding_maketake = None

    for maketake in uploaded_maketakes:
        print 'Considering maketake: '
        print maketake

        # we've found something that matches
        if (corresponding_maketake != None):
            break

        # check only uploads uploaded by the passed user
        if str(account_name) != maketake.split("_")[0]:
            print 'Nonmatching maketake'
            continue

        uploadDates = parse_file_date(maketake.split('.')[0])
        uploadFromDate = uploadDates[0]
        uploadToDate = uploadDates[1]
        print "HERE"
        hasFrom = uploadFromDate != ''
        hasTo = uploadToDate != ''

        # something has gone wrong in the file storing name scheme
        if not hasFrom and not hasTo:
            raise "There is a file that doesn't follow the naming convention in maketake uploads"
        print hasFrom
        print hasTo
        # the stored maketake has a range in which it's valid
        if hasFrom and hasTo:
            between = (uploadFromDate <= parse_date) and (uploadToDate >= parse_date)
            print "BETWEEN:"
            print between
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


# files are formatted as: <USER>_<FROM_DATE>-<TO_DATE>.txt, where from & to dates are not necessary,
#   but the punctuation is
def parse_file_date(date_string):
    print 'File date: ' + date_string
    user_half = date_string.split('_')[0]
    date_half = date_string.split('_')[1]

    date_parts = date_half.split('-')
    fromPart = date_parts[0]
    toPart = date_parts[1]

    print 'from part: ' + str(fromPart)
    print 'to part: ' + str(toPart)

    fromDate = make_date(fromPart)
    toDate = make_date(toPart)

    print 'Returning [' + str(fromDate) + ',' + str(toDate) + ']'

    return [fromDate, toDate]


# takes a YYYYMMDD string and converts it to a date object
def make_date(date_string):
    print 'Make date: ' + date_string
    # nothing passed in
    if date_string == '':
        return ''

    print date_string[:4]
    print date_string[4:6]
    print date_string[6:]
    yearParsed = int(float(date_string[:4]))
    monthParsed = int(float(date_string[4:6]))
    dayParsed = int(float(date_string[6:]))
    date_obj = date(yearParsed, monthParsed, dayParsed)
    return date_obj


# takes the from & to dates (taken from html date input)
#   and renames files as needed to make room for the new file
def rename_maketakes(account_id, from_date, to_date):
    from_parts = from_date.split('-')
    from_year = int(str(from_parts[0]))
    from_month = int(str(from_parts[1]))
    from_day = int(str(from_parts[2]))

    print from_parts

    has_to_date = to_date != ""
    to_year = None
    to_month = None
    to_day = None

    print 'Has To Date: ' + str(has_to_date)

    if has_to_date:
        to_parts = map(str, to_date.split('-'))
        print to_parts

        to_year = int(float(to_parts[0]))
        to_month = int(float(to_parts[1]))
        to_day = int(float(to_parts[2]))

    f_date = date(from_year, from_month, from_day)
    t_date = date(to_year, to_month, to_day) if has_to_date else None

    added_filename = encode_file_date(account_id, f_date, t_date)
    resolve_conflicts(account_id, added_filename)


def resolve_conflicts(account_id, addedFilename):
    print 'resolving conflicts for ' + addedFilename
    addFileDate = parse_file_date(addedFilename)
    add_from = addFileDate[0]
    add_to = addFileDate[1] if addFileDate[1] != '' else None

    print 'added from: ' + str(add_from)
    print 'added to: ' + str(add_to)

    uploaded_maketakes = os.listdir(maketake_upload_location)

    for maketake in uploaded_maketakes:
        print 'maketake: ' + str(maketake)

        # separate the maketake filename into its parts (minus the .txt extension)
        established = parse_file_date(maketake[:-4])
        established_from_date = established[0]
        established_to_date = established[1] if established[1] != '' else None

        print 'established from: ' + str(established_from_date)
        print 'established to: ' + str(established_to_date)

        # find differences
        oldRange = [established_from_date, established_to_date]
        newRange = [add_from, add_to]
        date_set_difference(oldRange, newRange);

        changes = date_set_difference(oldRange, newRange)

        # there was no overlap, so don't worry about this maketake
        if changes is None:
            print 'No changes for maketake'
            print maketake
        else:
            # break original filename into its parts if the uploaded maketake changed its effective dates
            for change in changes:
                fname = encode_file_date(account_id, change[0], change[1])
                copyfile(maketake_upload_location + maketake, maketake_upload_location + fname + '.txt')
                print fname

            os.remove(maketake_upload_location + maketake)


# return date ranges that are in the old range that are not in the new range
def date_set_difference(old_range, new_range):
    s1 = old_range[0]
    e1 = old_range[1]

    s2 = new_range[0]
    e2 = new_range[1]

    start_delta = s1 - s2

    # booleans for determining the correct dates
    old_ends = e1 is not None
    new_ends = e2 is not None

    old_is_first = start_delta.total_seconds() < 0
    same_start = start_delta.total_seconds() == 0
    new_is_first = start_delta.total_seconds() > 0

    is_changed = True
    changes = []

    if old_is_first:
        if old_ends and new_ends:
            # keep things the same if there is no overlap
            if e1 < s2:
                is_changed = False

            # old date completely holds new date
            # old date is broken into left and right halves
            elif e2 < e1:
                # the left starts with the old start value and ends the day before the new date takes effect
                leftStart = s1
                leftEnd = s2 - timedelta(1)
                changes.append([leftStart, leftEnd])

                # the right starts with the day after the new date's end and ends at the old end day
                rightStart = e2 + timedelta(1)
                rightEnd = e1
                changes.append([rightStart, rightEnd])

            # old date overlaps new date on the right side
            # old date is changed to only be the left portion before the right overlap
            elif e2 >= e1:
                # the left begins at the same time
                # the right ends the day before the new date takes effect
                leftStart = s1
                leftEnd = s2 - timedelta(1)
                changes.append([leftStart, leftEnd])

        elif old_ends and not new_ends:

            # there is no overlap, change nothing about the old transaction
            if e1 < s2:
                is_changed = False

            # old date is overlapped to the right by the new date
            # old date is changed to be only the left portion before the right overlap
            elif e1 >= s2:
                leftStart = s1
                leftEnd = s2 - timedelta(1)
                changes.append([leftStart, leftEnd])

        # imposing a right limit forces an end to not-ending ranges
        elif not old_ends and new_ends:

            leftStart = s1
            leftEnd = s2 - timedelta(1)
            changes.append([leftStart, leftEnd])

        # same rule as old_ends and new_ends
        elif not old_ends and not new_ends:

            leftStart = s1
            leftEnd = s2 - timedelta(1)
            changes.append([leftStart, leftEnd])

    elif new_is_first:
        if old_ends and new_ends:

            # do nothing if there is no overlap
            if e2 < s1:
                is_changed = False

            # new date overlaps to the left of the new date
            # old date is broken into its right portion
            elif e2 < e1:
                # the right starts the day after the end of the new date
                # the right end remains the same
                rightStart = e2 + timedelta(1)
                rightEnd = e1
                changes.append([rightStart, rightEnd])

            # the new date completely overlaps the old date
            # the old date is invalid and no longer applies, so no parts to break it into
            elif e2 >= e1:
                # note that is_changed remains true, so the date is replaced
                pass

        # if the new transaction comes first and doesn't end, the old transaction is obliterated
        elif old_ends and not new_ends:
            pass

        elif not old_ends and new_ends:

            # discard cases where there is no overlap
            if e2 < s1:
                is_changed = False

            # make the not-stopping old transaction a little shorter on the left
            elif e2 >= s1:
                rightStart = e2 + timedelta(1)
                rightEnd = None
                changes.append([rightStart, rightEnd])

        # New date completely consumes the old date
        elif not old_ends and not new_ends:
            pass

    elif same_start:

        if old_ends and new_ends:

            # discard cases where there is no overlap
            if e2 < s1:
                is_changed = False

            # new date overlaps the old date to the left
            # old date is broken into its right portion
            if e2 < e1:
                # the right starts the day after the end of the new date
                # the right ends at the same time
                rightStart = e2 + timedelta(1)
                rightEnd = e1
                changes.append([rightStart, rightEnd])

            # new date completely overlaps the old date
            # old date is invalid and and no longer applies, so no parts to break it into
            elif e2 >= e1:
                pass

        #  new date completely consumes old date
        elif old_ends and not new_ends:
            pass

        elif not old_ends and new_ends:

            # ignore the case of no overlap
            if e2 < s1:
                is_changed = False

            if e2 >= s1:
                rightStart = e2 + timedelta(1)
                rightEnd = None
                changes.append([rightStart, rightEnd])

        # new date completely consumes old date
        elif not old_ends and not new_ends:
            pass

    return changes if is_changed else None


# takes account name, from & to date objects and makes the correct filename for them
def encode_file_date(name, from_date, to_date):
    print 'Encoding filename'
    print 'name: ' + str(name)
    print 'from: ' + str(from_date)
    print 'to: ' + str(to_date)

    validFrom = (from_date != None)
    validTo = (to_date != None)

    print 'validFrom: ' + str(validFrom)
    print 'validTo: ' + str(validTo)

    if not validFrom and not validTo:
        raise "Cannot encode filenames missing both from and to dates"

    from_part = ''

    if validFrom:
        y = '{0:04d}'.format(from_date.year)
        m = '{0:02d}'.format(from_date.month)
        d = '{0:02d}'.format(from_date.day)
        from_part = y + m + d

    to_part = ''

    if validTo:
        y = '{0:04d}'.format(to_date.year)
        m = '{0:02d}'.format(to_date.month)
        d = '{0:02d}'.format(to_date.day)
        to_part = y + m + d

    return name + "_" + from_part + '-' + to_part
