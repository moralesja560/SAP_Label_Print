#test confidence levels.
import pyautogui
import os
import sys
import time
import datetime



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


def write_log(texto):
	#print("date and time =", dt_string)	
	mis_docs = My_Documents(5)
	ruta = str(mis_docs)+ r"\locate_screen.txt"
	file_exists = os.path.exists(ruta)
	if file_exists == True:
		with open(ruta, "a+") as file_object:
			# Move read cursor to the start of file.
			file_object.seek(0)
			# If file is not empty then append '\n'
			data = file_object.read(100)
			if len(data) > 0 :
				file_object.write("\n")
				# Append text at the end of file	
				file_object.write(f" {texto}")
	else:
		f= open(ruta,"w+")
		f.write(f" {texto}")
		# Close the file
		f.close()




for i in range(1,21):
	if i <= 10:
		confi = i/10
		inicial_btn = pyautogui.locateOnScreen(resource_path(r"images/boton1.png"),grayscale=False, confidence=confi)
		if inicial_btn == None:
			pass
		else:
			button7point = pyautogui.center(inicial_btn)
			button7x, button7y = button7point
			pyautogui.moveTo(button7x, button7y)
			time.sleep(2)
			print(f" prueba {i} con confidence {confi} y grayscale false :{inicial_btn}, con coordenadas centrales {button7x, button7y}")
			write_log(f" prueba {i} con confidence {confi} y grayscale false :{inicial_btn}, con coordenadas centrales {button7x, button7y}")
	else:
		confi = (i-10)/10
		inicial_btn = pyautogui.locateOnScreen(resource_path(r"images/boton1.png"),grayscale=True, confidence=confi)
		if inicial_btn == None:
			pass
		else:
			button7point = pyautogui.center(inicial_btn)
			button7x, button7y = button7point
			pyautogui.moveTo(button7x, button7y)
			time.sleep(2)
			print(f" prueba {i} con confidence {confi} y grayscale True :{inicial_btn}, con coordenadas centrales {button7x, button7y}")
			write_log(f" prueba {i} con confidence {confi} y grayscale false :{inicial_btn}, con coordenadas centrales {button7x, button7y}")