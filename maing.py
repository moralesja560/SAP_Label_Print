#------------------Author Info----------------------#
#			The SAP Automatic Labeling System
# Designed and developed by: Ing Jorge Alberto Morales, MBA
# Automation Project Sr Engineer for Mubea Coil Springs Mexico
# Jorge.Morales@mubea.com
#---------------------------------------------------#

#----------------------import area

import os
import time, threading
from tkinter import *
from tkinter import messagebox
from functools import partial
import tkinter as tk
import pyautogui
import sys
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote
from urllib.request import Request, urlopen
import json
import cv2
import pytesseract
import pandas as pd
import csv
from random import randrange
import pyads

###-------------------------------V2.9 Launched-------------------------#

"""
	loop para la detección del punto de entrada. Eso debería hacerlo mas eficiente.

"""


###-------------------------------V2.95 Progress-------------------------#
"""
	FINISHED:

	ONGOING:
		5.-Programar PLC para en caso de un OF, 
		7.- Si no hay punto de entrada, ¿qué podemos hacer?
		11.- Prevenir multiples instancias de la app
		15.- Creo que la app se queda sin responder. Algun loop para que esté haciendo algo con el PLC en lo que llega la etiqueta..
			El problema era el sistema de Quick Edit de la consola, si le das click, se pausa.
		16.- Reduce la cantidad de mensajes que marca 
		17.- borra una vez al mes la carpeta de fotos.
		



		

"""



###-------------- Algunas notas sobre Twincat ADS y Python----------------#
"""
	-Es fundamental que se instale el ambiente Twincat, hasta ahorita el que ha funcionado es el R3_2.11.2301
	-Despues se mueve la libreria TCAdsDll.dll (se encuentra en C:\TwinCAT\AdsApi\TcAdsDll\x64) a System32
	-Esa librería se tiene que registrar usando el CMD de Windows con el comando regsvr32 TcAdsDll.dll y debe dar OK
	-Una vez que se haya registrado la librería, se procede a usar el Twincat System Manager para hacer la conexión.
	-Esta conexion es la usual que se hace antes de conectarse al PLC.
	-Una vez que se haya hecho esta conexion, se va a poder usar la app en una nueva compu.
	-Casi cualquier error del ADS es por el remote route. Es necesario usar el System Manager para "que se conozcan" y luego ya pueda aceptar conexiones vía ADS
	-Cabe destacar que el PLC se conecta vía protocolo físico ethernet, pero protocolo virtual es Twincat ADS.
	-
"""

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




#-------------------Twincat String Management---------------------#
""" This function removes unwanted string and prevents strange characters to reach
	other parts of the code. It is not tha neccesary since the string comes clean from PLC, but who knows?
"""
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
		run1.console.configure(text = "No se puede identificar el punto de entrada")
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
			run1.console.configure(text = "Shop Order incorrecta")
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
		run1.console.configure(text = "No se encontró la secc de PI")
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
		run1.console.configure(text = "Impresión Terminada: Revise Log")
		return_codename = 0
		return return_codename

#---------------------------------End of Main Function-------------------------------#


