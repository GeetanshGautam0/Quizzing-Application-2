import tkinter as tk
from tkinter import ttk
import os, sys, threading

import qa_appinfo as QAInfo
import qa_theme as QATheme


class UI(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.root = tk.Toplevel()
        self.theme = QATheme.Get().get('theme')

        self.lb = tk.Listbox(self.root)
        self.vsb = ttk.Scrollbar(self.root)
        self.xsb = ttk.Scrollbar(self.root, orient=tk.HORIZONTAL)

        self.WM_QUIT = False
        self.counter = 0
        self.lst = []

        # self.run()
        self.start()
        self.root.mainloop()

    def close(self):
        if __name__ == "__main__" or self.WM_QUIT: self.root.after(0, self.root.quit)
        else: self.root.after(0, self.root.destroy)

    def run(self):
        self.root.title("Quizzing Application")
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.geometry("650x600+{}+{}".format(
            int(self.root.winfo_screenheight()/2 - 325),
            int(self.root.winfo_screenheight()/2 - 300)
        ))
        self.root.config(bg=self.theme.get('bg'))

        self.lb.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg'),
            font=(self.theme.get('font'), self.theme.get('btn_fsize')),
            selectmode=tk.EXTENDED,
            selectbackground=self.theme.get('ac'),
            selectforeground=self.theme.get('hg')
        )
        self.xsb.pack(fill=tk.X, side=tk.BOTTOM)
        self.lb.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.vsb.pack(fill=tk.Y, side=tk.RIGHT)

        self.lb.config(yscrollcommand=self.vsb.set, xscrollcommand=self.xsb.set)
        self.vsb.config(command=self.lb.yview)
        self.xsb.config(command=self.lb.xview)

    def insert_item(self, string: str, index=None) -> int:
        self.counter += 1
        self.lst.append(string)

        self.lb.insert(tk.END if type(index) is not int else index, string)
        self.root.update()

        return self.counter - 1

    def showERR(self, index: int):
        if index > len(self.lst) - 1 or index < 0: return

        self.lb.itemconfig(index,
                           background="#ffffff", foreground="#800000",
                           selectbackground="#800000",
                           selectforeground="#ffffff"
                           )

        self.root.update()

    def showOK(self, index: int):
        if index > len(self.lst) - 1 or index < 0: return

        self.lb.itemconfig(index,
                           background="#ffffff", foreground="#00802b",
                           selectbackground="#00802b",
                           selectforeground="#ffffff"
                           )

        self.root.update()

    def __del__(self):
        self.thread.join(self, 0)
        # pass
