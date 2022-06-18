# text recognition
import cv2
import pytesseract
import os,sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# read image
img = cv2.imread(resource_path(r"images/HUerror.png"))

# configurations
config = ('-l eng --oem 1 --psm 3')

# pytessercat
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract/tesseract.exe'


text = pytesseract.image_to_string(img, config=config)
text = text.split('\n')

for letter in text:
	#check for nonexistant HU
	if len(letter)<2:
		continue
	if "no existe" in letter:
		print("procesamiento de cadena por HU no existente")
	if "OF" in letter:
		print("procesamiento de cadena por OF")
	if "tratando" in letter:
		print("procesamiento de cadena por error de HU")
	if "HU planificada" in letter:
		print("Bug de misma Shop Order")


#HU processing
#x_pos= text.find('HU')
#print(text[x_pos+3:x_pos+12])


