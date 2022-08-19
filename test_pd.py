import pandas as pd
from datetime import datetime
import os



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


pd_dict = {'timestamp' : ['dummy'], 'logtype' : ['dummy'],	'texto' : ['dummy'], 'Shop Order' : ['dummy'], 'BoxType' : ['dummy'], 'SP' : ['dummy']}





def write_log(logtype,texto,ShopOrder,BoxType,StandardPack):
	now = datetime.now()
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
	#print("date and time =", dt_string)	
	mis_docs = My_Documents(5)
	ruta = str(mis_docs)+ r"\registro_etiquetas.txt"
	pd_ruta = str(mis_docs)+ r"\registro_etiquetas_df.csv"
	file_exists = os.path.exists(ruta)
	pd_file_exists = os.path.exists(pd_ruta)
	if file_exists == True:
		with open(ruta, "a+") as file_object:
			# Move read cursor to the start of file.
			file_object.seek(0)
			# If file is not empty then append '\n'
			data = file_object.read(100)
			if len(data) > 0 :
				file_object.write("\n")
			# Append text at the end of file
			if logtype == 'ok':
				file_object.write(f" Etiqueta Impresa en {dt_string} con los datos {ShopOrder,BoxType,StandardPack}")
			elif logtype == 'nok':
				file_object.write(f" Hubo un error durante impresión en {dt_string}, con datos {ShopOrder,BoxType,StandardPack} y con error: {texto}")
			elif logtype == 'log':
				file_object.write(f" Registro de Información para análisis en {dt_string}, con datos {ShopOrder,BoxType,StandardPack}: {texto}")
	else:
		with open(ruta,"w+") as f:
			if logtype == 'ok':
				f.write(f" Etiqueta Impresa en {dt_string} con los datos {ShopOrder,BoxType,StandardPack}")
			elif logtype == 'nok':
				f.write(f" Hubo un error durante impresión en {dt_string}, con datos {ShopOrder,BoxType,StandardPack} y con error: {texto}")
			elif logtype == 'log':
				f.write(f" Registro de Información para análisis en {dt_string}, con datos {ShopOrder,BoxType,StandardPack}: {texto}")

	#check if pandas DataFrame exists to load the stuff or to create with dummy data.
	if pd_file_exists:
		pd_log = pd.read_csv(pd_ruta)
	else:
		pd_log = pd.DataFrame(pd_dict)

	new_row = {'timestamp' : [dt_string], 'logtype' : [logtype], 'texto' : [texto], 'Shop Order' : [ShopOrder], 'BoxType' : [BoxType], 'SP' : [StandardPack]}
	new_row_pd = pd.DataFrame(new_row)
	pd_concat = pd.concat([pd_log,new_row_pd])
	print(pd_concat.to_string())
	#store the info
	pd_concat.to_csv(pd_ruta,index=False)



if __name__ == '__main__':
	write_log('ok',"falla de OT",'3568974',"BOX",'109')

