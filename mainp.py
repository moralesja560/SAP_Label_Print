#----------------------import area

import subprocess
import os
import sys
import time, threading
from tkinter import *
from tkinter import messagebox
from functools import partial
import tkinter as tk
from matplotlib.pyplot import text
import pyautogui
import serial
import sys
import glob
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote
from urllib.request import Request, urlopen
import json
import requests
import cv2
import pytesseract
#---------------------------------...


############progress check
######-------ENDED TASKS
#Integrar GR como punto de entrada
	#excelente funcionamiento
#Integrar la búsqueda de PI para reducción del tiempo del script
	#excelente funcionamiento
#Descartar cadenas de texto repetidas o corruptas
	#Ya no pasan Shop Orders que no sean de  7 digitos
	#tampoco pasan cadenas que sean distintas de 18 caracteres
#Prevención de envíos masivos de etiquetas
	#No le afecta al programa si presiona el botón manual muchas veces.
#Procedimiento de retorno para todas las funciones que desembocan en error
#Optimización de la consola para mantener el enfoque en el debugging
#Mejores y mas humanos textos de error.

######## ------------ PENDING TASKS
#Intentar algo para leer el error en Python
	#Ya se lee correctamente, pero falta pegarle a la limpieza y envío de la información
#Seleccionar las notificaciones para recibir las mas importantes.
#Subir el log a pastebin
#Integrar un metodo de centralización para evitar el bug de la doble shop order.
#Killswitch para notificaciones
#continuar en pruebas.
#optimización en el análisis de Shop Order


#####--------RECOMMENDATIONS
#Utiliza mejor los prints para señalar info importante.
# comentarios en todos lados..
#optimización de procesos.
#mensajes de informacion y error en todos lados

######-----------------Sensitive Data Load-----------------####
load_dotenv()
token_Tel = os.getenv('TOK_EN_BOT')
Grupo_SAP_Label = os.getenv('JORGE_MORALES')

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

def take_screenshot(type):
	now = datetime.now()
	dt_string = now.strftime("%d%m%Y-%H%M%S")
	mis_docs = My_Documents(5)
	if type == "error":
		im = pyautogui.screenshot(region=(500,350,450,190))
	else:
		im = pyautogui.screenshot(region=(0,0, 1200, 700))
	#check if folder exists
	isFile = os.path.isdir(f"{mis_docs}/scfolder")
	if isFile == False:
		os.mkdir(f"{mis_docs}/scfolder/")
	ruta_img = f"{mis_docs}/scfolder/sc-{dt_string}.png"
	im.save(ruta_img)
	return ruta_img

def read_from_img(img):
	#wait for branch merging then try to adjust screenshot area to allow tesseract to read accurately
	#check if program is installed
	file_exists2 = os.path.exists('C:/Program Files/Tesseract/tesseract.exe')
	if file_exists2 == False:
		#there's not Tesseract Installed
		write_log("nok","Tesseract no está instalado",'0','0','0')
		print("No encontré Tesseract")
		return
	# read image
	image = cv2.imread(img)
	# configurations
	config = ('-l eng --oem 1 --psm 3')
	# pytessercat
	pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract/tesseract.exe'
	text = pytesseract.image_to_string(image, config=config)
	# print text
	#text = text.split('\n')
	return text


#---------------------------------End of Auxiliary Functions-------------------------#

#--------------------------------Telegram Messaging Management----------------------#

def send_message(user_id, text,token):
	global json_respuesta
	url = f"https://api.telegram.org/{token}/sendMessage?chat_id={user_id}&text={text}"
	#resp = requests.get(url)
	#hacemos la petición
	try:
		respuesta  = urlopen(Request(url))
	except Exception as e:
		print(f"Ha ocurrido un error al enviar el mensaje: {e}")
	else:
		#recibimos la información
		cuerpo_respuesta = respuesta.read()
		# Procesamos la respuesta json
		json_respuesta = json.loads(cuerpo_respuesta.decode("utf-8"))
		print("mensaje enviado exitosamente")

   
