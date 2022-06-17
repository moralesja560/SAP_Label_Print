# text recognition
import cv2
import pytesseract
import os,sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# read image
img = cv2.imread(resource_path(r"images/HUread.png"))

# configurations
config = ('-l eng --oem 1 --psm 3')

# pytessercat
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract/tesseract.exe'
text = pytesseract.image_to_string(img, config=config)

# print text
text = text.split('\n')
print(text)