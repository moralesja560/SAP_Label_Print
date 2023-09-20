import pandas as pd
import os,sys
from datetime import datetime
import numpy as np
from random import randrange


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

mis_docs = My_Documents(5)
pd_ruta = str(mis_docs)+ r"\registro_tesseract_df.csv"

# cargamos los CSV
database = pd.read_csv(pd_ruta)

for x in range(0,database['filename'].count()):
	os.rename(str(database.iat[x,0]),str(database.iat[x,0]) +" "+ database.iat[x,2]+" "+ str(randrange(1000,90000)) +".PNG")



print("hi")