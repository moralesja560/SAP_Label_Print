#------------------Author Info----------------------#
#			The SAP Automatic Labeling System
# Designed and developed by: Ing Jorge Alberto Morales, MBA
# Automation Project Sr Engineer for Mubea Coil Springs Mexico
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
#import serial
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
#from sqlalchemy import create_engine
#import pyodbc
#from sqlalchemy.orm import sessionmaker
#import csv
import socket

HOST = "127.0.0.1"  # IP of local computer that
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

######-----------------Sensitive Data Load-----------------####
load_dotenv()
token_Tel = os.getenv('TOK_EN_BOT')
Jorge_Morales = os.getenv('JORGE_MORALES')
pyautogui.FAILSAFE = False


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
#-------------------------- End of Telegram---------------------#


#---------------Thread 1 Area----------------------#
class hilo1(threading.Thread):
	#thread init procedure
	# i think we pass optional variables to use them inside the thread
	def __init__(self,thread_name,opt_arg):
		threading.Thread.__init__(self)
		self.thread_name = thread_name
		self.opt_arg = opt_arg
		self._stop_event = threading.Event()
	#the actual thread function
	def run(self):
		print(f"Thread1: connection started")
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((HOST, PORT))
			s.listen()
			conn, addr = s.accept()
			with conn:
				print(f"Connected by {addr}")
				while True:
					
					data = conn.recv(1024)
					if not data:
						print("connection closed")
						break
					#conn.sendall(data)
					posdata = prepare_data(data)
					send_message(Jorge_Morales,quote(f"aquí está lo que enviaste: {data}"),token_Tel)
				conn.close()
				s.close()
	def stop(self):
		self._stop_event.set()
		print("Thread Stopped")
		
#-------------Thread 1 End------------------#

#---------------Thread 2 Area----------------------#
class hilo2(threading.Thread):
	#thread init procedure
	# i think we pass optional variables to use them inside the thread
	def __init__(self,thread_name,opt_arg):
		threading.Thread.__init__(self)
		self.thread_name = thread_name
		self.opt_arg = opt_arg
		self._stop_event = threading.Event()
	#the actual thread function
	def run(self):
		#check for thread1 to keep running
		while True:
			time.sleep(5)
			if [t for t in threading.enumerate() if isinstance(t, hilo1)]:
				print("todo ok")
			else:
				print(f"A problem occurred... Restarting Thread 1")
				time.sleep(10)
				thread1 = hilo1(thread_name="Hilo1",opt_arg="h")
				thread1.start()			
			print("thread 2 monitoring...")			
			if self._stop_event.is_set() == True:
				break

	def stop(self):
		self._stop_event.set()
		print("Thread Stopped")
#----------------------end of thread 2------------------#

#-----------Area for main program--------------#
# Create new thread.
thread1 = hilo1(thread_name="Hilo1",opt_arg="h")
thread2 = hilo2(thread_name="Hilo2",opt_arg="Z")
# Start new Threads
#use join to allow the thread to finish before continue. Remove join if you want the thread to execute at the same time.
thread1.start()
thread2.start()

while True:
	if [t for t in threading.enumerate() if isinstance(t, hilo1)] and [t for t in threading.enumerate() if isinstance(t, hilo2)] :
		time.sleep(10)
	else:
		break

sys.exit()
        