def send_photo(user_id, image,token):
	img = open(image, 'rb')
	TOKEN = token
	CHAT_ID = user_id
	url = f'https://api.telegram.org/{TOKEN}/sendPhoto?chat_id={CHAT_ID}'
	#resp = requests.get(url)
	#hacemos la petición

	respuesta = requests.post(url, files={'photo': img})

	if '200' in str(respuesta):
		print(f"mensaje enviado exitosamente con código {respuesta}")
	else:
		print(f"Ha ocurrido un error al enviar el mensaje: {respuesta}")

#--------------------------------Telegram Messaging Management END----------------------#



###################################This is the function that actually prints the labels.

def label_print(ShopOrder,BoxType,StandardPack):
	#a protection to avoid printing empty labels
	if len(str(ShopOrder))>0:
##########area to check if app is in position.
		#check if Membrain is ready to take inputs
		inicial_btn = pyautogui.locateOnScreen(resource_path(r"images/inicial2.png"),grayscale=False, confidence=.7)
		#check if Membrain is the main screen
		inbox_btn = pyautogui.locateOnScreen(resource_path(r"images/boton1.png"),grayscale=False, confidence=.7)
		#check if ok button was left open
		error2_btn = pyautogui.locateOnScreen(resource_path(r"images/purook.png"),grayscale=False, confidence=.7)
		#check if yesno button was left open
		error3_btn = pyautogui.locateOnScreen(resource_path(r"images/purosino1.png"),grayscale=False, confidence=.7)
		#check for GR Cancel
		error7_btn = pyautogui.locateOnScreen(resource_path(r"images/GR_Cancel2.png"),grayscale=False, confidence=.7)
		ok_flag = False
		#Test every scenario to look for possible entry points.
		# test for ok_flag to avoid double_checking

		#there was a ok button left
		if error2_btn != None and ok_flag == False:
			pyautogui.press('enter')
			time.sleep(1)
			pyautogui.click(435,142)
			ok_flag = True
			#no ok button was left, try with yesno
		if error3_btn != None and ok_flag == False:
			#if button left open, click 
			pyautogui.press('tab')
			time.sleep(1)
			pyautogui.press('enter')
			#if HU was exceeded
			time.sleep(3)
			error35_btn = pyautogui.locateOnScreen(resource_path(r"images/purook.png"),grayscale=False, confidence=.7)	
			if error35_btn != None and ok_flag == False:
			#main screen after all, click on the screen
				time.sleep(4)
				pyautogui.press('enter')
				time.sleep(1)
				pyautogui.click(50,50)
				time.sleep(1)
				pyautogui.click(523,223)
				time.sleep(1)
				pyautogui.click(435,142)
			ok_flag = True
		#Yes/NO button wasn't? try with the main screen
		if inbox_btn != None and ok_flag == False:
		#if main screen was found:
			pyautogui.click(523,223)
			ok_flag = True
		#¿Still no? Maybe it was ok after all this time
		if inicial_btn != None and ok_flag == False:
		#initial orange screen detected.
			pyautogui.click(435,142)
			ok_flag = True
		#Maybe it was left in GR Cancel
		if error7_btn != None and ok_flag == False:
			#main screen then click on the screen
			time.sleep(4)
			pyautogui.press('enter')
			time.sleep(1)
			pyautogui.click(50,50)
			time.sleep(1)
			pyautogui.click(523,223)
			time.sleep(1)
			pyautogui.click(435,142)
			ok_flag = True
		#throw error if ok_flag it's false after this
		if ok_flag == False:
			ruta_foto = take_screenshot("full")
			send_message(Grupo_SAP_Label,quote(f" En {Line_ID} Intenté imprimir una etiqueta, pero no veo el Membrain. Aquí está una foto de la pantalla:"),token_Tel)
			send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
			write_log("nok","No se puede identificar el punto de entrada",ShopOrder,BoxType,StandardPack)
			run1.console.configure(text = "No se puede identificar el punto de entrada")
			return

