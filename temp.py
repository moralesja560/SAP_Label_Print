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
	def __init__(self,thread_name):
		threading.Thread.__init__(self)
		self.thread_name = thread_name
		self._stop_event = threading.Event()
	#the actual thread function
	def tcp_listen_handle(self, port=65432, connects=5, timeout=2):
		"""This is running in its own thread."""
		sock = socket.socket()
		sock.settimeout(timeout)
		sock.bind((HOST, PORT))
		sock.listen(connects)  # We accept more than one connection.
		while self.keep_running_the_listening_thread()==True:
			connection = None
			addr = None
			try:
				connection, addr = sock.accept()
				print("Socket Connected: %s" % str(addr))
				# makes a thread deals with that stuff. We only do listening.
				#self.handle_tcp_connection_in_another_thread(connection, addr)
				thread2 = hilo2(connection, addr,HOST)
				thread2.start
			except socket.timeout:
				print(f"socket timeout")
				pass
			except OSError:
				# Some other error.
				print("Socket was killed: %s" % str(addr))
				if connection is not None:
					connection.close()
		sock.close()
	def keep_running_the_listening_thread(self):
		return True	
	def stop(self):
		self._stop_event.set()
		print("Thread Stopped")
#----------------------end of thread 1------------------#


class hilo2(threading.Thread):
	#thread init procedure
	# i think we pass optional variables to use them inside the thread
	def __init__(self,opt_arg,opt_arg2,opt_arg3):
		threading.Thread.__init__(self)
		self.conn1 = opt_arg
		self.addr1 = opt_arg2
		self.host1 = opt_arg3
		self._stop_event = threading.Event()
	#the actual thread function
	def run(self):

		print(f"Thread1: connection started")
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((self.host1, 65432))
			self.conn1, self.addr1 = s.accept()
			with self.conn1:
				print(f"Connected by {self.addr1}")
				while True:
					data = self.conn1.recv(1024)
					print(data)
					if not data:
						print("connection closed")
						break
					self.conn1.sendall(data)
				if self._stop_event.set == True:
					self.conn1.close()
					s.close()
				
	def stop(self):
		self._stop_event.set()
		print("Thread Stopped")




if __name__ == '__main__':
	thread1 = hilo1(thread_name="Hilo1")
	thread1.tcp_listen_handle()