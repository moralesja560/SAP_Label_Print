import pyads
import sys
import threading
import time
import sys
from dotenv import load_dotenv
import os
from urllib.request import Request, urlopen
import json
from urllib.parse import quote
import datetime

load_dotenv()
token_Tel = os.getenv('TOK_EN_BOT')
Jorge_Morales = os.getenv('JORGE_MORALES')

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

def otra_cosa(data):
	print("40")
	time.sleep(2)
	print("60")
	time.sleep(2)
	print("80")
	time.sleep(2)
	print("100")	
	time.sleep(2)
	print("120")


##--------------------the thread itself--------------#

class hilo1(threading.Thread):
	#thread init procedure
	# i think we pass optional variables to use them inside the thread
	def __init__(self):
		threading.Thread.__init__(self)
		self._stop_event = threading.Event()
	#the actual thread function
	def run(self):
		plc.open()		
		#symbol = plc.get_symbol("Ethernet.SD_Online_Printer_Send_String_Ethernet")
		#symbol.auto_update = True
		while True:
			time.sleep(0.2)
			data = plc.read_by_name("PB_Stueckzahl.ADS_Communication_Test_STRING", plc_datatype=pyads.PLCTYPE_STRING)
			if "s"  in data:
				pass
			else:
				print(f"ya recibi la información, vamos a def {data}")
				otra_cosa(data)
			if self._stop_event.is_set():
				# close connection
				print("saliendo")
				plc.close()
				break
	def stop(self):
		self._stop_event.set()

	def stopped(self):
		return self._stop_event.is_set()
#----------------------end of thread 1------------------#

if __name__ == '__main__':
	# connect to the PLC
	try:
		plc = pyads.Connection('10.65.96.129.1.1', 801)
	except:
		print("No se pudo abrir la conexión")
		sys.exit()
	# open the connection
	else:
		thread1 = hilo1()
		thread1.start()
	while True:
		stop_signal = input()
		if stop_signal == "T":
			thread1.stop()
		break
	