###############This is the procedure start

		#click on the HU field
		pyautogui.click(435,142)
		time.sleep(2)
		#write the shop order but before a healthy backspace
		pyautogui.press('backspace')
		pyautogui.write(f"{ShopOrder}")
		pyautogui.press('enter')
		time.sleep(6)
		#what if the HU is wrong. 
		error4_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
		if error4_btn is not None:
			#error in HU
			ruta_foto = take_screenshot("error")
			texto_error = read_from_img(ruta_foto)
			print(texto_error)
			write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
			send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
			send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Parece que no pusieron bien la Shop Order. ¿Es {ShopOrder} una Shop Order válida?"),token_Tel)
			pyautogui.press('enter')
			time.sleep(1)
			pyautogui.click(435,142)
			time.sleep(1)
			pyautogui.press('backspace')
			write_log("nok","HU incorrecta",ShopOrder,BoxType,StandardPack)
			run1.console.configure(text = "HU incorrecta")
			return
		for i in range(0,10):
		# tries before failing
		#error5 if to detect if script is going well.				
			error5_btn = pyautogui.locateOnScreen(resource_path(r"images/embalaje.png"),grayscale=False, confidence=.7)
			print(f"Intento de encontrar el embalaje {i}: status: {error5_btn}")
			if error5_btn is not None:
				break
			time.sleep(5)
		if error5_btn == None:
			ruta_foto = take_screenshot("full")
			send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
			send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Estaba creando una etiqueta, pero el Membrain ya no respondió. ¿Se podrá intentar de nuevo?"),token_Tel)
			write_log("nok","No se encontró el embalaje",ShopOrder,BoxType,StandardPack)
			run1.console.configure(text = "No se encontró la secc de embalaje")
			pyautogui.click(50,50)
			time.sleep(1)
			pyautogui.click(523,223)
			pyautogui.press('enter')
			pyautogui.click(435,142)
			return
		#no issue, continue
		pyautogui.press('tab')
		pyautogui.press('space')
		time.sleep(2)
		#This is where i can save some time by locating the screen.
		for i in range(0,10):
			#try locating the screen 10 times
			error8_btn = pyautogui.locateOnScreen(resource_path(r"images/PI.png"),grayscale=False, confidence=.7)
			print(f"Intento de encontrar el PI {i}: status: {error5_btn}")
			if error8_btn is not None:
				break
			time.sleep(3)
		if error8_btn == None:
			ruta_foto = take_screenshot("full")
			send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
			send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Estaba creando una etiqueta, pero el Membrain ya no respondió. ¿Se podrá intentar de nuevo?"),token_Tel)
			write_log("nok","No se encontró el embalaje",ShopOrder,BoxType,StandardPack)
			run1.console.configure(text = "No se encontró la secc de embalaje")
			pyautogui.click(50,50)
			time.sleep(1)
			pyautogui.click(523,223)
			pyautogui.press('enter')
			pyautogui.click(435,142)
			return
		#print(StandardPack)
		pyautogui.write(f"{StandardPack}")
		pyautogui.press('tab')
		#numero de operario
		pyautogui.write("20010380")
		time.sleep(2)
		#puesto de trabajo
		pyautogui.press('tab')
		time.sleep(2)
		pyautogui.press('tab')
		#texto libre
		pyautogui.write("Auto Print")
		time.sleep(2)
		pyautogui.press('tab')
		time.sleep(2)
