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

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)