import tkinter as tk

class FrameWithButton(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self.btn = tk.Button(root, text="Button")
        self.btn.pack()





root = tk.Tk()
an_instance = FrameWithButton(root)
an_instance.pack()
def update_button():
    global an_instance
    an_instance.btn['text'] = "Button Text Updated!"
tk.Button(root, text="Outside Button", command=update_button).pack()

root.mainloop()