###############this enter is to store the label
		pyautogui.press('enter')
		time.sleep(7)				
		#Look for 2 scenarios: 
		#After the label input, usually a Yes/no warning appears.
		#let's look for a yes/no and an error label
		#error
		error2_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
		#yes no
		error3_btn = pyautogui.locateOnScreen(resource_path(r"images/purosino1.png"),grayscale=False, confidence=.7)
		#puro ok
		error6_btn = pyautogui.locateOnScreen(resource_path(r"images/purook.png"),grayscale=False, confidence=.7)
		#a little timer to ease the sea
		time.sleep(2)
		#a third event is missing: OK only
		if error3_btn is not None:
			#the usual Yes/No
			pyautogui.press('tab')
			time.sleep(1)
			pyautogui.press('enter')
			#What if there's an error?
			time.sleep(6)
			error35_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)	
			if error35_btn is not None:
				#write the warning and return to HU input by using boton1.png
				time.sleep(1)
				ruta_foto = take_screenshot("error")
				send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
				send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Ya terminé de ingresar la etiqueta, pero me apareció este error. Intente imprimirla de nuevo desde el touchpanel"),token_Tel)
				write_log("nok","Error al ingresar la etiqueta",ShopOrder,BoxType,StandardPack)
				time.sleep(4)
				pyautogui.press('enter')
				time.sleep(1)
				pyautogui.click(50,50)
				time.sleep(1)
				pyautogui.click(523,223)
				pyautogui.press('enter')
				pyautogui.click(435,142)
			else:
				#No error: This is the good ending.
				ruta_foto = take_screenshot("error")
				texto_error = read_from_img(ruta_foto)
				print (texto_error)
				write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
				pyautogui.press('enter')
				write_log("ok","No error",ShopOrder,BoxType,StandardPack)
				run1.console.configure(text = "Impresión Terminada: Revise Log")
		if error2_btn is not None:
			#what is there was an error after the input (e.g. network)
			#write the warning and return to HU input by using boton1.png
			time.sleep(1)
			#warning_log("Error al ingresar la etiqueta")
			ruta_foto = take_screenshot("error")
			send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
			send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Ya terminé de ingresar la etiqueta, pero me apareció este error. Intente imprimirla de nuevo desde el touchpanel"),token_Tel)
			write_log("nok","Error al ingresar la etiqueta",ShopOrder,BoxType,StandardPack)
			time.sleep(4)
			pyautogui.press('enter')
			time.sleep(1)
			pyautogui.click(50,50)
			time.sleep(1)
			pyautogui.click(523,223)
			pyautogui.press('enter')
			pyautogui.click(435,142)
		if error6_btn is not None:
			#just a simple ok
			ruta_foto = take_screenshot("error")
			texto_error = read_from_img(ruta_foto)
			print (texto_error)
			write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
			pyautogui.press('enter')
			pyautogui.click(435,142)
			write_log("ok","No error",ShopOrder,BoxType,StandardPack)
			run1.console.configure(text = "Impresión Terminada: Revise Log")
	else:
		write_log("nok","Shop Order con longitud incorrecta",ShopOrder,BoxType,StandardPack)
		return


#---------------------------------End of Main Function-------------------------------#

#/////----------------------------Reading and Writing Files--------------------------#


#This CSV is for button data. You can add a button if you modify this adequately.
import csv

with open(resource_path("images/basic_btn_data.csv")) as file:
	type(file)
	csvreader = csv.reader(file)
	header = []
	header = next(csvreader)
	header
	rows = []
	for row in csvreader:
		rows.append(row)

with open(resource_path("images/entry_btn_data.csv")) as file:
	type(file)
	csvreader = csv.reader(file)
	header = []
	header = next(csvreader)
	header
	rows2 = []
	for row in csvreader:
		rows2.append(row)

with open(resource_path(r'images/idline.txt'), 'r') as f:
	Line_ID = f.readline()

