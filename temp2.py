from tkinter import *
from tkinter import messagebox
from unicodedata import name
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


ws = Tk()
ws.title('Membrain PAS')
ws.geometry('1440x900')
background_image = PhotoImage(file = resource_path("images/SAP1.png"))
label1 = Label(ws, image = background_image)
label1.place(x = 0,y = 0)


def welMsg(name):
    name = name_Tf.get()
    return messagebox.showinfo('pythonguides', f'Hi! {name}, welcome to pythonguides' )

Label(ws, text='Enter Name & hit Enter Key').place(x=390,y=177)
name_Tf = Entry(ws)
name_Tf.bind('<Return>',welMsg)
name_Tf.place(x=380,y=129)
name_Tf.configure(font=('Arial 16'))
ws.mainloop()