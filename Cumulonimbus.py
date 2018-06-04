import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import matplotlib.pyplot as plt
import matplotlib
import numpy
import matplotlib.dates as matdates
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from datetime import timedelta

switch_map = {
    '21': 'b',  # Pre-open, blue
    '17': 'g',  # Trading
    '2': 'r',  # Halt
    '18': 'y',  # Not available for trading
    '4': 'c',  # Close
    '26': 'm'   # Post-Close
}

product_list = {}
file_path = ""
youroptions = []


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


def OpenFile():
    global file_path
    global youroptions
    youroptions = []
    file_path = filedialog.askopenfilename()
    file_object = open(file_path, 'r')
    global product_list

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
        this_product['session_list'] = sorted(session_list, key=lambda x: x[1])
        print(this_product['product_complex'])
        print(this_product['session_list'])
        product_list[this_product['product_complex']] = this_product
        youroptions.append(this_product['product_complex'])

    youroptions = sorted(youroptions)
    for prod in youroptions:
        listbox.insert(tk.END, prod)
    print("Read the data in alright")


def ListboxChooseGraph(event):
    global product_list
    productindex = listbox.curselection()[0]
    productcomplex = youroptions[productindex]
    product = product_list[productcomplex]
    xs = []
    ys = []
    cs = []

    firstDate = ToDateTime(product['session_list'][0][1])
    lastDate = ToDateTime(product['session_list'][-1][1])
    firstDate = firstDate.strftime("%b %d %Y")
    lastDate = lastDate.strftime("%b %d %Y")

    for session_tuple in product['session_list']:
        # For each session, the color will be determined by the status code
        status_code = session_tuple[0]
        status_color = switch_map[status_code]

        # Get the x from the time that's passed
        session_time = session_tuple[1]
        xs.append(ToDateTime(session_time) - timedelta(hours=5))
        ys.append(0)
        cs.append(status_color)

    ax.clear()
    majorFmt = matdates.DateFormatter('%a %d, %H:%M')
    minorFmt = matdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(majorFmt)
    ax.xaxis.set_minor_formatter(minorFmt)
    ax.set_title(productcomplex + " Hours\n" + firstDate + " - " + lastDate)
    PlotLines(xs, ys, cs)
    ax.scatter(xs, ys, c=cs, marker='D', zorder=2)
    ax.grid(True)
    ax.get_yaxis().set_ticks([0])
    fig.autofmt_xdate()
    ax.autoscale()
    canvas.draw()

def PlotLines(xs, ys, cs):
    for i in range(0, len(xs) - 1):
        ax.plot(xs[i:i+2], ys[i:i+2], c=cs[i], zorder=1)

root = tk.Tk()
root.title("Cumulonimbus v0.1")
menu = tk.Menu(root)
root.config(menu=menu)
filemenu = tk.Menu(menu)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Open File", command=OpenFile)

listbox = tk.Listbox(root, height=5)
listbox.grid(column=0, row=0, sticky=(tk.N,tk.W,tk.S))
listbox.bind("<<ListboxSelect>>", ListboxChooseGraph)

s = tk.ttk.Scrollbar(root, orient=tk.VERTICAL, command=listbox.yview)
s.grid(column=1, row=0, sticky=(tk.N,tk.S,tk.W))
listbox['yscrollcommand'] = s.set
tk.ttk.Sizegrip().grid(column=1, row=1, sticky=(tk.S))
root.grid_rowconfigure(0, weight=1)

fig = plt.Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
t = numpy.arange(0.0, 3.0, 0.01)
s = numpy.sin(2*numpy.pi*t)

ax.plot(t, s)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=2, row=0)

toolbar_frame = tk.Frame(root)
toolbar_frame.grid(column=2, row=1, sticky="W")
toolbar = NavigationToolbar2TkAgg(canvas, toolbar_frame)
toolbar.update()
toolbar.grid(column=2, row=1)

legendimg = tk.PhotoImage(file='legend_50.png')
legend = tk.Label()
legend['image'] = legendimg
legend.grid(column=3, row=0)

root.mainloop()