def write_log(logtype,texto,ShopOrder,BoxType,StandardPack):
	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	#print("date and time =", dt_string)	
	mis_docs = My_Documents(5)
	ruta = str(mis_docs)+ r"\registro_etiquetas.txt"
	file_exists = os.path.exists(ruta)
	if file_exists == True:
		with open(ruta, "a+") as file_object:
			# Move read cursor to the start of file.
			file_object.seek(0)
			# If file is not empty then append '\n'
			data = file_object.read(100)
			if len(data) > 0 :
				file_object.write("\n")
			# Append text at the end of file
			if logtype == 'ok':
				file_object.write(f" Etiqueta Impresa en {dt_string} con los datos {ShopOrder,BoxType,StandardPack}")
			elif logtype == 'nok':
				file_object.write(f" Hubo un error durante impresión en {dt_string}, con datos {ShopOrder,BoxType,StandardPack} y con error: {texto}")
			elif logtype == 'log':
				file_object.write(f" Registro de Información para análisis en {dt_string}, con datos {ShopOrder,BoxType,StandardPack} y con error: {texto}")
	else:
		with open(ruta,"w+") as f:
			if logtype == 'ok':
				f.write(f" Etiqueta Impresa en {dt_string} con los datos {ShopOrder,BoxType,StandardPack}")
			elif logtype == 'nok':
				f.write(f" Hubo un error durante impresión en {dt_string}, con datos {ShopOrder,BoxType,StandardPack} y con error: {texto}")
			elif logtype == 'log':
				file_object.write(f" Registro de Información para análisis en {dt_string}, con datos {ShopOrder,BoxType,StandardPack} y con error: {texto}")



#/////-----------------------End of Reading and Writing Files--------------------------#

#-----------------------------Start of tkinter classes-----------------------------#

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
		self.background_image = PhotoImage(file = resource_path("images/UI3.png"))
		label1 = Label(self.parent, image = self.background_image)
		label1.place(x = 0,y = 0)
		#general parameters for the buttons.
		h_offset = 2
		w_offset = 4
		self.fg_offset = "white"
		self.bg_offset = '#314a94'
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
			globals()[a_temp].configure(font=("Helvetica", 8, "bold"))
			globals()[a_temp].configure(text = rows[i-1][4])
			#self.selector is the function inside the main class
			globals()[a_temp].configure(command=partial(self.Selector, int(rows[i-1][5])))

			self.console = Label(self.parent,width = w_offset*15, height = h_offset)
			self.console.place(x=475,y=695)
			self.console.configure(text = "")
			self.console.configure(fg="white", bg="black", font=("Console",10))
		#call the port selector function and retrieve all available COM ports.
		portList = serial_ports()
