import os, sys, shutil
import qa_logging as Logging
from tkinter import messagebox as tkmsb

def rm():
    for i in os.listdir(Logging.Variables().folderName()):
        try:
            f = Logging.Variables().folderName() + "\\" + i.replace('/', '\\')
            os.remove(f)

        except Exception as e:
            print(e)

    tkmsb.showinfo("QA-Logs", f"Removed Logs")

if __name__ == "__main__": rm()