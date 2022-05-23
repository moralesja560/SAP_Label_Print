from tkinter import *
from tkinter import messagebox

ws = Tk()
ws.title('pythonguides')
ws.geometry('250x200')

def welMsg(name):
    name = name_Tf.get()
    return messagebox.showinfo('pythonguides', f'Hi! {name}, welcome to pythonguides' )

Label(ws, text='Enter Name & hit Enter Key').pack(pady=20)
name_Tf = Entry(ws)
name_Tf.bind('<Return>',welMsg)
name_Tf.pack()

ws.mainloop()