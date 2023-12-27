import argparse
from queue import Queue
from threading import Thread
from datetime import datetime
from dotenv import load_dotenv
from urllib.request import Request, urlopen
import json
from urllib.parse import quote
import pyads
import sys
import time
import pandas as pd
import os
from tkinter import *
from tkinter import messagebox
from functools import partial
import tkinter as tk
import pyautogui
import sys
import cv2
import pytesseract
import csv
from random import randrange

######-----------------Sensitive Data Load-----------------####
load_dotenv()
token_Tel = os.getenv('TOK_EN_BOT')
Jorge_Morales = os.getenv('JORGE_MORALES')
pyautogui.FAILSAFE = False


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

#-----------------Telegram Management Area------------------#

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
"""
def send_photo(user_id, image,token):
	img = open(image, 'rb')
	url = f'http://api.telegram.org/{token}/sendPhoto?chat_id={user_id}'
	#resp = requests.get(url)
	#hacemos la petición
	try:
		respuesta = requests.post(url, files={'photo': img})
	except:
		run1.console2.configure(text = f"No se pudo enviar el mensaje")
	else:
		if '200' in str(respuesta):
			print(f"mensaje enviado exitosamente con código {respuesta}")
		else:
			print(f"Ha ocurrido un error al enviar el mensaje: {respuesta}")
"""

#-------------------------- End of Telegram---------------------#

#-----------------------------AUXILIARY OPTIMIZATION FUNCTIONS------------------------#
def return_to_main():
	time.sleep(0.5)
	pyautogui.click(435,163)

def main_menu():
	#flecha de regresar
	pyautogui.click(50,70)
	time.sleep(0.5)
	#boton de ingreso del menu principal
	pyautogui.click(500,200)
	time.sleep(0.5)
	# orden de fabricación
	pyautogui.click(435,163)



def watchdog_t(main_queue,PLC_LT_queue_i):
	while True:
		stop_signal = input()
		if stop_signal == "T":
			PLC_LT_queue_i.put(None)
			shutdown_queue.put(None)
		break


def prepare_data(predata):
	#remove the b stuff
	if len(predata) != 15 :
		predata = "0"
		return predata
	else:
		predata = str(predata)
	return predata

def unpack_datos(posdata):
	x_pos=posdata.find("X")
	print("2.- X encontrada") #b'1234567box140'
	ShopOrder = posdata[x_pos-9:x_pos-2]
	BoxType = posdata[x_pos-2:x_pos+1]
	StandardPack =posdata[x_pos+1:x_pos+4]
	return ShopOrder,BoxType,StandardPack





def PLC_comms(PLC_LT_queue_i,PLC_LT_queue_o,plc,plc_address,plc_netid):
	print('++++++++++++++++++++++++++++++++++ PLC: Running')

	label_data = '0'
	try:
		plc.open()
		plc.set_timeout(2000)
		printer_data = plc.get_handle('PB_Stueckzahl.ADS_Label_Printer_Data_STRING')
	
	except Exception as e:
			print(f"Starting error: {e}")
			time.sleep(5)
			plc,printer_data = aux_PLC_comms(plc_address,plc_netid)
	while True:
		# get a unit of work
		try:
			item = PLC_LT_queue_i.get(block=False)
		except:
			item='0000'
			pass

		# check for stop
		if item is None:
			#PLC release and break
			plc.release_handle(printer_data)
			print(f"handles1 released")
			plc.close()
			PLC_LT_queue_i.task_done()
			break

		#it's time to work.
		try:
			label_data= plc.read_by_name("", plc_datatype=pyads.PLCTYPE_STRING,handle=printer_data)
			if len(label_data)>10:
				PLC_LT_queue_o.put(label_data)
				time.sleep(5)
			label_data = '0'

		except Exception as e:
			print(f"Could not update in PLC: error {e}")
			plc,printer_data = aux_PLC_comms(plc_address,plc_netid)
			continue

