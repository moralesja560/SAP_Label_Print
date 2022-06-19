# text recognition
import cv2
import pytesseract
import os,sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



directory_list = os.listdir(resource_path(r'images\testimg'))
print("Files and directories in  current working directory :") 


for image in directory_list:
	# read image
	img = cv2.imread(resource_path(r'images\testimg'+"\\"+image))
	# configurations
	config = ('-l eng --oem 1 --psm 1')
	# pytessercat
	pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract/tesseract.exe'
	text = pytesseract.image_to_string(img, config=config)
	text = text.split('\n')
	print(f"se procesa la imagen {image} con el texto {text}")
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
			#'Entrada de mercancias en HU 156444885 a 3000 contabilizada'
		elif "eliminada" in letter:
			print("HU ya fue eliminada")
		elif "maestro de personal" in letter:
			print("Numero de empleado no existe")
		else:
			print(f"El error tenía esto {letter}, pero no pude detectar caracteres")
