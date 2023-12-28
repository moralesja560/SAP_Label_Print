import cv2
import numpy as np
import os
import sys

def template_match(base_img):

	ok_found = False
	sino_found = False
	error_found = False
	boton_found = False
	inicial_found = False

	ok_int = 0
	sino_int = 0
	error_int = 0
	boton_int = 0
	inicial_int = 0

	#Load base image
	base_img = cv2.imread(base_img)

	#load templates ok
	template_ok = cv2.imread("images/purook.png")
	template_sino = cv2.imread("images/purosino1.png")
	template_error = cv2.imread("images/errorlabel.png")
	boton_ini = cv2.imread("images/boton2.png")
	template_inicial = cv2.imread("images/inicial3.png")
	
	  
	#w, h = template.shape[1],template.shape[0]


	res_ok = cv2.matchTemplate(base_img,template_ok,cv2.TM_CCOEFF_NORMED)
	res_sino = cv2.matchTemplate(base_img,template_sino,cv2.TM_CCOEFF_NORMED)
	res_error = cv2.matchTemplate(base_img,template_error,cv2.TM_CCOEFF_NORMED)
	
	#botones de proceso
	boton1_mtc = cv2.matchTemplate(base_img,boton_ini,cv2.TM_CCOEFF_NORMED)
	inicial_mtc = cv2.matchTemplate(base_img,template_inicial,cv2.TM_CCOEFF_NORMED)
	
	#Threshold de 90 para los botones de respuesta.
	threshold = 0.90
	loc_ok = np.where( res_ok >= threshold)
	loc_sino = np.where( res_sino >= threshold)
	loc_error = np.where( res_error >= threshold)

	threshold = 0.85
	loc_inicial = np.where( inicial_mtc >= threshold)

	threshold = 0.75
	#Threshold de 75 para los botones de proceso
	loc_boton = np.where( boton1_mtc >= threshold)
	
	
	
	for pt in zip(*loc_ok[::-1]):
		ok_int +=1
	for pt in zip(*loc_sino[::-1]):
		sino_int +=1
	for pt in zip(*loc_error[::-1]):
		error_int +=1
	for pt in zip(*loc_boton[::-1]):
		boton_int +=1
	for pt in zip(*loc_inicial[::-1]):
		inicial_int +=1
		
	#Seccion de retorno de interaccion
	if error_int >0:
		error_found = True
	elif sino_int >0:
		sino_found = True
	elif ok_int > 0:
		ok_found = True
	# Seccion de retorno de proceso
	elif boton_int >0:
		boton_found = True
	elif inicial_int >0:
		inicial_found = True

	return error_found,sino_found,ok_found,boton_found,inicial_found
		#cv2.rectangle(base_img, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)


		#min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
		#top_left = max_loc
		#bottom_right = (top_left[0] + w, top_left[1] + h)

		#cv2.rectangle(base_img,top_left, bottom_right, 255, 2)	
		#cv2.imwrite("base_processed3.png",base_img)

if __name__ == '__main__':

	file_list = os.listdir(r"E:\TEMP_LABEL\scfolder")
	n=0
	for filepaths in file_list:
		
		ruta_c = r"E:\TEMP_LABEL\scfolder"+"\\"+filepaths
		#print(ruta_c)
		img = cv2.imread(ruta_c)
		error_found,sino_found,ok_found,boton_found,inicial_found = template_match(ruta_c)
		n+=1
		ruta_d = r"E:\TEMP_LABEL\cero"+"\\"+f"{n}"
		if error_found:
			ruta_d = ruta_d + "-ERR"
		if sino_found:
			ruta_d = ruta_d + "-SINO"
		if ok_found:
			ruta_d = ruta_d + "-OK"
		if boton_found:
			ruta_d = ruta_d + "-BOT"
		if inicial_found:
			ruta_d = ruta_d + "-INI"
			ruta_d = ruta_d + ".png"
			cv2.imwrite(ruta_d,img)
		
		
		#ruta_d = r"E:\TEMP_LABEL\ok"+"\\"+f"{n}-ERR{error_found}-SN{sino_found}-OK{ok_found}-BOT{boton_found}-INI{inicial_found}.png"
		