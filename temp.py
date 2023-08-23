		#print(f"Thread1: connection started")
		send_message(Jorge_Morales,quote(f"CONEXIÓN ABIERTA"),token_Tel)
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((self.HOST, self.PORT))
			s.settimeout(5)
			s.listen()
			while True:
				if self.stopped():
					s.close()
					break				
				try:
					conn, addr = s.accept()
					print("Socket Connected: %s" % str(addr))
				except socket.timeout:
					print(f"socket timeout")
				except OSError:
					# Some other error.
					print("Socket was killed: %s" % str(addr))
				else:		
					with conn:
						print(f"Connected by {addr}")
						while True:
							data = conn.recv(1024)
							if not data:
								send_message(Jorge_Morales,quote(f"CONEXIÓN CERRADA"),token_Tel)
								break
							posdata = prepare_data(data)
							if posdata != "0":
								ShopOrder,BoxType,StandardPack = unpack_datos(posdata)
								####################-----THE LABEL PRINTING PROCESS-----#
								send_message(Jorge_Morales,quote(f" La Shop Order es {ShopOrder}, el box es {BoxType} y el SPack es {StandardPack}"),token_Tel)
								"""
									nuevo_intento = label_print(ShopOrder,BoxType,StandardPack)
									if nuevo_intento == 1:
										print("se intenta de nuevo la etiqueta")
										nuevo_intento = label_print(ShopOrder,BoxType,StandardPack)
									#waiting time before restarting the process.
									print("5.Tiempo de Espera para Nueva Etiqueta: 1 mins")
									run1.console.configure(text = f"Tiempo de Espera para Nueva Etiqueta: 30s")
									time.sleep(30)
									print("6.- Limpieza de variables")
									ShopOrder = ""
									BoxType = ""
									StandardPack = ""
								"""
							if self._stop_event.set == True:
								conn.close()
								s.close()	