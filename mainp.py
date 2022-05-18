#Developed by Jorge Alberto Morales.
	#Mechatronics Engineering
	#Master in Business Management and Corporate Finance
	#Python Dev
	#JorgeAlberto.Morales@mubea.com


#----------------------import area

import os
import sys
import time, threading
from tkinter import *
from tkinter import messagebox
from functools import partial
from tkinter import ttk
import pyautogui
import serial
import sys
import glob
#---------------------------------


#---------------------------------------Auxiliary Functions-------------------------#

#This function sets the absolute path for the app to access its resources
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def My_Documents(location):
	import ctypes.wintypes
		#####-----This section discovers My Documents default path --------
	CSIDL_PERSONAL = location       # My Documents
	SHGFP_TYPE_CURRENT = 0   # Get current, not default value
	buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
	ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
	#####-------- please use buf.value to store the data in a variable ------- #####
	#add the text filename at the end of the path
	temp_docs = buf.value
	return temp_docs

def line_selector(num,port):
	print("hi")



#def comPort_sel(self,num):
#		if num == 45:
#			for i in self.comList.curselection():
#				print(self.comList.get(i))


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

#---------------------------------End of Auxiliary Functions-------------------------#


#/////----------------------------Reading and Writing Files--------------------------#


#This CSV is for button data. You can add a button if you modify this adequately.
import os
import csv
file = open(resource_path("images/btn_data.csv"))
type(file)
csvreader = csv.reader(file)
header = []
header = next(csvreader)
header
rows = []
for row in csvreader:
	rows.append(row)

file.close()




#/////-----------------------End of Reading and Writing Files--------------------------#


#-----------------------------Start of tkinter classes-----------------------------#

class Interface:
	def __init__(self):
		#threading.Thread.__init__(self)
		self.attrib1 = "Attrib from Interface class"
		#Main Window
		self.mainWindow = Tk()
		self.btn_text = StringVar()
		self.mainWindow.geometry("1024x768")

		#self.mainWindow.title("My GUI Title")
		self.mainWindow.title("Mubea de Mexico - Interfaz para impresión de etiquetas.")

		#self.mainWindow.protocol("WM_DELETE_WINDOW", self.quit)
		self.mainWindow.protocol("WM_DELETE_WINDOW", self.quit)
		
		#in case a background is needed
		self.background_image = PhotoImage(file = resource_path("images/UI.png"))
		label1 = Label(self.mainWindow, image = self.background_image)
		label1.place(x = 0,y = 0)
		self.l = Label(self.mainWindow)
		self.l.pack()	
		h_offset = 2
		w_offset = 4
		fg_offset = "white"
		bg_offset = '#3d85c5'

######Button declaration area
		for i in range(len(rows)):
		#process the first button
			a_temp = rows[i-1][1]
			globals()[a_temp] = Button(self.mainWindow, width = w_offset, height = h_offset)
			globals()[a_temp].configure(width = int(rows[i-1][6]))
			globals()[a_temp].configure(height = int(rows[i-1][7]))
			globals()[a_temp].place(x =int(rows[i-1][2]),y=int(rows[i-1][3]))
			globals()[a_temp].configure(bg = bg_offset)
			globals()[a_temp].configure(fg = fg_offset)
			globals()[a_temp].configure(font=("Helvetica", 10, "bold"))
			globals()[a_temp].configure(text = rows[i-1][4])
			globals()[a_temp].configure(command=partial(line_selector, int(rows[i-1][5])))
			#COM port Listbox
			comList = Listbox(self.mainWindow, width=12, height=8)
			comList.place(x =418,y=620)
			portList = serial_ports()
			for seriales in portList:
				comList.insert(0,seriales)

	def start(self): #Start
		self.mainWindow.mainloop()


	

    #The Interface class contains methods that use attributes from itself and attributes from Process class.
	def method1(self): 
		#print(self.attrib1)
		#print(SecondThread.attrib2)
		#here you can put something to run as second background, do not forget to uncomment #GUI.method1()
		print("hola")
		ser = serial.Serial(
				port='COM3',\
				baudrate=9600,\
				parity=serial.PARITY_NONE,\
				stopbits=serial.STOPBITS_ONE,\
				bytesize=serial.EIGHTBITS,\
				timeout=1)
		print("connected to: " + ser.portstr)
		while finish is False:
			s = ser.read(20)
			label_data = str(s)[2:-3]
			print(label_data)
			print(f"Shop Order is {label_data[0:6]} and type {label_data[6:9]} and standard pack {label_data[9:12]}  ")

	def quit(self):
		if messagebox.askyesno('App','Are you sure you want to quit?'):
            #In order to use quit function, mainWindow MUST BE an attribute of Interface. 
			self.mainWindow.destroy()
			self.mainWindow.quit()

class Process(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.attrib2 = "Attrib from Process1 class"

class Process(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.attrib2 = "Attrib from Process2 class"

    def run(self):
        global finish
        while not finish:
            #print("Proceso infinito")
			#do not start serial until com info is selected.
            #GUI.method1()
            time.sleep(3)
#########################finished classes


finish = False
GUI = Interface()
#Starts the infinity process
SecondThread = Process()
GUI.mainWindow.after(50, SecondThread.start)   
#Waits until GUI is closed
GUI.start()
#GUI.join()
print("When GUI is closed this message appears")
#When GUI is closed we set finish to True, so SecondThread will be closed.
finish = True