def aux_PLC_comms(plc_address_aux,plc_netid_aux):

	while True:
		try:
			plc=pyads.Connection(plc_netid_aux, 801,plc_address_aux)
			plc.open()
			printer_data = plc.get_handle('PB_Stueckzahl.ADS_Label_Printer_Data_STRING')
		except:	
			print(f"Auxiliary PLC_LT1: Couldn't open")
			time.sleep(4)
			continue
		else:
			plc.open()
			print("Success PLC_LT")
			return plc,printer_data

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
	pd_concat = pd.concat([pd_log,new_row_pd])
	pd_concat.to_csv(pd_ruta,index=False)

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
	"""
	La idea de leer estos letreros es tratar de ajustar acciones (como reintentar o no) acorde al texto.
	Se van a dividir en 2 categorías

	Los que paran línea por error de información ingresada o que no tiene caso reintentar.
		-error OF: La shop order ya está llena
		-RTC / Network: error de la aplicación del SAP
	
	Los que ocurren porque hubo un error en la secuencia que podría reintentarse.
		-embalaje
		-HU en uso
		-Objeto bloqueado
		-tratando
	
	Para el primero, implementaremos un código de retorno de 2, si se recibe un 2 en el main thread, entonces hablamos de parar la linea
	Todos los demas código (0 y 1), implican un reintente genérico.
	"""

	with open(resource_path(r'images/tesseract.txt'), 'r') as f:
		tesse_location = f.readline()
	processed_text = "cadena vacia"
	#wait for branch merging then try to adjust screenshot area to allow tesseract to read accurately
	#check if program is installed
	file_exists2 = os.path.exists(tesse_location)
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
	pytesseract.pytesseract.tesseract_cmd = tesse_location
	text = pytesseract.image_to_string(image, config=config)
	# print text
	text = text.split('\n')
	for letter in text:
	#check for nonexistant HU
		if len(letter)<3:
			continue
		#Codigo OF para Shop Order llena
		elif "OF" in letter or "cerrada" in letter or "orden excedido" in letter :
			processed_text = "OF error"
		
		elif "Entrada de mercancias" in letter:
			HU_step1 = letter.find("HU")
			print(f"Proceso terminó normal: {letter[HU_step1:HU_step1+12]}")
			processed_text = f"Proceso termina normal {letter[HU_step1:HU_step1+12]}"
		
		elif "no existe" in letter or "ya esta eliminada" in letter or "entrada" in letter:
			processed_text = "SHO error"
		elif "HTTP" in letter or "RTC" in letter or "network" in letter:
			processed_text = "SAP error"
		else:
			processed_text = f"Error: {letter}"
		"""
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
		"""

	return processed_text




###################################This is the function that actually prints the labels.

def label_print(ShopOrder,BoxType,StandardPack):
	global return_codename
	print("label printing started")
	#a protection to avoid printing empty labels
	##########area to check if app is in position.
	#check if Membrain is ready to take inputs
	inicial_btn = None
	inbox_btn = None
	error2_btn  = None
	error3_btn = None
	error7_btn = None
	error10_btn = None
	
	for i in range(0,6):
		#main screen.
		inicial_btn = pyautogui.locateOnScreen(resource_path(r"images/inicial2.png"),grayscale=False, confidence=.7)
		if inicial_btn !=None:
			break
		#check for an error screen
		error10_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
		if error10_btn !=None:
			break
		#check if Membrain is the main screen
		inbox_btn = pyautogui.locateOnScreen(resource_path(r"images/boton1.png"),grayscale=False, confidence=.7)
		if inbox_btn !=None:
			break
		#check if ok button was left open
		error2_btn = pyautogui.locateOnScreen(resource_path(r"images/purook.png"),grayscale=False, confidence=.7)
		if error2_btn !=None:
			break
		#check if yesno button was left open
		error3_btn = pyautogui.locateOnScreen(resource_path(r"images/purosino1.png"),grayscale=False, confidence=.7)
		if error3_btn !=None:
			break
		#check for GR Cancel
		error7_btn = pyautogui.locateOnScreen(resource_path(r"images/GR_Cancel2.png"),grayscale=False, confidence=.7)
		if error7_btn !=None:
			break
		print(f"pto entrada {i}: {inicial_btn,inbox_btn,error2_btn,error3_btn,error7_btn,error10_btn}")
		time.sleep(3)	

	#there was a ok button left
	if error2_btn != None:
		pyautogui.press('enter')
		return_to_main()
	#no ok button was left, try with yesno
	elif error3_btn != None:
		#if button left open, click 
		pyautogui.press('tab')
		time.sleep(1)
		pyautogui.press('enter')
		#if HU was exceeded
		for i in range(0,10):
			error35_btn = pyautogui.locateOnScreen(resource_path(r"images/purook.png"),grayscale=False, confidence=.7)	
			if error35_btn == None:
				time.sleep(2)
			else:
				break
		if error35_btn != None:
		#main screen after all, click on the screen
			time.sleep(4)
			pyautogui.press('enter')
			main_menu()
			return_to_main()
	#Yes/NO button wasn't? try with the main screen
	elif inbox_btn != None:
	#if main screen was found:
		pyautogui.click(500,200)
	#¿Still no? Maybe it was ok after all this time
	elif inicial_btn != None:
	#initial orange screen detected.
		return_to_main()

	#Maybe it was left in GR Cancel
	elif error7_btn != None:
		#main screen then click on the screen
		time.sleep(4)
		pyautogui.press('enter')
		main_menu()
		return_to_main()
	elif error10_btn != None:
		#somebody left an error message
		pyautogui.press('enter')
		main_menu()
		return_to_main()
	#throw error if ok_flag it's false after this
	else:
		ruta_foto = take_screenshot("full")
		send_message(Jorge_Morales,quote(f" En {Line_ID} falla de detección de punto de entrada"),token_Tel)
		#send_photo(Jorge_Morales,ruta_foto,token_Tel)
		write_log("nok","No se puede identificar el punto de entrada",ShopOrder,BoxType,StandardPack)
		#Add a 1 to try to print again
		return_codename = 1
		return return_codename