######### Create Dropdown menus for COM options 
		#ComPort.
		dropwidth = 18
		dropfront = "white"
		dropbg = '#314a94'
		dropfont = ("Sans-serif",10)
		dropx = 405
		dropy = 351

		self.ComList = StringVar()
		self.ComList.set("Selecc Puerto")
		dropdown1 = OptionMenu(self.parent,self.ComList,*portList)
		dropdown1.place(x=int(dropx),y=int(dropy))
		dropdown1.configure( fg=dropfront, bg=dropbg, width=dropwidth, font=dropfont )

		#Speed.
		speeds = [9600,19200,38400,57600,115200]
		self.baudRate1 = StringVar()
		self.baudRate1.set("9600")
		dropdown2 = OptionMenu(self.parent,self.baudRate1,*speeds)
		dropdown2.place(x=int(dropx),y=int(dropy)+30)
		dropdown2.configure(fg=dropfront, bg=dropbg, width=dropwidth, font=dropfont)

		#Parity
		parity = [serial.PARITY_EVEN,serial.PARITY_NONE,serial.PARITY_ODD]
		self.Parity1 = StringVar()
		self.Parity1.set("N")
		dropdown3 = OptionMenu(self.parent,self.Parity1,*parity)
		dropdown3.place(x=int(dropx),y=int(dropy)+60)
		dropdown3.configure(fg=dropfront, bg=dropbg, width=dropwidth, font=dropfont)

		#stop_bits
		sbits = [serial.STOPBITS_ONE,serial.STOPBITS_ONE_POINT_FIVE,serial.STOPBITS_TWO]
		self.stopBits1 = IntVar()
		self.stopBits1.set("1")
		dropdown4 = OptionMenu(self.parent,self.stopBits1,*sbits)
		dropdown4.place(x=int(dropx),y=int(dropy)+90)
		dropdown4.configure(fg=dropfront, bg=dropbg, width=dropwidth, font=dropfont)

		#byte_size
		byte_s = [serial.EIGHTBITS,serial.FIVEBITS,serial.SIXBITS,serial.SEVENBITS]
		self.byteSize1 = IntVar()
		self.byteSize1.set("8")
		dropdown5 = OptionMenu(self.parent,self.byteSize1,*byte_s)
		dropdown5.place(x=int(dropx),y=int(dropy)+120)
		dropdown5.configure(fg=dropfront, bg=dropbg, width=dropwidth, font=dropfont)

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
					self.console.configure(text = "Se ha cerrado el puerto")
			except:
				messagebox.showinfo('Puerto no abierto','Puerto no existe o no abierto.')
				a_temp = 'Button1'
				globals()[a_temp].configure(state = "active")
				globals()[a_temp].configure(bg = self.bg_offset)
				globals()[a_temp].configure(fg = self.fg_offset)
		if num == 30:
			#button to open the management console
			temp_mis_docs = My_Documents(37)
			mis_docs = temp_mis_docs + "/devmgmt.msc"
			subprocess.run([mis_docs],shell=True)


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
		self.console.configure(text = "Conectado a: " + self.ser.portstr)
		#serial buffer cleaning
		s = ""
		#variable initialization
		ShopOrder_comp = ""
		StandardP_comp = ""
		while finish is not True:
			#monitor the buffer s to look for /n
			if self.ser.is_open == False:
				self.console.configure(text = "Se ha cerrado el puerto")
				return
			# the TRY catcher is to find if the port has been closed and react accordingly
			while '/n' not in str(s):
				try:
					s = self.ser.read(17)
				except:
					self.console.configure(text = 'Se ha cerrado el puerto exitosamente.')
					return
				#changed else for finally:
				finally:
					if finish == True:
						return
			label_data = str(s)
			#once its stored, destroy port
			self.ser.close()
			self.console.configure(text = "1.- Puerto Cerrado. Datos Recibidos: " + label_data)
			print(f"Cadena Recibida: {label_data}")
			#prevent data process if label_data is 0 characters long.
			#find the X in box.
			if label_data.find('X') == -1 or len(label_data) != 18:
				#what if the string does not have X
				self.console.configure(text = "Datos No Válidos: " + label_data)
				print(f"Se recibió esta cadena {label_data}, pero parece que no es válida")
				write_log("nok","La información no es válida",{label_data},"BOX","SP")
				label_data = ""
				s = ""
				self.console.configure(text = "Puerto Abierto: Descarte de datos inválidos")
				self.ser.open()
				continue
			else:
				x_pos=label_data.find('X')
				print("2.- X encontrada")
				#we store Shop Order data in two separate vars,  but we do not clear one,
				#no issue if it's the same data, but will send a notification if there's change.
				ShopOrder = label_data[x_pos-9:x_pos-2]
				BoxType = label_data[x_pos-2:x_pos+1]
				#Standard Pack was changed due to serial data overflow. 
				StandardPack =label_data[x_pos+1:x_pos+4]
