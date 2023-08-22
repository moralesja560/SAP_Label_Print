import threading
import time
import sys
import socket

HOST = "10.65.72.70"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

##--------------------the thread itself--------------#

class hilo1(threading.Thread):
	#thread init procedure
	# i think we pass optional variables to use them inside the thread
	def __init__(self):
		threading.Thread.__init__(self)
		self._stop_event = threading.Event()
	#the actual thread function
	def run(self):
		print(f"Thread1: connection started")
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((HOST, PORT))
			s.settimeout(5)
			s.listen()
			while True:
				try:
					if self.stopped():
						s.close()
						break
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
							print("connection closed")
							break
						conn.sendall(data)
					if self._stop_event.set == True:
						conn.close()
						s.close()				
	def stop(self):
		self._stop_event.set()

	def stopped(self):
		return self._stop_event.is_set()
#----------------------end of thread 1------------------#

if __name__ == '__main__':
	thread1 = hilo1()
	thread1.start()
	while True:
		stop_signal = input()
		if stop_signal == "T":
			thread1.stop()
		break
	