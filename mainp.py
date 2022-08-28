#------------------Author Info----------------------#
#			The SAP Automatic Labeling System
# Designed and developed by: Ing Jorge Alberto Morales, MBA
# Controls Engineer for Mubea Coil Springs Mexico
# JorgeAlberto.Morales@mubea.com
#---------------------------------------------------#

#----------------------import area

import subprocess
import os
import time, threading
from tkinter import *
from tkinter import messagebox
from functools import partial
import tkinter as tk
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
import pandas as pd
from sqlalchemy import create_engine
import pyodbc
from sqlalchemy.orm import sessionmaker
#---------------------------------...


############progress check
######-------ENDED TASKS V181
## branch severe_lot_bug
	# el lote se abre como un campo en lugar de ya estar diseñado.
	# obten las coordenadas de lote, clickealo y luego metes 0123456700 (0+ShopOrder+00)
	# luego click al campo de PI en lugar de tabularlo, es mas seguro.


######## ------------ PENDING TASKS for V19

## timestamp on console 

## limpieza mensual del folder scfolder y del txt log

## im alive notif.

## print cuando arranque de funcion label_print. 

## investigar porque el SQL falla a veces. activar el echo y lo dejamos unos días funcionando.

## Log de consola >> txt

## launch notification 

## branch COM open_close
## mejoras a la gestión del puerto de comunicaciones para evitar cerrar la app en caso de falla.

## branch diskette## branch diskette
# Durante el procedimiento de guardar etiqueta (enter al icono diskette) reemplaza el tabular por un locatescreen para clickear el boton

## branch: parameter_txt
	# sacar los parámetros como Line_ID, tiempos de espera y SQL_Server a un txt de configuración.

## branch incorrect_data
	# CUando llegan datos malos, llenar las variables con información anterior y mandar a imprimir.


#------------V19 preprod branch------------------#

######-----------------Sensitive Data Load-----------------####
load_dotenv()
token_Tel = os.getenv('TOK_EN_BOT')
Grupo_SAP_Label = os.getenv('SAP_LT_GROUP')
Jorge_Morales = os.getenv('JORGE_MORALES')
pyautogui.FAILSAFE = False


#####--------------------SQL Session Management--------------####
#engine = create_engine('mssql+pyodbc://scadamex:scadamex@SAL-W12E-SQL\MSSQLMEX/scadadata?driver=SQL+Server+Native+Client+11.0', echo=True)
#WINDOWS + R >>> TYPE ODBC AND FIND THE INSTALLED SQL DRIVER.
engine = create_engine('mssql+pyodbc://scadamex:scadamex@SAL-W12E-SQL\MSSQLMEX/scadadata?driver=SQL+Server', echo=False)

Session = sessionmaker(bind=engine)
session = Session()
####--------------------------------------------------------####

####----------------Time Management--------------####
now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
###---------------------------------------------####

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
		im = pyautogui.screenshot(region=(490,350,510,190)) #changed to 490 from 500
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
	processed_text = "cadena vacia"
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
	text = text.split('\n')
	for letter in text:
	#check for nonexistant HU
		if len(letter)<3:
			continue
		elif "no existe" in letter or "ya esta eliminada" in letter:
			processed_text = "HU no existente"
		elif "OF" in letter or "cerrada" in letter or "orden excedido" in letter :
			processed_text = "Shop Order con OF"
		elif "tratando" in letter:
			processed_text = "HU está siendo usada en otro lado"
		elif "HU planificada" in letter:
			processed_text = "Bug de misma Shop Order"
		elif "ninguna orden para" in letter:
			processed_text = "Configuración del Membrain equivocada"
		elif "HTTP" in letter or "RTC" in letter:
			processed_text = "No respondio el SAP"
		elif "Entrada de mercancias" in letter:
			HU_step1 = letter.find("HU")
			print(f"Proceso terminó normal: {letter[HU_step1:HU_step1+12]}")
			processed_text = f"Proceso termina normal {letter[HU_step1:HU_step1+12]}"
		elif "eliminada" in letter:
			processed_text = "HU ya fue eliminada"
		elif "maestro de personal" in letter:
			processed_text = "Numero de empleado no existe"
		elif "embalaje planificada" in letter:
			processed_text = "no hay embalaje planeado"
		else:
			processed_text = f"El error tenía esto {letter}, pero no pude detectar caracteres"

	return processed_text


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