##############This is the procedure start
		#click on the Shop Order field
	#pyautogui.click(500,200)
	return_to_main()
	time.sleep(1)
	#write the shop order but before a healthy backspace
	pyautogui.press('backspace')
	pyautogui.write(f"{ShopOrder}")
	print(f"escribí {ShopOrder} en el campo ShopOrder")
	pyautogui.press('enter')

	"""
	Instead of inputting the SHO and waiting 6 seconds to continue, we input the SHO and after that 
		we start to look for both and SHO error and embalaje. Whichever appears first wins.

	If error4 is <> None, then we execute the script for failed SHO 
	IF error5 is None and Error4 is None, then we execute the script for failed embalaje opening (mostly due to internet)

	"""
	for i in range(0,15):
	# tries before failing
	#error5 if to detect if script is going well.				
		error5_btn = pyautogui.locateOnScreen(resource_path(r"images/embalaje.png"),grayscale=False, confidence=.7)
		print(f"Intento de encontrar el embalaje {i}: status: {error5_btn}")
		error4_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
		print(f"Intento de encontrar error en Shop Order {i}: status: {error4_btn}")
		if error5_btn is not None:
			print("Embalaje encontrado")
			break
		if error4_btn is not None:
			print("Error de Shop Order encontrado")
			break			
		time.sleep(3)
	
	if error4_btn is not None and error5_btn is None:
		#error4 es cuando ingresas una Shop Order mal y te envia a falla
		ruta_foto = take_screenshot("error")
		texto_error = read_from_img(ruta_foto)
		write_log("log",texto_error,ShopOrder,BoxType,StandardPack) 
		if "SHO error" in texto_error or "OF error" in texto_error :			
			pyautogui.press('enter')
			main_menu()
			pyautogui.press('backspace')
			write_log("nok","SHO incorrecta",ShopOrder,BoxType,StandardPack)
			# Paro de Línea TBD aqui
			send_message(Jorge_Morales,quote(f" En {Line_ID}: Error 4: {texto_error} Se ejecuta paro de línea"),token_Tel)
			return_codename = 2
			return return_codename
		else:
			#Something standard
			pyautogui.press('enter')
			main_menu()
			send_message(Jorge_Morales,quote(f" En {Line_ID}: Error 4: {texto_error}"),token_Tel)
			return_codename = 1
			return return_codename
		

	
	if error5_btn == None:
		#el error5 es cuando no responde el SAP
		ruta_foto = take_screenshot("error") # cambiado desde full
		send_message(Jorge_Morales,quote(f" En {Line_ID}: No encontré el embalaje"),token_Tel)
		write_log("nok","No se encontró el embalaje",ShopOrder,BoxType,StandardPack)
		main_menu()
		pyautogui.press('enter')
		return_to_main()
		return_codename = 1
		return return_codename
	
	
	
	#no issue, continue
	pyautogui.press('tab')
	pyautogui.press('space')
	#after this space may errors can arise, including the HU is already in use.
	time.sleep(0.2)
	#This is where i can save some time by locating the screen.
	for i in range(0,20):
		#try locating the screen 10 times
		error8_btn = pyautogui.locateOnScreen(resource_path(r"images/PI.png"),grayscale=False, confidence=.7)
		error10_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
		print(f"Intento de encontrar el PI {i}: status: {error8_btn}")
		print(f"Intento de encontrar algun error {i}: status: {error10_btn}")
		if error8_btn is not None or error10_btn is not None:
			print(f"PI o error encontrado: PI:{error8_btn}, error:{error10_btn}")
			break
		time.sleep(3)
	# Si al terminar el ciclo de deteccion de error8 y erro10 no hay nada, (ambos errores = None)
	# entonces se ejecuta el error8 donde NO respondió el SAP
	if error8_btn == None and error10_btn == None :
		ruta_foto = take_screenshot("full")
		send_message(Jorge_Morales,quote(f" En {Line_ID}: No se pudo abrir el PI."),token_Tel)
		write_log("nok","No se encontró el PI",ShopOrder,BoxType,StandardPack)
		main_menu()
		return_codename = 1
		return return_codename
	#si el error 10 no está vacio (<>None), entonces hubo error al desplegar el embalaje.
	if error10_btn is not None:
		#encuentra el error y leelo
		ruta_foto = take_screenshot("error")
		texto_error = read_from_img(ruta_foto)
		# Aqui se puede ejecutar otro paro de linea 
		send_message(Jorge_Morales,quote(f" En {Line_ID}: error10btn: {texto_error}."),token_Tel)
		write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
		pyautogui.press('enter')
		main_menu()
		return_codename = 1
		return return_codename


	#Click en el Lote
	pyautogui.click(747, 360)
	time.sleep(0.5)
	pyautogui.write(f"0{ShopOrder}00")
	time.sleep(0.5)
	#Click en el PI
	pyautogui.click(451, 480)
	time.sleep(0.5)
	pyautogui.write(f"{StandardPack}")
	pyautogui.press('tab')
	#numero de operario
	pyautogui.write(Operator)
	time.sleep(0.5)
	#puesto de trabajo
	pyautogui.press('tab')
	time.sleep(0.5)
	pyautogui.press('tab')
	#texto libre
	pyautogui.write("Auto Print")
	time.sleep(0.5)
	pyautogui.press('tab')
	time.sleep(0.5)