#---------------Thread 1 Area----------------------#
class hilo1(threading.Thread):
	#thread init procedure
	# i think we pass optional variables to use them inside the thread
	def __init__(self,thread_name,opt_arg,opt_arg2):
		threading.Thread.__init__(self)
		self.daemon = True
		self.thread_name = thread_name
		self.HOST = opt_arg
		self.PORT = opt_arg2
		self._stop_event = threading.Event()
	#the actual thread function
	def run(self):
		try:
			plc = pyads.Connection(self.HOST, self.PORT)	
		except Exception as e:
			print(f"No se pudo conectar con el puerto. Error {e}")
		else:
			plc.open()		
			while True:
				time.sleep(0.5)
				try:
					data = plc.read_by_name("PB_Stueckzahl.ADS_Label_Printer_Data_STRING", plc_datatype=pyads.PLCTYPE_STRING)
				except Exception as e:
					print(f"Falla al leer la variable: error {e}")
					thread1.stop()
					break
				else:
					if len(data)>10:
						#print("inicia proceso")
						posdata = prepare_data(data)
						if posdata != "0":
							ShopOrder,BoxType,StandardPack = unpack_datos(posdata)
							####################-----THE LABEL PRINTING PROCESS-----#
							#send_message(Jorge_Morales,quote(f" La Shop Order es {ShopOrder}, el box es {BoxType} y el SPack es {StandardPack}"),token_Tel)
							root.wm_state('iconic')
							time.sleep(2)
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
							run1.console.configure(text = f"Tiempo de Espera para Nueva Etiqueta: 10s")
							now = datetime.now()
							hora_fecha = now.strftime("%d/%m/%Y %H:%M:%S")
							time.sleep(5)
							print(f"6.- Limpieza de variables {hora_fecha}")
							ShopOrder = ""
							BoxType = ""
							StandardPack = ""
							
				if self.stopped():
					thread1.stop()
					plc.close()
					break
	def stop(self):
		print("si entre a stopear")
		self.stopped = True
		self._stop_event.set()


	def stopped(self):
		return self._stop_event.is_set()
		
#-------------Thread 1 End------------------#

#---------------Thread 2 Area----------------------#
class hilo2(threading.Thread):
	#thread init procedure
	# i think we pass optional variables to use them inside the thread
	def __init__(self,thread_name):
		threading.Thread.__init__(self)
		self.thread_name = thread_name
		self._stop_event = threading.Event()
	#the actual thread function
	def run(self):
		#check for thread1 to keep running
		while True:
			now = datetime.now()
			hora_fecha = now.strftime("%d/%m/%Y %H:%M:%S")
			if [t for t in threading.enumerate() if isinstance(t, hilo1)]:
				try:
					run1.console.configure(text = f"Monitor Activo {randrange(10)}")
					time.sleep(5)
				except:
					self._stop_event.set()
			else:
				print(f"A problem occurred... Restarting Thread 1 {hora_fecha}")
				time.sleep(5)
				try:
					thread1 = hilo1(thread_name="Hilo1",opt_arg=run1.ComList.get(),opt_arg2=801)
					thread1.start()
					print(f"Thread 1 Started {hora_fecha}")
				except:
					print(f"ya se cerró la app")
					sys.exit()
				
			
			if self._stop_event.is_set() == True:
				print("Thread 2 Stopped")
				break

	def stop(self):
		self._stop_event.set()
		
#----------------------end of thread 2------------------#







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
		self.background_image = PhotoImage(file = resource_path("images/UI4.png"))
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
			self.console.place(x=240,y=515)
			self.console.configure(text = "")
			self.console.configure(fg="white", bg="black", font=("Console",10))

			self.console2 = Label(self.parent,width = w_offset*15, height = h_offset)
			self.console2.place(x=240,y=630)
			self.console2.configure(text = "")
			self.console2.configure(fg="white", bg="black", font=("Console",10))

			# operator num show
			operatorlabel=Label(self.parent,text = Operator).place(x = 40, y = 60) 

######### Create Dropdown menus for COM options 
		#ComPort.
		dropwidth = 20
		dropfront = "white"
		dropbg = '#314a94'
		dropfont = ("Sans-serif",10)
		dropx = 100
		dropy = 308
		
		portList = ['10.65.96.129.1.1','10.65.96.2.1.1']

		intlist = [1,2,3,4,5,6,7]

		self.ComList = StringVar()
		self.ComList.set('10.65.96.129.1.1')
		dropdown1 = OptionMenu(self.parent,self.ComList,*portList)
		dropdown1.place(x=int(dropx)-50,y=int(dropy))
		dropdown1.configure( fg=dropfront, bg=dropbg, width=dropwidth, font=dropfont )

		self.IntSending = StringVar()
		self.IntSending.set(int(1))
		dropdown1 = OptionMenu(self.parent,self.IntSending,*intlist)
		dropdown1.place(x=int(dropx+500),y=int(dropy))
		dropdown1.configure( fg=dropfront, bg=dropbg, width=dropwidth, font=dropfont )

		#Button disable until AMS NetID connection is successful
		a_temp = 'Button1'
		globals()[a_temp].configure(state = "disabled")
