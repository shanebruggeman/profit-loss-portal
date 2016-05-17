import os


class OptionRowHolder(object):
    def __init__(self):
        self.all_tabs = []
        top_props = ['top', '  ', 'top', '   ', '(top add fee)', '  ', '(top take fee)', '', 'top=top']
        top_tab = StockRow(top_props)
        self.all_tabs.append(top_tab)

    def __str__(self):
        return str(self.all_tabs)

    def __repr__(self):
        return str(self)

    def size(self):
        return len(self.all_tabs)

    def get_first(self):
        return self.all_tabs[0]

    # determines the correct fee for a given exchange and liquidity boolean
    def lookup(self, exchange, isAddingLiquidity):
        print "Looking up the exchange " + exchange
        # print self.all_tabs[3]
        for tab in self.all_tabs:
            print tab
            print tab.properties["name"]
            if tab.properties["name"] == exchange or exchange in tab.properties["alias"]:
                fee = "add_fee" if isAddingLiquidity else "take_fee"
                print fee
                # print "Found exchange " + exchange + "\n"
                return tab.properties[fee]

        # print "Exchange " + exchange + " was not found!\n"
        return False

    # each tab acts as a container to those beneath it
    def add(self, stock_row):
        last_added_tab = self.all_tabs[len(self.all_tabs) - 1]
        last_added_tabval = last_added_tab.get_tabval()

        next_added_tabval = stock_row.get_tabval()
        parent_tab = {}

        # if the last added tab was nested deeper than the incoming one
        indent_in = next_added_tabval > last_added_tabval

        # if the last added tab was nested less deeply than the incoming one
        indent_back = next_added_tabval < last_added_tabval

        # if the last added tab was nested equally as deep as the incoming one
        indent_same = next_added_tabval == last_added_tabval

        # a deeper nesting indicates the last added tab was the parent
        if indent_in:
            parent_tab = last_added_tab

        # less deep or equal nesting implies an earlier parent than the last added
        if indent_back or indent_same:

            # start at the back and move towards the front until the list's tab item is less deeply nested
            i = len(self.all_tabs) - 1
            parent_tab = self.all_tabs[i]
            parent_tab_val = parent_tab.get_tabval()

            # continue until we hit a less tabbed entry.
            # (the zero'eth entry is guaranteed to be less than)
            while i >= 0 and parent_tab_val >= next_added_tabval:
                parent_tab = self.all_tabs[i]
                parent_tab_val = parent_tab.get_tabval()
                i -= 1

        # retrieve the added tab's name and add them to the parent
        stock_name = stock_row.properties["name"]

        # adding the entry to the parent
        parent_tab.children[stock_name] = stock_row

        # always add the added tab to the list of tabs
        self.all_tabs.append(stock_row)

        # always return the overall built object
        return self.all_tabs[0]


class StockRow(object):
    def __init__(self, line_parts):
        self.line_parts = line_parts
        self.parent = None
        self.properties = {}
        self.children = {}
        self.parse(line_parts)

    def get_tabval(self):
        return self.properties["tabval"]

    def parse(self, line_parts):
        # each of these corresponds to a part of the line
        # where lines go [characters, space, characters, space, ....]
        make_take = 0
        option_name = 2
        add_liquidity_fee = 4
        take_liquidity_fee = 6
        tabbed_space = 7
        attributes_pos = 8

        # tabval lets us know how deeply nested our row is
        tabbing = line_parts[tabbed_space]
        tabval = len(tabbing) / 4

        # retrieve the predetermined parts of the line
        maketake = line_parts[make_take]
        op_name = line_parts[option_name]
        op_aliases = []
        add_fee = line_parts[add_liquidity_fee]
        take_fee = line_parts[take_liquidity_fee]

        # split into (blank=blank) tokens
        attributes = line_parts[attributes_pos].split(' ')

        # split (blank1=blank2,blank3) into (blank) and (blank2,blank3)
        for attr in attributes:
            attribute_breakdown = attr.split('=')
            attr_name = attribute_breakdown[0]
            attr_vals = attribute_breakdown[1].split(',')

            # exchanges can have multiple names, comma separated on the exchange attribute
            if attr_name == 'exchange':
                if len(attr_vals) >= 1:
                    for alias in attr_vals:
                        alias = alias.strip()
                        alias_directory = '../aliases/' + alias
                        path_exists = os.path.exists(alias_directory)
                        # case where a lot of aliases are required, where a file can just be supplied
                        if path_exists:
                            print 'found alias file, ' + alias_directory + ', opening ...'
                            alias_file = open(alias_directory, 'r').read()

                            # alias file should have form of altName1,altName2,altname3
                            for fileAlias in alias_file.split(','):
                                op_aliases.append(fileAlias.strip())
                        else:
                            op_aliases.append(alias)

        properties = {
            "name": op_name,
            "alias": op_aliases,
            "maketake": maketake,
            "add_fee": add_fee,
            "take_fee": take_fee,
            "tabval": tabval
        }

        self.properties = properties

    def set_parent(self, parent):
        self.parent = parent

    def __str__(self):
        return str(self.properties)

    def __repr__(self):
        return str(self)


# process the fee file so that we can easily look up relevant fees
class MakeTakeParser(object):
    def __init__(self):
        pass

    def __str__(self):
        return str(self.properties)

    def __repr__(self):
        return str(self)

    def parse_maketake(self, maketake_filetext):
        lines = maketake_filetext.split('\n')

        properties = {}
        count = 0

        # word map holds the parts of the line
        # like add_fee, take_fee, and the spaces between
        word_map = []

        # build the word map for each of the lines
        for line in lines:
            # remove commented or irrelevant lines
            if '#' in line or not line.strip():
                continue

            words = []
            build_word = ''
            index = 0

            for char in line:
                if len(build_word):
                    if index == len(line) - 1:
                        words.append(build_word + char)

                    if build_word[0] == ' ' and char != ' ':
                        words.append(build_word)
                        build_word = char
                        index += 1
                        continue

                    if build_word[0] != ' ' and char == ' ':
                        words.append(build_word)
                        build_word = char
                        index += 1
                        continue

                index += 1
                build_word = build_word + char

            word_map.append(words)

        holder = OptionRowHolder()

        # make a stock row object to hold each line's information,
        # and hold all the rows inside an OptionRowHolder
        for line in word_map:
            tab = StockRow(line)
            holder.add(tab)

        return holder
