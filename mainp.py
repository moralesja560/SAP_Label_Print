#----------------------import area
from ast import Compare
import os
import sys
import time, threading
from tkinter import *
from tkinter import messagebox
from functools import partial
import tkinter as tk
from unittest import expectedFailure
from matplotlib.pyplot import text
import pyautogui
import serial
import sys
import glob
#---------------------------------...


############progress check
######-------TASKS
####-----production run to test pyautogui.
####----put in PLC some characters to better recognize parameters sent over serial
### sistema de registro en un TXT


#####--------RECOMMENDATIONS
#Utiliza mejor los prints para señalar info importante.
# comentarios en todos lados..
#optimización de procesos.
#mensajes de informacion y error en todos lados



#---------------------------------------Auxiliary Functions-------------------------#

#This function sets the absolute path for the app to access its resources
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def My_Documents(location):
	import ctypes.wintypes
		#####-----This section discovers My Documents default path --------
		#### loop the "location" variable to find many paths, including AppData and ProgramFiles
	CSIDL_PERSONAL = location       # My Documents
	SHGFP_TYPE_CURRENT = 0   # Get current, not default value
	buf= ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
	ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
	#####-------- please use buf.value to store the data in a variable ------- #####
	#add the text filename at the end of the path
	temp_docs = buf.value
	return temp_docs

#This functions returns a list of available serial ports.
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

###################################This is the function that actually prints the labels.

def label_print(ShopOrder,BoxType,StandardPack):
	#a protection to avoid printing empty labels
	if len(str(ShopOrder))>0:
		#pyautogui.hotkey('win','r')
		#pyautogui.write('chrome.exe')
		#pyautogui.press('enter')
		#time.sleep(5)
		#pyautogui.write(f"{ShopOrder,BoxType,StandardPack}")
		#run1 es la puerta de acceso a todos los widgets en el GUI
		#bring
		
		
		
		
		run1.console.configure(text = "Impresión Terminada")
		


#---------------------------------End of Auxiliary Functions-------------------------#


#/////----------------------------Reading and Writing Files--------------------------#


#This CSV is for button data. You can add a button if you modify this adequately.
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

file = open(resource_path("images/entry_btn_data.csv"))
type(file)
csvreader = csv.reader(file)
header = []
header = next(csvreader)
header
rows2 = []
for row in csvreader:
	rows2.append(row)

file.close()


#/////-----------------------End of Reading and Writing Files--------------------------#

#-----------------------------Start of tkinter classes-----------------------------#

#This stuff is actually difficult to understand.

#This class PasswordChecker stores the necessary data to run a tkinter gui.
class Passwordchecker(tk.Frame):
	#needs info
	def __init__(self, parent):
	#tk.frame starts and calls the initialize user interface
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.initialize_user_interface()

	#first function inside the class: GUI initializing
	#this is where GUI initial configuration takes place.
	def initialize_user_interface(self):
		#define the GUI size in px (depends on end-user screen size)
		self.parent.geometry("1024x768")
		#protocol to correctly close GUI
		self.parent.protocol("WM_DELETE_WINDOW", self.quit)
		self.parent.title("Mubea de Mexico - Interfaz para impresión de etiquetas.")
		# a label that contains the background image
		self.background_image = PhotoImage(file = resource_path("images/UI.png"))
		label1 = Label(self.parent, image = self.background_image)
		label1.place(x = 0,y = 0)
		#general parameters for the buttons.
		h_offset = 2
		w_offset = 4
		self.fg_offset = "white"
		self.bg_offset = '#3d85c5'