##########Selector is the function that commands buttons actions
	def Selector(self,num):
		global ComPort
		#go to def run() in thread 2 and config it to pass these variables to the method1 second thread.	
		#### area to check if the info coming from the optionmenu is valid and all the option menus were opened and selected.
			
		#button to Ping
		if num == 10:
			pass
		if num == 20:
			try:
				thread1 = hilo1(thread_name="Hilo1",opt_arg=ComPort,opt_arg2=801)
				thread2 = hilo2(thread_name="Hilo2")
				thread2.stop()
				time.sleep(2)
				thread1.stop()
				messagebox.showinfo('Terminar Proceso','Conexión Cerrada')
			except Exception as e:
				print(f"error de cierre es: {e}")
			finally:
				a_temp = 'Button1'
				globals()[a_temp].configure(state = "disabled")
				#a_temp = 'Button4'
				#globals()[a_temp].configure(state = "disabled")
				a_temp = 'Button3'
				globals()[a_temp].configure(state = "active")
		if num == 30:
			ComPort = self.ComList.get()
			try:
				pyads.open_port()
				ams_net_id = pyads.get_local_address().netid
				#print(ams_net_id)
				pyads.close_port()
				
			except Exception as e:
				print("No se pudo abrir la conexión: Error {e}")
				# open the connection
			else:
				thread1 = hilo1(thread_name="Hilo1",opt_arg=ComPort,opt_arg2=801)
				thread2 = hilo2(thread_name="Hilo2")
				thread1.daemon =  True
				thread1.start()
				print(f"se arranca hilo")
				thread2.daemon = True
				thread2.start()
				a_temp = 'Button1'
				globals()[a_temp].configure(state = "active")
				a_temp = 'Button3'
				globals()[a_temp].configure(state = "disabled")
				#a_temp = 'Button4'
				#globals()[a_temp].configure(state = "active")
				
		if num == 40:
			Nummer = self.IntSending.get()
			ComPort = self.ComList.get()
			try:
				plc = pyads.Connection(ComPort,801)	
				plc.open()
				plc.write_by_name('PB_Stueckzahl.ADS_Label_Incoming_Ping',int(Nummer),pyads.PLCTYPE_INT)
				message_from_twincat = plc.read_by_name('PB_Stueckzahl.ADS_Label_Outgoing_Ping', pyads.PLCTYPE_INT)
				run1.console.configure(text=f"Recepción de PLC {message_from_twincat}")
			except Exception as e:
				print(f"No se pudo conectar con el puerto. Error {e}")
			

	def quit(self):
		if messagebox.askyesno('Salida','¿Seguro que quiere salir?'):
            #In order to use quit function, mainWindow MUST BE an attribute of Interface. 
			thread2.stop()
			time.sleep(2)
			thread1.stop()
			self.parent.destroy()
			self.parent.quit()
			send_message(Jorge_Morales,quote(f'{Line_ID}: El sistema se ha detenido'), token_Tel)
			sys.exit()



#/////----------------------------Reading and Writing Files--------------------------#

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



#-----------Area for main program--------------#

if __name__ == '__main__':
	send_message(Jorge_Morales,quote(f'{Line_ID}: El sistema se ha iniciado'), token_Tel)
	#tkinter class assign
	root = tk.Tk()
## How to start a new thread? 
	# Assign a name and pass a few variables to it.
	# First thread 
	run1 = Passwordchecker(root)
	thread1 = hilo1(thread_name="Hilo1",opt_arg="",opt_arg2=65432)
	thread2 = hilo2(thread_name="Hilo2")
	root.mainloop() #GUI.start()
	sys.exit()
	