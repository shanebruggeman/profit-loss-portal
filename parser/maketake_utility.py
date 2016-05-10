import os
from datetime import date
from datetime import timedelta

maketake_upload_location = "maketake_uploads/"


# look for the correct maketake file for the given transaction (determined from TransactTime)
def find_maketake(account_name, transaction):
    print 'Finding maketake for account name ' + account_name

    # cut off the hours / minutes / seconds from the transact time
    time = transaction.properties['TransactTime'].split('-')[0]

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
        if account_name != maketake.split("_")[0]:
            print 'Nonmatching maketake'
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


# files are formatted as: <USER>_<FROM_DATE>-<TO_DATE>.txt, where from & to dates are not necessary,
#   but the punctuation is
def parse_file_date(date_string):
    user_half = date_string.split('_')[0]
    date_half = date_string.split('_')[1]

    date_parts = date_half.split('-')
    fromPart = date_parts[0]
    toPart = date_parts[1][:-4]

    fromDate = make_date(fromPart)
    toDate = make_date(toPart)

    return [fromDate, toDate]


# takes a YYYYMMDD string and converts it to a date object
def make_date(date_string):
    # nothing passed in
    if date_string == '':
        return ''

    yearParsed = int(date_string[:4])
    monthParsed = int(date_string[4:6])
    dayParsed = int(date_string[6:])
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

    if has_to_date:
        to_parts = to_date.split('-')
        to_year = int(str(to_parts[0]))
        to_month = int(str(to_parts[1]))
        to_day = int(str(to_parts[2]))

    f_date = date(from_year, from_month, from_day)
    t_date = date(to_year, to_month, to_day) if has_to_date else None

    added_filename = encode_file_date(account_id, f_date, t_date)
    resolve_conflicts(added_filename)


def resolve_conflicts(addedFilename):
    addFileDate = parse_file_date(addedFilename)
    add_from = addFileDate[0]
    add_to = addFileDate[1] if addFileDate[1] != '' else None

    uploaded_maketakes = os.listdir(maketake_upload_location)

    for maketake in uploaded_maketakes:

        # separate the maketake filename into its parts
        established = parse_file_date(maketake)
        established_to_date = established[0]
        established_from_date = established[1] if established[1] != '' else None

        # find differences
        oldRange = [established_from_date, established_to_date]
        newRange = [add_from, add_to]
        date_set_difference(oldRange, newRange);

        print date_set_difference(oldRange, newRange)


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

    changes = []

    if old_is_first:
        if old_ends and new_ends:
            # keep things the same if there is no overlap
            if e1 < s2:
                pass

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
                pass

            # old date is overlapped to the right by the new date
            # old date is changed to be only the left portion before the right overlap
            elif e1 >= s2:
                leftStart = e1
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
                pass

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
                # note that no changes are pushed
                pass

        # if the new transaction comes first and doesn't end, the old transaction is obliterated
        elif old_ends and not new_ends:
            pass

        elif not old_ends and new_ends:

            # discard cases where there is no overlap
            if e2 < s1:
                pass

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
                pass

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
                pass

            if e2 >= s1:
                rightStart = e2 + timedelta(1)
                rightEnd = None
                changes.append([rightStart, rightEnd])

        # new date completely consumes old date
        elif not old_ends and not new_ends:
            pass

    print changes

# takes account name, from & to date objects and makes the correct filename for them
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
