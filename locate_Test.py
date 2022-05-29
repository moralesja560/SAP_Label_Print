#test confidence levels.
import pyautogui
import os
import sys


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


for i in range(1,21):
	if i <= 10:
		confi = i/10
		inicial_btn = pyautogui.locateOnScreen(resource_path(r"images/inicial2.png"),grayscale=False, confidence=confi)
		if inicial_btn == None:
			pass
		else:
			button7point = pyautogui.center(inicial_btn)
			button7x, button7y = button7point
			print(f" prueba {i} con confidence {confi} y grayscale false :{inicial_btn}, con coordenadas centrales {button7x, button7y}")
	else:
		confi = (i-10)/10
		inicial_btn = pyautogui.locateOnScreen(resource_path(r"images/inicial2.png"),grayscale=True, confidence=confi)
		if inicial_btn == None:
			pass
		else:
			button7point = pyautogui.center(inicial_btn)
			button7x, button7y = button7point
			print(f" prueba {i} con confidence {confi} y grayscale True :{inicial_btn}, con coordenadas centrales {button7x, button7y}")