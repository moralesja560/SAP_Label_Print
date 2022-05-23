from importlib.metadata import entry_points
import os
import sys
import time, threading
from tkinter import *
from tkinter import messagebox
import tkinter as tk
import sys
from functools import partial

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class Passwordchecker(tk.Frame):
	#needs info
	def __init__(self, parent):
	#tk.frame starts and calls the initialize user interface
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.initialize_user_interface()

	def Selector1(self):
		self.c_temp = PhotoImage(file = resource_path("images/SAP2.png"))
		self.label1.configure(image = self.c_temp)
		pass
	#first function inside the class: GUI initializing
	#this is where GUI initial configuration takes place.
	def initialize_user_interface(self):
		#define the GUI size in px (depends on end-user screen size)
		self.parent.geometry("1440x900")
		#protocol to correctly close GUI
		self.parent.protocol("WM_DELETE_WINDOW", self.quit)
		self.parent.title("Membrain PAS")
		# a label that contains the background image
		self.background_image = PhotoImage(file = resource_path("images/SAP1.png"))
		self.label1 = Label(self.parent, image = self.background_image)
		self.label1.place(x = 0,y = 0)
		#general parameters for the buttons.
		h_offset = 2
		w_offset = 4
		self.fg_offset = "white"
		self.bg_offset = '#3d85c5'
		self.caja = Entry(self.parent,width = w_offset)
		self.caja.bind('<Return>',self.Selector1)
		self.caja.place(x =int(377),y=int(128))

##########Selector is the function that commands buttons actions




	def quit(self):
		if messagebox.askyesno('Salida','¿Seguro que quiere salir?'):
            #In order to use quit function, mainWindow MUST BE an attribute of Interface. 
			self.parent.destroy()
			self.parent.quit()

	def method1(self): 
		#This is the area where the second thread lives.
		print("hi")
		
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
		run1.method1()
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