#-----------------------------AUXILIARY OPTIMIZATION FUNCTIONS------------------------#
def return_to_main():
	time.sleep(1)
	pyautogui.click(435,142)

def main_menu():
	pyautogui.click(50,50)
	time.sleep(1)
	pyautogui.click(523,223)
	time.sleep(1)
	pyautogui.click(435,142)



###################################This is the function that actually prints the labels.

def label_print(ShopOrder,BoxType,StandardPack):
	global return_codename
	#a protection to avoid printing empty labels
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
	#check for an error screen
	error10_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
	ok_flag = False
	#Test every scenario to look for possible entry points.
	# test for ok_flag to avoid double_checking
	#there was a ok button left
	if error2_btn != None and ok_flag == False:
		pyautogui.press('enter')
		return_to_main()
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
			main_menu()
			return_to_main()
		ok_flag = True
	#Yes/NO button wasn't? try with the main screen
	if inbox_btn != None and ok_flag == False:
	#if main screen was found:
		pyautogui.click(523,223)
		ok_flag = True
	#¿Still no? Maybe it was ok after all this time
	if inicial_btn != None and ok_flag == False:
	#initial orange screen detected.
		return_to_main()
		ok_flag = True
	#Maybe it was left in GR Cancel
	if error7_btn != None and ok_flag == False:
		#main screen then click on the screen
		time.sleep(4)
		pyautogui.press('enter')
		main_menu()
		return_to_main()
		ok_flag = True
	if error10_btn != None and ok_flag == False:
		#somebody left an error message
		#########################
		pyautogui.press('enter')
		main_menu()
		return_to_main()

	#throw error if ok_flag it's false after this
	if ok_flag == False:
		ruta_foto = take_screenshot("full")
		send_message(Grupo_SAP_Label,quote(f" En {Line_ID} Intenté imprimir una etiqueta pero no veo el Membrain, intentaré de nuevo"),token_Tel)
		send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
		write_log("nok","No se puede identificar el punto de entrada",ShopOrder,BoxType,StandardPack)
		run1.console.configure(text = "No se puede identificar el punto de entrada")
		#Add a 1 to try to print again
		return_codename = 1
		return return_codename