######Button declaration area
		for i in range(len(rows)):
		#process the first button
			a_temp = rows[i-1][1]
			globals()[a_temp] = Button(self.parent, width = w_offset, height = h_offset)
			globals()[a_temp].configure(width = int(rows[i-1][6]))
			globals()[a_temp].configure(height = int(rows[i-1][7]))
			globals()[a_temp].place(x =int(rows[i-1][2]),y=int(rows[i-1][3]))
			globals()[a_temp].configure(bg = self.bg_offset)
			globals()[a_temp].configure(fg = self.fg_offset)
			globals()[a_temp].configure(font=("Helvetica", 10, "bold"))
			globals()[a_temp].configure(text = rows[i-1][4])
			#self.selector is the function inside the main class
			globals()[a_temp].configure(command=partial(self.Selector, int(rows[i-1][5])))

			self.console = Label(self.parent,width = w_offset*8, height = h_offset)
			self.console.place(x=750,y=590)
			self.console.configure(text = "")
			self.console.configure(fg="white", bg="black", font=("Console",10))


		#call the port selector function and retrieve all available COM ports.
		portList = serial_ports()

######### Create Dropdown menus for COM options 
		#ComPort.
		self.ComList = StringVar()
		self.ComList.set("Elige Puerto")
		dropdown1 = OptionMenu(self.parent,self.ComList,*portList)
		dropdown1.place(x=418,y=590)
		dropdown1.configure(width=14)

		#Speed.
		speeds = [9600,19200,38400,57600,115200]
		self.baudRate1 = StringVar()
		self.baudRate1.set("Elige Baudios")
		dropdown2 = OptionMenu(self.parent,self.baudRate1,*speeds)
		dropdown2.place(x=418,y=620)
		dropdown2.configure(width=14)

		#Parity
		parity = [serial.PARITY_EVEN,serial.PARITY_NONE,serial.PARITY_ODD]
		self.Parity1 = StringVar()
		self.Parity1.set("Elige Paridad")
		dropdown3 = OptionMenu(self.parent,self.Parity1,*parity)
		dropdown3.place(x=418,y=650)
		dropdown3.configure(width=14)

		#stop_bits
		sbits = [serial.STOPBITS_ONE,serial.STOPBITS_ONE_POINT_FIVE,serial.STOPBITS_TWO]
		self.stopBits1 = IntVar()
		self.stopBits1.set("Elige Stop Bits")
		dropdown4 = OptionMenu(self.parent,self.stopBits1,*sbits)
		dropdown4.place(x=418,y=680)
		dropdown4.configure(width=14)

		#byte_size
		byte_s = [serial.EIGHTBITS,serial.FIVEBITS,serial.SIXBITS,serial.SEVENBITS]
		self.byteSize1 = IntVar()
		self.byteSize1.set("Elige Bytsize")
		dropdown5 = OptionMenu(self.parent,self.byteSize1,*byte_s)
		dropdown5.place(x=418,y=710)
		dropdown5.configure(width=14)