#####-------------------------------Shop Order management. Prevent any Shop Order to be printed if it's has less than 6 characters.
			###send a message if a Shop Order is less than  characters, then clean vars, then continue.
			if len(ShopOrder) != 7 and  len(ShopOrder_comp)!=7 :
				#send a message that we cannot print a label with that info.
				send_message(Grupo_SAP_Label,quote(f"En {Line_ID}: La Shop Order debe tener 7 digitos. ¿Es {ShopOrder} una Shop Order válida?"),token_Tel)
				ShopOrder = ""
				BoxType = ""
				StandardPack = ""
				label_data = ""
				s = ""
				self.ser.open()
				print(" 2.4.- Error: No llegó bien la Shop Order.")
				run1.console.configure(text = f"Puerto Abierto: Listo para Recibir Error: Datos Incorrectos")
				continue
			elif (len(ShopOrder) != 7 or '/' in ShopOrder or "'" in ShopOrder or 'b' in ShopOrder) and  len(ShopOrder_comp)==7 : #dfd
				#Use the previous Shop Order to print the new label
					ShopOrder = ShopOrder_comp
					print(" 2.5.- Se ha enviado un warning que llego cortada la etiqueta Shop Order.")
					write_log("nok","La información llegó cortada, pero si se imprimió la etiqueta",ShopOrder,BoxType,StandardPack)
			#if the var is empty (as usual when new run, please fill it, then just compare it)
			if ShopOrder_comp == "" or ShopOrder_comp == None:
				ShopOrder_comp = label_data[2:x_pos-2]
				print(f"3.- variable shoporder_comp se llena {ShopOrder_comp}")
			#if variable is already done, then compare:
			if ShopOrder_comp == ShopOrder:
				print(f'3.- Shop Order válida y repetida: {ShopOrder}')
			else:
				send_message(Grupo_SAP_Label,quote(f'En {Line_ID}: Se ha cambiado la Shop Order: \n Shop Order Anterior: {ShopOrder_comp} \n Shop Order Nueva: {ShopOrder}'), token_Tel)
				#ShopOrder update to prevent this again.
				ShopOrder_comp = ShopOrder
###---------------SHOP ORDER MANAGEMENT END-------------------------#

####-------------Standard Pack Management ---------------------------#
			###send a message if a Shop Order is less than  characters, then clean vars, then continue.
			if StandardP_comp == "" or StandardP_comp == None:
				StandardP_comp = label_data[x_pos+1:len(label_data)-3]
				print(f"4.- se ha llenado la variable SP con los datos {StandardP_comp}")
			if len(StandardPack) != 3 and  len(StandardP_comp)!=3 :
				#send a message that we cannot print a label with that info.
				send_message(Grupo_SAP_Label,quote(f"En {Line_ID}: El Standard Pack debe tener 3 digitos. ¿Es {StandardPack} un Standard Pack válido?"),token_Tel)
				ShopOrder = ""
				BoxType = ""
				StandardPack = ""
				label_data = ""
				s = ""
				self.ser.open()
				print(f'4.1.- Error: No llegó bien el Standard Pack')
				run1.console.configure(text = f"Puerto Abierto: Listo para Recibir Error: Datos Incorrectos")
				continue
			elif (len(StandardPack) != 3 or '/' in StandardPack or "'" in StandardPack or 'b' in StandardPack) and  len(StandardP_comp)==3 :
				#Use the previous Shop Order to print the new label
					StandardPack = StandardP_comp
					print("4.2.- Se ha enviado un warning que llego cortada la etiqueta Standard Pack.")
					write_log("nok","La información llegó cortada, pero si se imprimió la etiqueta",ShopOrder,BoxType,StandardPack)
			#if the var is empty (as usual when new run, please fill it, then just compare it)

			#if variable is already done, then compare:
			if StandardP_comp == StandardPack:
				print(f'4.- SP está igual: {StandardPack}')
			else:
				send_message(Grupo_SAP_Label,quote(f'En {Line_ID}: Se ha cambiado el Standard Pack: \n SP Anterior: {StandardP_comp} \n SP Nuevo: {StandardPack}'), token_Tel)
				#ShopOrder update to prevent this again.
				StandardP_comp = StandardPack


####################Launch label printing process..
			label_print(ShopOrder,BoxType,StandardPack)
			#waiting time before restarting the process.
			run1.console.configure(text = f"Tiempo de Espera para Nueva Etiqueta: 1 mins")
			time.sleep(60)
			ShopOrder = ""
			BoxType = ""
			StandardPack = ""
			label_data = ""
			s = ""
			#Open the port again.
			self.ser.open()
			run1.console.configure(text = f"Puerto Abierto: Listo para Recibir")
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
		run1.console.configure(text = f"Proceso Terminado: Puerto Cerrado")

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
	root.mainloop() #GUI.start()
	#print("Exiting....")
	finish = True
