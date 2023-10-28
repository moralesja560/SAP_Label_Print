# text recognition
import os,sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

print(resource_path(r'images\testimg'))

directory_list = os.listdir(resource_path(r'images\testimg'))
print("Files and directories in  current working directory :") 
print(directory_list)