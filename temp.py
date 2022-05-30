from genericpath import isfile
import os 
import pyautogui
from datetime import datetime
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



#for i in range(1,81):
#	mis_docs = My_Documents(i)
#	print(f"{i} y la ruta es {mis_docs}")
now = datetime.now()
dt_string = now.strftime("%d%m%Y-%H%M%S")
mis_docs = My_Documents(5)
im = pyautogui.screenshot(region=(410,350, 700, 300))
#check if folder exists
isFile = os.path.isdir(f"{mis_docs}/scfolder")
print(isFile)
if isFile == False:
	os.mkdir(f"{mis_docs}/scfolder/")

im.save(f"{mis_docs}/scfolder/sc-{dt_string}.png")