##############This is the procedure start
		#click on the HU field
	pyautogui.click(523,223)
	return_to_main()
	time.sleep(2)
	#write the shop order but before a healthy backspace
	pyautogui.press('backspace')
	pyautogui.write(f"{ShopOrder}")
	print(f"escribí {ShopOrder} en el campo ShopOrder")
	pyautogui.press('enter')
	time.sleep(6)
	#what if the HU is wrong. 
	error4_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
	if error4_btn is not None:
		#error in HU
		ruta_foto = take_screenshot("error")
		texto_error = read_from_img(ruta_foto)
		write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
		if "Membrain equivocada" in texto_error:
			pyautogui.press('enter')
			return_to_main()
			time.sleep(1)
			pyautogui.press('tab')
			time.sleep(1)
			pyautogui.press('tab')
			time.sleep(1)
			pyautogui.press('space')
			return_to_main()
			pyautogui.press('backspace')
			return_codename = 1
			return return_codename
		elif "HU no existente" in texto_error:			
			send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
			send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Parece que no pusieron bien la Shop Order. ¿Es {ShopOrder} una Shop Order válida?"),token_Tel)
			pyautogui.press('enter')
			return_to_main()
			time.sleep(1)
			pyautogui.press('backspace')
			write_log("nok","HU incorrecta",ShopOrder,BoxType,StandardPack)
			run1.console.configure(text = "HU incorrecta")
			return_codename = 1
			return return_codename
	for i in range(0,15):
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
		main_menu()
		pyautogui.press('enter')
		return_to_main()
		return_codename = 1
		return return_codename
	#no issue, continue
	pyautogui.press('tab')
	pyautogui.press('space')
	#after this space may errors can arise, including the HU is already in use.
	time.sleep(2)
	#This is where i can save some time by locating the screen.
	for i in range(0,20):
		#try locating the screen 10 times
		error8_btn = pyautogui.locateOnScreen(resource_path(r"images/PI.png"),grayscale=False, confidence=.7)
		error10_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
		print(f"Intento de encontrar el PI {i}: status: {error5_btn}")
		print(f"Intento de encontrar algun error {i}: status: {error10_btn}")
		if error8_btn is not None or error10_btn is not None:
			break
		time.sleep(3)
	# Si no aparece la seccion 3 de la etiqueta, haz lo siguiente
	# puede deberse a internet o a errores en la HU		
	if error8_btn == None:
		ruta_foto = take_screenshot("full")
		send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
		send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Error de Standard Pack: Intentaré de nuevo."),token_Tel)
		write_log("nok","No se encontró el PI",ShopOrder,BoxType,StandardPack)
		run1.console.configure(text = "No se encontró la secc de PI")
		main_menu()
		return_codename = 1
		return return_codename
	#si el error 10 no está vacio (=None), entonces encontró un error
	if error10_btn is not None:
		#encuentra el error y leelo
		ruta_foto = take_screenshot("error")
		texto_error = read_from_img(ruta_foto)
		write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
		if  texto_error == "no hay embalaje planeado" or texto_error == "Bug de misma Shop Order":
			main_menu()
			return_codename = 1
			return return_codename
	#print(StandardPack)
	# Integrar el error de Lote
	pyautogui.click(747, 342)
	time.sleep(1)
	pyautogui.write(f"0{ShopOrder}00")
	time.sleep(1)
	#Click en el PI
	pyautogui.click(451, 500)
	time.sleep(1)
	pyautogui.write(f"{StandardPack}")
	pyautogui.press('tab')
	#numero de operario
	pyautogui.write("20010380")
	time.sleep(1)
	#puesto de trabajo
	pyautogui.press('tab')
	time.sleep(1)
	pyautogui.press('tab')
	#texto libre
	pyautogui.write("Auto Print")
	time.sleep(1)
	pyautogui.press('tab')
	time.sleep(1)
##############---------------THIS ENTER IS TO STORE THE LABEL.
	pyautogui.press('enter')
	time.sleep(2)
###########################################
	#Look for 2 scenarios: 
	#After the label input, usually a Yes/no warning appears.
	#let's look for a yes/no and an error label
	#error
	for i in range(0,20):
		#error
		error2_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
		#yes no
		error3_btn = pyautogui.locateOnScreen(resource_path(r"images/purosino1.png"),grayscale=False, confidence=.7)
		#puro ok
		error6_btn = pyautogui.locateOnScreen(resource_path(r"images/purook.png"),grayscale=False, confidence=.7)
		if error2_btn is not None or error3_btn is not None or error6_btn is not None:
			break
		else:
			time.sleep(5)
		#YES/NO 
	#This error3_btn appears when there is a warning that says " x pieces to fulfill the order"
	#This is not relevant to read, but a necesary step.
	if error3_btn is not None:
		pyautogui.press('tab')
		time.sleep(1)
		pyautogui.press('enter')
		#What if there's an error? 
		#check for error and for the label correct ending
		for i in range(0,20):
			error35_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
			error9_btn = pyautogui.locateOnScreen(resource_path(r"images/purook.png"),grayscale=False, confidence=.7)
			if error35_btn is not None or error6_btn is not None :
				break
			else:
				time.sleep(2)
		if error35_btn is not None:
			#write the warning and return to HU input by using boton1.png
			time.sleep(1)
			ruta_foto = take_screenshot("error")
			texto_error = read_from_img(ruta_foto)
			print (texto_error)
			#####This area is to select what the error text will do. 
				#What to do if there's an OF error (overfill)
				#What to do if there's an HU in use error?
			send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
			if texto_error == "Shop Order con OF":
				return_codename = 0
				send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Ya se llenó la Shop Order, por favor cambiar"),token_Tel)
			elif texto_error == "HU está siendo usada en otro lado" or texto_error == "Bug de misma Shop Order":
				return_codename = 1
				send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: La Hu ya esta siendo utilizada en otro lado"),token_Tel)
			else:
				return_codename = 0
				send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Ya terminé de ingresar la etiqueta, pero me apareció este error. Intente imprimirla de nuevo desde el touchpanel"),token_Tel)

			write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
			time.sleep(4)
			pyautogui.press('enter')
			time.sleep(1)
			main_menu()
			return return_codename
		if error9_btn is not None:
