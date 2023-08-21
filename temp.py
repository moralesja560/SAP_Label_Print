import os
import time, threading
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import quote
from urllib.request import Request, urlopen
import json



load_dotenv()
token_Tel = os.getenv('TOK_EN_BOT')
Jorge_Morales = os.getenv('JORGE_MORALES')

def send_message(user_id, text,token):
	global json_respuesta
	url = f"https://api.telegram.org/{token}/sendMessage?chat_id={user_id}&text={text}"
	#https://api.telegram.org/bot6392752900:AAGV5VWXxIjpbuyqyVWv6SmdheEPN4LzTV0/sendMessage?
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



while True:
	send_message(Jorge_Morales,quote(f"hi"),token_Tel)
	time.sleep(30)