##########Selector is the function that commands buttons actions
	def Selector(self,num):
		global ComPort
		global baud_Rate
		global Parity_data
		global stop_bits
		global byte_size

		#go to def run() in thread 2 and config it to pass these variables to the method1 second thread.
		
		#### area to check if the info coming from the optionmenu is valid and all the option menus were opened and selected.
			
		#button to Open COM
		if num == 10:
			#Variable declaration starts here
			try:
				ComPort = self.ComList.get()
				baud_Rate = self.baudRate1.get()
				Parity_data = self.Parity1.get()
				stop_bits = self.stopBits1.get()
				byte_size = self.byteSize1.get()
			except:
				messagebox.showinfo('Error en Parámetros','Revise los parámetros del puerto')
			else:			
			#### area to check if the info coming from the optionmenu is valid and all the option menus were opened and selected.
				if len(ComPort)>5:
					messagebox.showinfo('Error en Parámetros','Revise los parámetros del puerto')
				else:
				#if "COM" in ComPort:
					try:
						#Try to start the Serial Process Thread
						SecondThread.start()
					except:
						#It is well known that a finished process cannot be restarted, so a new process is started
						SecondThread = Process()
						SecondThread.start()
					finally:
					#disable button 
						a_temp = 'Button1'
						globals()[a_temp].configure(state = "disabled")
			#else:
				# A warning that no port is selected.
			#	messagebox.showinfo('Puerto no seleccionado','Click en la lista para seleccionar un puerto COM')
		#button to close COM
		if num == 20:
			# When button "Close Port" is clicked but the thread is not alive, an error occurs.
			try:
				# if the serial port is open, close it and reenable the process.
				if self.ser.is_open:
					self.ser.close()
					a_temp = 'Button1'
					globals()[a_temp].configure(state = "active")
					globals()[a_temp].configure(bg = self.bg_offset)
					globals()[a_temp].configure(fg = self.fg_offset)
				else:
					messagebox.showinfo('Puerto no abierto','Aún no se ha abierto el puerto')
			except:
				messagebox.showinfo('Puerto no abierto','Puerto no existe o no abierto.')
				a_temp = 'Button1'
				globals()[a_temp].configure(state = "active")
				globals()[a_temp].configure(bg = self.bg_offset)
				globals()[a_temp].configure(fg = self.fg_offset)

	def quit(self):
		if messagebox.askyesno('Salida','¿Seguro que quiere salir?'):
            #In order to use quit function, mainWindow MUST BE an attribute of Interface. 
			self.parent.destroy()
			self.parent.quit()

	def method1(self,ComPort,baudRate,Parity_data,stop_bits,byte_size): 
		#This is the area where the second thread lives.
		self.ser = serial.Serial(
				port=ComPort,\
				baudrate=baudRate,\
				parity=Parity_data,\
				stopbits=stop_bits,\
				bytesize=byte_size,\
				timeout=1)
		#A notice that the COM has been opened
		#print("connected to: " + self.ser.portstr)
		self.console.configure(text = "Conectado a: " + self.ser.portstr)
		#serial buffer cleaning
		s = ""

		while finish is not True and self.ser.is_open == True:
			#monitor the buffer s to look for /n
			# the TRY catcher is to find if the port has been closed and react accordingly
			while '/n' not in str(s):
				try:
					s = self.ser.read(40)
				except:
					#messagebox.showinfo('Puerto no abierto','Se ha cerrado el puerto exitosamente.')
					self.console.configure(text = 'Se ha cerrado el puerto exitosamente.')
					break
				#changed else for finally:
				finally:
					pass
				if finish == True:
					break
			
##############----------------This is the data processing area



			#remove the firt two characters 'b and the last characters /n
			label_data = str(s)[2:-3]
			self.console.configure(text = "Datos Recibidos:" + label_data)
			#prevent data process if label_data is 0 characters long.
			if finish == False and len(label_data)>0:
				#print(f"Shop Order is {label_data[0:6]} and type {label_data[6:9]} and standard pack {label_data[9:12]}  ")
				ShopOrder = label_data[0:6]
				BoxType = label_data[6:9]
				StandardPack =label_data[9:12]
				#Launch label printing process..
				label_print(ShopOrder,BoxType,StandardPack)
				#self.console.configure(text = "Impresión Terminada")
				s = ""
			else:
				self.console.configure(text = f"Puerto Cerrado o Error en {ComPort}")
				break


#################Threading area 
class Process(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.attrib2 = "Attrib from Process1 class"

class Process(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.attrib2 = "Attrib from Process2 class"
		self._stop_event = threading.Event()

	def run(self):
		global finish
		#while not finish:
			#do not start serial until com info is selected.
		run1.method1(ComPort,baud_Rate,Parity_data,stop_bits,byte_size)
		time.sleep(3)
	
	def stop(self):
		self._stop_event.set()
		print("Thread Stopped")

#stuff that 
if __name__ == '__main__':
	finish = False
	root = tk.Tk()
	SecondThread = Process()
	run1 = Passwordchecker(root)
	#root.after(50, SecondThread.start)
	root.mainloop() #GUI.start()
	#print("Exiting....")
	finish = True