#################No error after a yes/no message: This is the good ending 1.
			ruta_foto = take_screenshot("error")
			texto_error = read_from_img(ruta_foto)
			print (texto_error)
			write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
			pyautogui.press('enter')
			write_log("ok","No error",ShopOrder,BoxType,StandardPack)
			run1.console.configure(text = "Impresión Terminada: Revise Log")
			return_codename = 0
			return return_codename
	
	#This error differs from error35 because the error triggers immediately after pressing enter.
	#what if there was an error after the input (e.g. network, Shop Order Overfill)
	#write the warning and return to HU input by using boton1.png
	if error2_btn is not None:
		time.sleep(1)
		ruta_foto = take_screenshot("error")
		texto_error = read_from_img(ruta_foto)
		print(texto_error)
		send_photo(Grupo_SAP_Label,ruta_foto,token_Tel)
		if texto_error == "Shop Order con OF":
			return_codename = 0
			send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Ya se llenó la Shop Order, por favor cambiar"),token_Tel)
		elif texto_error == "HU está siendo usada en otro lado" or texto_error == "Bug de misma Shop Order":
			return_codename = 1
			send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: La HU ya está siendo utilizada en otro lado"),token_Tel)
		else:
			return_codename = 0
			send_message(Grupo_SAP_Label,quote(f" En {Line_ID}: Ya terminé de ingresar la etiqueta, pero me apareció este error. Intente imprimirla de nuevo"),token_Tel)
		
		write_log("log",texto_error,ShopOrder,BoxType,StandardPack)		
		write_log("nok","Error al ingresar la etiqueta",ShopOrder,BoxType,StandardPack)

		time.sleep(4)
		pyautogui.press('enter')
		time.sleep(1)
		main_menu()
		if  texto_error == "no hay embalaje planeado" or texto_error == "Bug de misma Shop Order":
			main_menu()
			return_codename = 1
			return return_codename
		else:
			return_codename = 0
			return return_codename
	if error6_btn is not None:
		#Good ending 2: take note of the HU
		ruta_foto = take_screenshot("error")
		texto_error = read_from_img(ruta_foto)
		write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
		pyautogui.press('enter')
		return_to_main()
		write_log("ok","No error",ShopOrder,BoxType,StandardPack)
		run1.console.configure(text = "Impresión Terminada: Revise Log")
		return_codename = 0
		return return_codename

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

#Pandas DataFrame dictionaries

pd_dict = {'timestamp' : ['dummy'], 'logtype' : ['dummy'],	'texto' : ['dummy'], 'Shop Order' : ['dummy'], 'BoxType' : ['dummy'], 'SP' : ['dummy']}


