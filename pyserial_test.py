import sys
import glob
import serial
# Import tkinter
from tkinter import *


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

 
# Create the root window
root = Tk()
root.geometry('180x200')
 
# Create a listbox
listbox = Listbox(root, width=40, height=10, selectmode=MULTIPLE)
 
# Inserting the listbox items
portList = serial_ports()
for seriales in portList:
	listbox.insert(0,seriales)
 
# Function for printing the
# selected listbox value(s)
def selected_item():
     
    # Traverse the tuple returned by
    # curselection method and print
    # corresponding value(s) in the listbox
    for i in listbox.curselection():
        print(listbox.get(i))
 
# Create a button widget and
# map the command parameter to
# selected_item function
btn = Button(root, text='Print Selected', command=selected_item)
 
# Placing the button and listbox
btn.pack(side='bottom')
listbox.pack()
 
root.mainloop()