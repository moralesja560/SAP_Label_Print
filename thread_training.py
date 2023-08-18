import threading
import time
import sys
import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)



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

"""
mis_docs = My_Documents(5)
ruta = str(mis_docs)+ r"\consola.txt"
sys.stdout = open(ruta, 'w')
"""
##--------------------the thread itself--------------#

class hilo1(threading.Thread):
	#thread init procedure
	# i think we pass optional variables to use them inside the thread
	def __init__(self,thread_name,opt_arg):
		threading.Thread.__init__(self)
		self.thread_name = thread_name
		self.opt_arg = opt_arg
		self._stop_event = threading.Event()
	#the actual thread function
	def run(self):
		#for i in range(1,50):
		#	print(f"thread 1 active: optional var passed is {self.opt_arg}")
		#	time.sleep(2)
		#	if self._stop_event.is_set() == True:
		#		break
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((HOST, PORT))
			s.listen()
			conn, addr = s.accept()
			with conn:
				print(f"Connected by {addr}")
				while True:
					data = conn.recv(1024)
					if not data:
						break
					conn.sendall(data)

	def stop(self):
		self._stop_event.set()
		print("Thread Stopped")
#----------------------end of thread 1------------------#


##--------------------thread 2--------------#

class hilo2(threading.Thread):
	#thread init procedure
	# i think we pass optional variables to use them inside the thread
	def __init__(self,thread_name,opt_arg):
		threading.Thread.__init__(self)
		self.thread_name = thread_name
		self.opt_arg = opt_arg
		self._stop_event = threading.Event()
	#the actual thread function
	def run(self):
		#for i in range(1,50):
		#	print(f"thread 2 active: optional var passed is {self.opt_arg}")
		#	time.sleep(2)
		#	if self._stop_event.is_set() == True:
		#		break
		
		#check for thread1 to keep running
		while True:
			if thread1.is_alive() == False:
				thread1.start()
				print(f"A problem occurred... Restarting Thread 1")
			time.sleep(10)			
			if self._stop_event.is_set() == True:
				break

	def stop(self):
		self._stop_event.set()
		print("Thread Stopped")
#----------------------end of thread 2------------------#






# Create new thread.
thread1 = hilo1(thread_name="Hilo1",opt_arg="h")
thread2 = hilo2(thread_name="Hilo2",opt_arg="Z")
# Start new Threads
#use join to allow the thread to finish before continue. Remove join if you want the thread to execute at the same time.
thread1.start()
thread2.start()


print('Press T to stop hilo1 and S to stop hilo 2:')
#stop_signal = input()

while (thread1.is_alive() or thread2.is_alive()):
	stop_signal = input()
	if stop_signal == "T":
		# I made a function called stop to control an "Event", this event cleanly passes to the thread and i can use it to stop it from inside
		# Please notice that this event do not stop the thread by itself. It only serves as a signal that i can use.
		# two options I can use thread1.stop() or this below
		#thread1._stop_event.set()
		thread1.stop()
		time.sleep(5)
		if thread1.is_alive() == False:
			print(f"Thread 1 has been successfully stopped")
		if thread1.is_alive() == False and thread2.is_alive() == False:
			print(f"Thread 1 & 2 have been successfully stopped")
			break
	if stop_signal == "S":
		#thread2._stop_event.set()
		thread2.stop()
		time.sleep(5)
		if thread2.is_alive() == False:
			print(f"Thread 2 has been successfully stopped")
		if thread1.is_alive() == False and thread2.is_alive() == False:
			print(f"Thread 1 & 2 have been successfully stopped")
			break

#sys.stdout.close()
sys.exit()