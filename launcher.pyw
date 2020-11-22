import sys
import subprocess
from time import sleep
from threading import Thread
from tkinter import Tk
from tkinter import Frame
from tkinter import Label
from tkinter.ttk import Progressbar
from tkinter.constants import CENTER
from tkinter.constants import HORIZONTAL


class Launcher:
    __slots__ = ("app", "frame", "update_label", "progressbar", "window_thread", "update_thread")

    def __init__(self):
        self.app = Tk()
        self.app.title("QCKYTMP3 Updater")
        self.app.geometry("300x150")
        self.frame = Frame(self.app)
        self.frame.place(relx=0.30, rely=0.30)
        self.update_label = Label(self.frame, text="Updating", font=("bold", 20), anchor=CENTER)
        self.update_label.pack()
        self.progressbar = Progressbar(self.frame, orient=HORIZONTAL, maximum=10, value=0)
        self.progressbar.pack()
        self.update_thread = Thread(target=self.update_service, daemon=True)        
        self.update_thread.start()

    def run(self):
        self.app.mainloop()

    def update_service(self):
        self.progressbar.start()
        ret = subprocess.run([sys.executable, "-m", "pip", "install", "-U", "pip", "youtube-dl"]).returncode
        self.progressbar.stop()
        if (ret != 0):
            self.update_label.config(text="Update Fehler...")
            sleep(5)
        self.app.destroy()


launcher = Launcher()
launcher.run()

subprocess.run([sys.executable, "qymp3.pyw"])
