import sys
import subprocess
from threading import Thread
from tkinter import StringVar, Tk
from tkinter import Frame
from tkinter import Label
from tkinter import Entry
from tkinter import Button
from tkinter import filedialog
from tkinter import Menu
from tkinter import TclError
from tkinter.ttk import Progressbar
from tkinter.constants import CENTER
from tkinter.constants import HORIZONTAL
from configparser import ConfigParser
from queue import Queue
from queue import Empty
from time import sleep


class QYMP3:
    __slots__ = (
        "app", 
        "frame", 
        "config", 
        "urlbox_label", 
        "urlbox_text",
        "urlbox_entry", 
        "spacer_1",
        "save_path",
        "save_path_string",
        "path_label", 
        "path_button", 
        "spacer_2", 
        "download_button",
        "progress_bar",
        "progress_label",
        "running",
        "download_queue",
        "download_thread"
    )

    def __init__(self):
        self.app = Tk()
        self.app.title("Papa's Musik Converter")
        self.app.geometry("560x340")
        self.frame = Frame(self.app)
        self.frame.place(relx=0.05, rely=0.05)
        self.config = ConfigParser()
        self.config.read("config.ini")
        self.save_path = self.config.get("directories", "download_path")
        self.save_path_string = "Speicherort: " + self.save_path

        self.urlbox_label = Label(self.frame, text="Youtube Link einfügen: ", font=("bold", 20), anchor=CENTER)
        self.urlbox_label.pack()
        self.urlbox_text = StringVar()
        self.urlbox_entry = Entry(self.frame, textvariable=self.urlbox_text, width=45, font=("bold", 15))
        self.urlbox_entry.pack()
        self.urlbox_entry.bind("<Button-3>", self.rClicker, add="")
        self.spacer_1 = Label(self.frame, text="", font=("bold", 10), anchor=CENTER)
        self.spacer_1.pack()

        self.path_button = Button(self.frame, text="Speicherort wählen (Klick mich)", font=("bold", 15),
                                command=lambda: self.directory_selection())
        self.path_button.pack(pady=7)
        self.path_label = Label(self.frame, text=self.save_path_string, font=(13), anchor=CENTER)
        self.path_label.pack()
        self.spacer_2 = Label(self.frame, text="", font=("bold", 10), anchor=CENTER)
        self.spacer_2.pack()

        self.download_button = Button(self.frame, text="Download", font=("bold", 20), anchor=CENTER,
                                    command=lambda: self.add_to_download_queue())
        self.download_button.pack()
        self.progress_bar = Progressbar(self.frame, orient=HORIZONTAL, maximum=10, value=0)
        self.progress_bar.pack(pady=7)
        self.progress_label = Label(self.frame, text="", font=("bold", 15), anchor=CENTER)
        self.progress_label.pack()

        self.running = True
        self.download_queue = Queue()
        self.download_thread = Thread(target=self.download_loop, daemon=True)
        self.download_thread.start()


    def run(self):
        self.app.mainloop()


    def download_loop(self):
        while self.running:
            try:
                track = self.download_queue.get(timeout=3600)

                self.progress_bar.start()
                self.progress_label.config(text="Downloading...")
                retval = self.get_mp3(track)
                if retval != 0:
                    sleep(5)
                    retval = self.get_mp3(track)
                    if retval != 0:
                        self.progress_label.config(text="Fehler bei " + track.get("url"))
                    else:
                        self.progress_label.config(text="Fertig!")
                        self.urlbox_entry.delete(0, "end")
                else:
                    self.progress_label.config(text="Fertig!")
                    self.urlbox_entry.delete(0, "end")

                self.progress_bar.stop()
                
            except Empty:
                self.app.destroy()
                sys.exit(0)


    def get_mp3(self, track):
        url = track.get("url")
        save_path = track.get("save_path")

        return subprocess.run([
            "youtube-dl", 
            "--extract-audio",
            "--audio-format", 
            "mp3",
            "--audio-quality",
            "192K",
            "--prefer-ffmpeg",
            "-o",
            save_path,
            "-f",
            "251",
            url
        ]).returncode


    def add_to_download_queue(self):
        save_path = self.save_path + "/%(title)s.%(ext)s"
        url = self.urlbox_entry.get()
        if url.startswith("https://www.youtube.com/") or url.startswith("https://youtu.be/") or url.startswith("https://m.youtube.com/"):
            track = {"url": url, "save_path": save_path}
            self.download_queue.put(track)
        else:
            self.progress_label.config(text="Das ist kein Youtube Link")


    def directory_selection(self):
        self.save_path = filedialog.askdirectory()
        self.path_label.config(text="Speicherort: " + self.save_path)
        self.config.read('config.ini')
        self.config.set('directories', 'download_path', self.save_path)
        with open('config.ini', 'w') as f:
            self.config.write(f)


    def rClicker(self, e):
        '''right click context menu for all Tk Entry and Text widgets'''

        try:
            def rClick_Copy(e, apnd=0):
                e.widget.event_generate('<Control-c>')
            def rClick_Cut(e):
                e.widget.event_generate('<Control-x>')
            def rClick_Paste(e):
                e.widget.event_generate('<Control-v>')
            e.widget.focus()

            nclst = [
                (' Ausschneiden', lambda e=e: rClick_Cut(e)),
                (' Kopieren', lambda e=e: rClick_Copy(e)),
                (' Einfügen', lambda e=e: rClick_Paste(e)),
            ]

            rmenu = Menu(None, tearoff=0, takefocus=0)

            for (txt, cmd) in nclst:
                rmenu.add_command(label=txt, command=cmd)

            rmenu.tk_popup(e.x_root + 40, e.y_root + 10, entry="0")

        except TclError:
            print
            ' - rClick menu, something wrong'
            pass

        return "break"



qymp3 = QYMP3()
qymp3.run()
