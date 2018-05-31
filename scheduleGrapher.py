import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import sys

# Remember that line 17 had to be removed
# Cause it was displaying in March
# Which was weird, but correct given the data
# It was BMD (MYR) CRUDE PALM OIL

if len(sys.argv) < 2:
    print("USAGE: %s input-file" % (sys.argv[0]))
    sys.exit(1)

DATFILE = sys.argv[1]

def ToDateTime(my_string):
    return datetime.strptime(my_string, "%Y%m%d%H%M%S%f")


# This is a suite of functions to chomp through a
# Rips off the front of a string up to the next  character
def ChompNextBlock(my_string):
    if(not my_string):
        return False

    i = 0
    while(my_string[i:i + 1] != ''):
        i += 1

    return my_string[i + 1:len(my_string)]


# Gets the value of the next expression after the = and before the 
# Also returns the rest of the string, should you want it
def GetNextValue(my_string):
    if not my_string:
        return False

    i = 0
    while my_string[i:i + 1] != '=':
        i += 1

    j = i
    while my_string[j:j + 1] != '':
        j += 1

    return my_string[i + 1:j], ChompNextBlock(my_string)


# Gets the label of the next block in the string
def GetNextLabel(my_string):
    if(not my_string):
        return False

    i = 0
    while(my_string[i:i + 1] != "=" and i < len(my_string)):
        i += 1

    return my_string[:i]


# For each line, we're going to want to build a list of products
file_object  = open(DATFILE, 'r')
product_list = []

print("We've opened the file successfully")

for line in file_object:
    this_product = {}
    line = ChompNextBlock(line)  # Chew off the 35
    this_product['market_segment_id'], line = GetNextValue(line)  # Grab the 1300
    this_product['product_complex'], line = GetNextValue(line)  # grab the 1227
    this_product['security_group'], line = GetNextValue(line)  # grab the 1151
    this_product['no_dates'], line = GetNextValue(line)  # grab the 580
    date_list = {}
    session_list = []

    for i in range(0, int(this_product['no_dates'])):
        date_list['trade_date'], line = GetNextValue(line)  # Grab the 75
        date_list['no_sessions'], line = GetNextValue(line)  # Grab the 386
        for j in range(0, int(date_list['no_sessions'])):

            session_id, line = GetNextValue(line)  # 336
            timestamp, line = GetNextValue(line)  # 341

            session_list.append((session_id, timestamp))

            # I don't really care about the next value, but we still have to deal with it
            next_label = GetNextLabel(line)
            if next_label == '625':
                session_sub_id, line = GetNextValue(line)  # 625

    this_product['date_list'] = date_list
    this_product['session_list'] = session_list
    product_list.append(this_product)

print("Read the data in alright")

# So now we need to graph it out
i = 0
switch_map = {
    '21': 'b',  # Pre-open, blue
    '17': 'g',  # Trading
    '2': 'r',  # Halt
    '18': 'y',  # Not available for trading
    '4': 'c',  # Close
    '26': 'm'   # Post-Close
}
xs = []
ys = []
cs = []
labels = []

for product in product_list:
    # For each product
    i += 5

    for session_tuple in product['session_list']:
        # For each session, the color will be determined by the status code
        status_code = session_tuple[0]
        status_color = switch_map[status_code]

        # Get the x from the time that's passed
        session_time = session_tuple[1]
        xs.append(ToDateTime(session_time) - timedelta(hours=5))
        ys.append(i)
        cs.append(status_color)
        labels.append(product['product_complex'])


fig, ax = plt.subplots()
ax.grid(True)
plt.scatter(xs, ys, c=cs)

# rotates and right aligns the x labels, and moves the bottom of the
# axes up to make room for them
fig.autofmt_xdate()
plt.show()
