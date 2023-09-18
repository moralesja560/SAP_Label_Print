# text recognition
import cv2
import pytesseract
import os,sys
import pandas as pd

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


def write_log(image,text):
	mis_docs = My_Documents(5)
	pd_ruta = str(mis_docs)+ r"\registro_tesseract_df.csv"
	pd_file_exists = os.path.exists(pd_ruta)
	#check if pandas DataFrame exists to load the stuff or to create with dummy data.
	if pd_file_exists:
		pd_log = pd.read_csv(pd_ruta)
	else:
		pd_log = pd.DataFrame(pd_dict)
	new_row = {'filename' : [image], 'texto' : [text]}
	new_row_pd = pd.DataFrame(new_row)
	pd_concat = pd.concat([pd_log,new_row_pd])
	pd_concat.to_csv(pd_ruta,index=False)


with open(resource_path(r'images/tesseract.txt'), 'r') as f:
	tesse_location = f.readline()

directory_list = os.listdir(r'C:\Users\moralesjo\OneDrive - Mubea\Pictures\testimg')
#Pandas DataFrame dictionaries
pd_dict = {'filename' : ['dummy'], 'texto' : ['dummy']}


for image in directory_list:
	# read image
	img = cv2.imread(resource_path(r'C:\Users\moralesjo\OneDrive - Mubea\Pictures\testimg'+"\\"+image))
	# configurations
	config = ('-l spa --oem 1 --psm 1')
	# pytessercat
	pytesseract.pytesseract.tesseract_cmd = tesse_location
	text = pytesseract.image_to_string(img, config=config)
	text = text.split('\n')
	#print(f"se procesa la imagen {image} con el texto {text}")
	write_log(image=resource_path(r'C:\Users\moralesjo\OneDrive - Mubea\Pictures\testimg'+"\\"+image),text=text)
"""	
	for letter in text:
		#check for nonexistant HU
		if len(letter)<3:
			continue
		elif "no existe" in letter:
			print("HU no existente")
		elif "OF" in letter:
			print("Shop Order con OF") 
		elif "tratando" in letter:
			print("HU está siendo usada en otro lado")
		elif "HU planificada" in letter:
			print("Bug de misma Shop Order")
		elif "ninguna orden para" in letter:
			print("Configuración del Membrain equivocada")
		elif "HTTP" in letter or "RTC" in letter:
			print("No respondió el SAP")
		elif "Entrada de mercancias" in letter:
			HU_step1 = letter.find("HU")
			print(f"Proceso terminó normal, HU es {letter[HU_step1:HU_step1+12]}")
			try:
				os.remove(resource_path(r'images\testimg'+"\\"+image))
			except:
				print("error")
		elif "eliminada" in letter:
			print("HU ya fue eliminada")
		elif "maestro de personal" in letter:
			print("Numero de empleado no existe")
		else:
			print(f"El error tenía esto {letter}, pero no pude detectar caracteres")
"""