##############---------------THIS ENTER IS TO STORE THE LABEL.
	pyautogui.press('enter')
	time.sleep(1)
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
		print(f"Intento de encontrar el guardar {i}: error: {error2_btn}")
		print(f"Intento de encontrar el guardar {i}: si/no: {error3_btn}")
		print(f"Intento de encontrar el guardar {i}: puro_ok: {error6_btn}")
		if error2_btn is not None or error3_btn is not None or error6_btn is not None:
			break
		else:
			time.sleep(3)
		#YES/NO 
	#This error3_btn appears when there is a warning that says " x pieces to fulfill the order"
	#This is not relevant to read, but a necesary step.
	if error3_btn is not None:
		pyautogui.press('tab')
		time.sleep(0.5)
		pyautogui.press('enter')
		#What if there's an error? 
		#check for error and for the label correct ending
		for i in range(0,20):
			error35_btn = pyautogui.locateOnScreen(resource_path(r"images/errorlabel.png"),grayscale=False, confidence=.7)
			error9_btn = pyautogui.locateOnScreen(resource_path(r"images/purook.png"),grayscale=False, confidence=.7)
			print(f"Intento de encontrar el guardar 2da etapa {i}: error: {error35_btn}")
			print(f"Intento de encontrar el guardar 2da etapa {i}: puro_ok: {error9_btn}")
			if error35_btn is not None or error9_btn is not None :
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
			
			if texto_error == "OF error" or texto_error == "SHO error":
				## Códigos de paro de línea ##
				return_codename = 2
				send_message(Jorge_Morales,quote(f" En {Line_ID}: error35_btn {texto_error}. Se ejecuta paro de línea."),token_Tel)
			else:
				return_codename = 1
				send_message(Jorge_Morales,quote(f" En {Line_ID}: Error35 despues de Enter: {texto_error} "),token_Tel)

			write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
			time.sleep(1)
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
		if texto_error == "OF error" or texto_error == "SHO error" :
			## Códigos de paro de línea ##

			return_codename = 2
			send_message(Jorge_Morales,quote(f" En {Line_ID}: error2_btn {texto_error}. Se ejecuta paro de línea."),token_Tel)
		else:

			return_codename = 1
			send_message(Jorge_Morales,quote(f" En {Line_ID}: Error2_btn despues de Enter: {texto_error} "),token_Tel)

		write_log("log",texto_error,ShopOrder,BoxType,StandardPack)		
		write_log("nok","Error al ingresar la etiqueta",ShopOrder,BoxType,StandardPack)

		time.sleep(0.5)
		pyautogui.press('enter')
		time.sleep(0.5)
		main_menu()
		return return_codename
	if error6_btn is not None:
		#Good ending 2: take note of the HU
		ruta_foto = take_screenshot("error")
		texto_error = read_from_img(ruta_foto)
		write_log("log",texto_error,ShopOrder,BoxType,StandardPack)
		pyautogui.press('enter')
		return_to_main()
		write_log("ok","No error",ShopOrder,BoxType,StandardPack)
		return_codename = 0
		return return_codename

