#----------------------import area
import os
import sys
import time, threading
from tkinter import *
from tkinter import messagebox
from functools import partial
import tkinter as tk
import pyautogui
import serial
import sys
import glob
#---------------------------------


#progress check
#hay que buscar una forma de que se arranque el serial con el botón para setear el puerto COM
#tambien hay que buscar una forma de sacar los prints a una consola en la GUI
#viiglar que todo cierre bien y empezar a compilar
#empezar a probar en producción para ajustar el pyautogui



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

def label_print(ShopOrder,BoxType,StandardPack):
	if len(str(ShopOrder))>0:
		pyautogui.hotkey('win','r')
		pyautogui.write('chrome.exe')
		pyautogui.press('enter')
		time.sleep(5)
		pyautogui.write(f"{ShopOrder,BoxType,StandardPack}")


#---------------------------------End of Auxiliary Functions-------------------------#


#/////----------------------------Reading and Writing Files--------------------------#


#This CSV is for button data. You can add a button if you modify this adequately.
import os
import csv
file = open(resource_path("images/basic_btn_data.csv"))
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
class Passwordchecker(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.initialize_user_interface()

	def initialize_user_interface(self):

		#self.parent.geometry("200x200")
		self.parent.geometry("1024x768")
		self.parent.protocol("WM_DELETE_WINDOW", self.quit)
		self.parent.title("Mubea de Mexico - Interfaz para impresión de etiquetas.")
		self.entry=tk.Entry(self.parent)
		self.entry.pack()
		self.background_image = PhotoImage(file = resource_path("images/UI.png"))
		label1 = Label(self.parent, image = self.background_image)
		label1.place(x = 0,y = 0)
		self.l = Label(self.parent)
		self.l.pack()	
		h_offset = 2
		w_offset = 4
		fg_offset = "white"
		bg_offset = '#3d85c5'
######Button declaration area
		for i in range(len(rows)):
		#process the first button
			a_temp = rows[i-1][1]
			globals()[a_temp] = Button(self.parent, width = w_offset, height = h_offset)
			globals()[a_temp].configure(width = int(rows[i-1][6]))
			globals()[a_temp].configure(height = int(rows[i-1][7]))
			globals()[a_temp].place(x =int(rows[i-1][2]),y=int(rows[i-1][3]))
			globals()[a_temp].configure(bg = bg_offset)
			globals()[a_temp].configure(fg = fg_offset)
			globals()[a_temp].configure(font=("Helvetica", 10, "bold"))
			globals()[a_temp].configure(text = rows[i-1][4])
			globals()[a_temp].configure(command=partial(self.Selector, int(rows[i-1][5])))
		self.comList = Listbox(self.parent, width=12, height=8)
		self.comList.place(x =418,y=620)
		portList = serial_ports()
		for seriales in portList:
			self.comList.insert(0,seriales)

	def Selector(self,num):
		print(num)
		global ComPort
		if num == 45:
			for i in self.comList.curselection():
				print(self.comList.get(i))
				ComPort = self.comList.get(i)
				print((ComPort))
			if "COM" in ComPort:
				SecondThread.start()
				for i in range(0,1):
			#process the first button
					a_temp = 'Button9'
					globals()[a_temp].configure(state = "disabled")
					globals()[a_temp].configure(fg = "gray")


	def quit(self):
		if messagebox.askyesno('App','Are you sure you want to quit?'):
            #In order to use quit function, mainWindow MUST BE an attribute of Interface. 
			self.parent.destroy()
			self.parent.quit()

	def method1(self,ComPort): 
		#here you can put something to run as second background, do not forget to uncomment #GUI.method1()
		ser = serial.Serial(
				port=ComPort,\
				baudrate=9600,\
				parity=serial.PARITY_NONE,\
				stopbits=serial.STOPBITS_ONE,\
				bytesize=serial.EIGHTBITS,\
				timeout=1)
		print("connected to: " + ser.portstr)
		s = ""
		while finish is not True:
			while '/n' not in str(s):
				s = ser.read(40)
				if finish == True:
					break
			label_data = str(s)[2:-3]
			if finish == False and len(label_data)>0:
				print(len(label_data))
				print(f"Shop Order is {label_data[0:6]} and type {label_data[6:9]} and standard pack {label_data[9:12]}  ")
				ShopOrder = label_data[0:6]
				BoxType = label_data[6:9]
				StandardPack =label_data[9:12]
				label_print(ShopOrder,BoxType,StandardPack)
				s = ""
			else:
				print(f"port closed or error {ComPort}")
				break


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
            print("Proceso infinito")
			#do not start serial until com info is selected.
            run1.method1(ComPort)
            time.sleep(3)


if __name__ == '__main__':
	finish = False
	root = tk.Tk()
	SecondThread = Process()
	run1 = Passwordchecker(root)
	#root.after(50, SecondThread.start)
	root.mainloop() #GUI.start()
	print("Exiting....")
	finish = True