def write_log(logtype,texto,ShopOrder,BoxType,StandardPack):
	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	#print("date and time =", dt_string)	
	mis_docs = My_Documents(5)
	ruta = str(mis_docs)+ r"\registro_etiquetas.txt"
	pd_ruta = str(mis_docs)+ r"\registro_etiquetas_df.csv"
	file_exists = os.path.exists(ruta)
	pd_file_exists = os.path.exists(pd_ruta)
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
				file_object.write(f" Registro de Información para análisis en {dt_string}, con datos {ShopOrder,BoxType,StandardPack}: {texto}")
	else:
		with open(ruta,"w+") as f:
			if logtype == 'ok':
				f.write(f" Etiqueta Impresa en {dt_string} con los datos {ShopOrder,BoxType,StandardPack}")
			elif logtype == 'nok':
				f.write(f" Hubo un error durante impresión en {dt_string}, con datos {ShopOrder,BoxType,StandardPack} y con error: {texto}")
			elif logtype == 'log':
				f.write(f" Registro de Información para análisis en {dt_string}, con datos {ShopOrder,BoxType,StandardPack}: {texto}")

	#check if pandas DataFrame exists to load the stuff or to create with dummy data.
	if pd_file_exists:
		pd_log = pd.read_csv(pd_ruta)
	else:
		pd_log = pd.DataFrame(pd_dict)

	new_row = {'timestamp' : [dt_string], 'logtype' : [logtype], 'texto' : [texto], 'Shop Order' : [ShopOrder], 'BoxType' : [BoxType], 'SP' : [StandardPack]}
	new_row_pd = pd.DataFrame(new_row)
	try:
		new_row_pd.to_sql(f'Temp1_SAPLabel_{Line_ID}', con=engine, if_exists='append',index=False)
	except:
		print("no pude subir la info a sql")
	else: 
		print("SQL exitoso")
	pd_concat = pd.concat([pd_log,new_row_pd])
	#store the info
	pd_concat.to_csv(pd_ruta,index=False)



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
		
		#comboboxes data
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
		speeds = ['9600','19200','38400','57600','115200']
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
					#SecondThread = Process()
					SecondThread.stop()
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
			try:
				#SecondThread.stop()
				finish = True
			except:
				pass
			
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
			self.console.configure(text = " Puerto Cerrado. Datos Recibidos: " + label_data)
			print(f"1.- Cadena Recibida: {label_data}")
			#prevent data process if label_data is 0 characters long.
			#find the X in box.
			if label_data.find('X') == -1 or len(label_data) != 18:
				#what if the string does not have X
				self.console.configure(text = "Datos No Válidos: " + label_data)
				print(f"Se recibió esta cadena {label_data}, pero parece que no es válida")
				write_log("nok","La informacion no es valida",label_data,"BOX","0")
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
				print(f'4.- SP se ha cambiado por un Standard Pack válido: {StandardPack}')
				StandardP_comp = StandardPack


####################-----THE LABEL PRINTING PROCESS-----#
			nuevo_intento = label_print(ShopOrder,BoxType,StandardPack)
			if nuevo_intento == 1:
				print("se intenta de nuevo la etiqueta")
				nuevo_intento = label_print(ShopOrder,BoxType,StandardPack)
			#waiting time before restarting the process.
			print("5.Tiempo de Espera para Nueva Etiqueta: 1 mins")
			run1.console.configure(text = f"Tiempo de Espera para Nueva Etiqueta: 30s")
			time.sleep(30)
			print("6.- Limpieza de variables")
			ShopOrder = ""
			BoxType = ""
			StandardPack = ""
			label_data = ""
			s = ""
			#Open the port again.
			self.ser.open()
			print(f"7.- Reapertura de puerto. timestamp: {dt_string}")
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
		#V182 corrected bug: app crash when GUI is closed and COM is connected
		#run1.console.configure(text = f"Proceso Terminado: Puerto Cerrado")

		time.sleep(3)
	
	def stop(self):
		self._stop_event.set()
		print("Thread Stopped")


if __name__ == '__main__':
	send_message(Jorge_Morales,quote(f'Arranque de software {Line_ID}'), token_Tel)
	#SIGTERM signal
	finish = False
	#tkinter class assign
	root = tk.Tk()
## How to start a new thread? 
	# Assign a name and pass a few variables to it.
	# First thread 
	run1 = Passwordchecker(root)
	#Second thread handles COM Port
	SecondThread = Process()
	root.mainloop() #GUI.start()
	#print("Exiting....")
	finish = True