#---------------------------------End of Main Function-------------------------------#


def process_coordinator():
	ShopOrder = ""
	BoxType = ""
	StandardPack = ""
	n=0
	while True:
		time.sleep(2)
		n +=1
		try:
			item = shutdown_queue.get(block=False)
		except:
			pass
		else:
			if item == None:
				print("Closing thread")
				shutdown_queue.task_done()
				break
		
		try:
			print_data = PLC_LT_queue_o.get(block=False)
		except:
			if n % 10 ==0:
				now = datetime.now()
				hora_fecha = now.strftime("%d/%m/%Y %H:%M:%S")
				print(f"APLICACION FUNCIONANDO, EN ESPERA DE ETIQUETAS {hora_fecha}")
		else:
			print(f"Recibido de LT: dato {print_data} \nIniciando Impresion")
			posdata = prepare_data(print_data)
			if posdata != "0":
				ShopOrder,BoxType,StandardPack = unpack_datos(posdata)
			else:
				PLC_LT_queue_o.task_done()
				continue
			nuevo_intento = label_print(ShopOrder,BoxType,StandardPack)
			if nuevo_intento == 1:
				print("se intenta de nuevo la etiqueta")
				nuevo_intento = label_print(ShopOrder,BoxType,StandardPack)
			elif nuevo_intento == 2:
				send_message(Jorge_Morales,quote(f" En {Line_ID}: Paro de Linea ejecutado "),token_Tel)
				# aqui va la variable booleana para ejecutar el paro.
				# 10 segundos despues
				# se libera la variable booleana.
				# hay que programar que si se escribe un 107, el plc libere la variable a Falso. Esto como killswitch
				#waiting time before restarting the process.
			print("5.Tiempo de Espera para Nueva Etiqueta: 1 mins")
			now = datetime.now()
			hora_fecha = now.strftime("%d/%m/%Y %H:%M:%S")
			print(f"6.- Limpieza de variables {hora_fecha}")
			ShopOrder = ""
			BoxType = ""
			StandardPack = ""
			print_data = '0'
			PLC_LT_queue_o.task_done()










if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--PLC1', action='store_true', help='Load Test 1 10.65.96.2')
	parser.add_argument('--PLC2', action='store_true', help='Load Test 2 10.65.96.129')
	parser.add_argument('--noTele', action='store_true', help='Disable Telegram messaging')
	opt = parser.parse_args()

	if not opt.PLC1 and not opt.PLC2:
		print("No se ha seleccionado ningún PLC")
		sys.exit()

	if opt.PLC1 or opt.PLC2:
		#Q1 for PLC_LT command
		PLC_LT_queue_i = Queue()
		PLC_LT_queue_o = Queue()

	#This CSV is for button data. You can add a button if you modify this adequately.
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


	with open(resource_path(r'images/Operator.txt'), 'r') as f:
		Operator = f.readline()

#------------------End of reading files--------------------------#

	#Pandas DataFrame dictionaries
	pd_dict = {'timestamp' : ['dummy'], 'logtype' : ['dummy'],	'texto' : ['dummy'], 'Shop Order' : ['dummy'], 'BoxType' : ['dummy'], 'SP' : ['dummy']}



	#Queue to shutdown main process
	shutdown_queue = Queue()

	if opt.PLC1:
		plc_address = '10.65.96.2'
		plc_netid = '10.65.96.2.1.1'
		print("PLC1 seleccionado")
	else:
		plc_address = '10.65.96.129'
		plc_netid = '10.65.96.129.1.1'
		print("PLC2 seleccionado")

	try:
		pyads.open_port()
		ams_net_id = pyads.get_local_address().netid
		print(ams_net_id)
		pyads.close_port()
		plc=pyads.Connection(plc_netid,801,plc_address)
		plc.set_timeout(2000)
		PLC_thread = Thread(name="hilo_PLC",target=PLC_comms, args=(PLC_LT_queue_i,PLC_LT_queue_o,plc,plc_address,plc_netid),daemon=True)
	except:
		print("PLC couldn't be open. Try establishing it first using System Manager")
		sys.exit()
	else:
		PLC_thread.start()


	#Start monitor thread
	monitor_thread = Thread(target=watchdog_t, args=(shutdown_queue,PLC_LT_queue_i),daemon=True)
	monitor_thread.start()


	process_coordinator()
	monitor_thread.join()
	PLC_thread.join()