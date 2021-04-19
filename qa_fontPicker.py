from tkinter import *
from tkinter import ttk
from tkinter import font
import threading
import re

OK = False

"""
Base Code from rvfont
Made changes to UI and function

(pip3 install rvfont)
"""

class FontChooser(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        self.start()

        self.root = Tk()

        self.weight = 'normal'
        self.slant = 'roman'
        self.underline = True
        self.strike = False
        self.fonts = {}
        self.selected_font = StringVar()

        self.choose_font = ttk.Combobox(self.root)

        self.selected_size = IntVar()
        self.default_size = 5

        self.window()
        self.root.mainloop()

    def __del__(self):
        pass

    def __repr__(self):
        return self.selected_font.get()

    def window(self):
        self.root.title("Font Picker")
        self.root.geometry("250x85")
        self.root.resizable(False, False)

        self.root.protocol("WM_DELETE_WINDOW", self.Close_Win)

        available_fonts=list(font.families())
        available_fonts.sort()

        self.choose_font.config(width=20, textvariable=self.selected_font, values=available_fonts)
        self.choose_font.current(31)
        self.choose_font.pack(fill=BOTH, expand=1, padx=20, pady=10)
        # self.choose_font.bind("<Key>", lambda: self.FontSearch()) # Added *args to compensate, yet still removed statement due to unexpected behaviour
        self.FontSearch()

        Button(self.root, text='Ok', width=5, command=self.Ok).pack(side=RIGHT, padx=(5, 10), pady=5)
        Button(self.root, text='Cancel', width=5, command=self.Cancel).pack(side=RIGHT, padx=(10, 5), pady=5)

    def FontSearch(self, *args): # In case it gets called by an event, add *args
        values = []

        for i in font.families():
            s = re.match(r"^%s" % (self.selected_font.get()), i, re.I)
            if s: values.append(i)

        self.choose_font["values"] = values
        self.selected_font.set(values[0])

    def destroyWin(self, __setOK: bool, __setOK_Val: any, __ms: int = 0):
        if __setOK:
            global OK
            OK = __setOK_Val

        # self.root.after(__ms, self.root.destroy)

    def Close_Win(self):
        self.root.after(0, self.root.destroy)

    def Cancel(self):
        print(self.choose_font.get())
        self.fonts = {"font": None,
                      "size": None,
                      "weight": None,
                      "slant": None,
                      "underline": None,
                      "strike": None,
                      }

        self.Done() 
        self.root.withdraw()

    def Ok(self):
        self.fonts = {"font": self.choose_font.get(),
                      "size": self.selected_size.get(),
                      "weight": self.weight,
                      "slant": self.slant,
                      "underline": self.underline,
                      "strike": self.strike,
                      }

        self.Done()

    def Done(self):
        Set(self.fonts, self)

def Set(f_info, ref):
    global OK
    OK = f_info
    print(f"Set OK to {f_info}")

    ref.root.after(0, lambda: ref.thread.join(ref, 0))
    ref.DD = True
    ref.root.after(0, ref.root.quit)
    ref.root.withdraw()

def FontDialog():
    FontChooser()

    global OK
    fonts = OK

    print(f"FontDialog: {fonts}")

    return fonts
