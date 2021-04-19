import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsb
import threading, sys, os

import qa_appinfo as QAInfo
import qa_theme as QATheme
import qa_fileIOHandler as QAFileIO
import qa_errors as QAExceptions
import qa_questions as QAQuestionStandard

class IO:    
    def __init__(self, fn: str, **kwargs):
        self.filename = fn
        self.object = QAFileIO.create_fileIO_object(self.filename)
        
        self.flagsHandlerDict = {
            'append': [False, (bool, )],
            'append_sep': ["\n", (str, bytes)],
            'suppressError': [False, (bool,)],
            'encoding': ['utf-8', (str, )],
            'encrypt': [False, (bool, )]
        }
        
        print(kwargs)
        
        self.flags = {}; KWARGS(self, 'f', flags=kwargs)
        
        print(self.flags)
        
    def rawLoad(self) -> bytes:
        return QAFileIO.load(self.object)

    def save(self, Data):  # Secure Save
        QAFileIO.save(
            self.object,
            Data,
            append=self.flags['append'],
            appendSeperator=self.flags['append_sep'],
            encryptData=self.flags['encrypt'],
            encoding=self.flags['encoding']
        )

    def clear(self) -> None:
        open(self.object.filename, 'w').close()

    def autoLoad(self) -> str:
        return QAFileIO.read(self.object)

    def encrypt(self) -> None:
        QAFileIO.encrypt(self.object)

    def decrypt(self) -> None:
        QAFileIO.decrypt(self.object)
    
class UI(threading.Thread):
    
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        
        self.root = tk.Toplevel()

        self.ws = [
            self.root.winfo_screenwidth(),
            self.root.winfo_screenheight()
        ]; self.ws = (
            # int(self.ws[0] - self.ws[0] * 0.05),
            # int(self.ws[1] - self.ws[1] * 0.05)
            self.ws[0], self.ws[1]
        )

        self.wp = (
            # int(self.root.winfo_screenwidth() / 2 - self.ws[0] / 2),
            # int(self.root.winfo_screenheight() / 2 - self.ws[1] / 2)
            0, 0
        )

        self.vsb_style = ttk.Style()
        self.vsb_style.theme_use('default')
        
        self.sepStyle = ttk.Style()
        self.sepStyle.theme_use('default')
        
        self.vsb = ttk.Scrollbar(
            self.root,
            orient=tk.VERTICAL
        )
        
        self.xsb = ttk.Scrollbar(
            self.root,
            orient=tk.HORIZONTAL
        )
        
        self.canv = tk.Canvas(self.root)
        self.frame = tk.Frame(self.canv)

        self.loadingLbl = tk.Label(self.frame, text="Loading questions; please wait.")
        
        self.theme = QATheme.Get().get('theme')
        
        self.update_lbl: list = []
        self.update_accent_foreground: list = []
        self.update_text_font: dict = {}

        self.id_assign = {}

        self.start()
        self.root.mainloop()
    
    def close(self):
        if not __name__ == "__main__":
            self.root.after(0, self.root.destroy)
            return

        else:
            sys.exit('WM_DELETE_WINDOW')
    
    def run(self):
        # Root config
        self.root.state('zoomed') # Maximize the winow
        self.root.iconbitmap(QAInfo.icons_ico.get('admt'))
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.title(f"Quizzing Application: Registered Questions")
        self.root.minsize(500, 100)

        # Place the widgets
        self.xsb.pack(fill=tk.X, expand=False, side=tk.BOTTOM)
        self.canv.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.vsb.pack(fill=tk.Y, expand=False, side=tk.RIGHT)
        self.frame.pack(fill=tk.BOTH, expand=True)

        self.loadingLbl.config(text="Loading questions; please wait.")
        self.loadingLbl.pack(fill=tk.X, expand=False, padx=10, pady=10)
        self.update_lbl.append(self.loadingLbl)
        self.update_accent_foreground.append(self.loadingLbl)
        self.update_text_font[self.loadingLbl] = (
            self.theme.get('font'),
            18
        )
        
        self.questions = loadQuestions()
        
        self.loadingLbl.config(text="Inserting questions into UI...")
        
        for i in self.questions:
            tempQuestionLbl = tk.Label(
                self.frame, 
                text=f"Question #{dict_getIndex(self.questions, i, 1, True)}:\n{i.strip()}",
                anchor=tk.W,
                justify=tk.LEFT,
                wraplength=int((int(self.ws[0] - self.ws[0]*0.02)))
            )
            
            tempQuestionLbl.pack(fill=tk.BOTH, expand=False, padx=10, pady=(15, 5))
            
            self.update_lbl.append(tempQuestionLbl)
            self.update_text_font[tempQuestionLbl] = (self.theme.get('font'), 14)
            
            tempAnswerLbl = tk.Label(
                self.frame,
                text=f"Answer: {self.questions.get(i).strip()}",
                anchor=tk.W,
                justify=tk.LEFT,
                wraplength=int((int(self.ws[0] - self.ws[0]*0.08)))
            )
            
            tempAnswerLbl.pack(fill=tk.BOTH, expand=False, padx=10, pady=(1, 1))

            remButton = tk.Button(
                self.frame,
                text="Remove Question",
                fg=self.theme.get('fg'),
                bg=self.theme.get('bg'),
                activebackground="red",
                activeforeground="white",
                bd=0,
                anchor=tk.SW
            )
            remButton.pack(
                fill=tk.BOTH,
                expand=False,
                padx=10,
                pady=(0, 10)
            )

            self.config_rm_button(remButton, i)

            self.update_lbl.append(tempAnswerLbl)
            self.update_text_font[tempAnswerLbl] = (self.theme.get('font'), 14)
            self.update_accent_foreground.append(tempAnswerLbl)
            
            # sep = ttk.Separator(self.frame)
            # sep.pack(fill=tk.X, expand=True)
            
        self.loadingLbl.config(text="Completed loading process...")
        self.loadingLbl.pack_forget()
        
        # ttk :: SB conf. (After widget placement)
        self.vsb.configure(command=self.canv.yview)
        self.xsb.configure(command=self.canv.xview)
        
        self.canv.configure(
            yscrollcommand=self.vsb.set,
            xscrollcommand=self.xsb.set
        )
        
        self.canv.create_window(
            (0,0),
            window=self.frame,
            anchor="nw",
            tags="self.frame"
        )
        
        # Event Handlers
        self.frame.bind("<Configure>", self.onFrameConfig)
        self.frame.bind_all("<MouseWheel>", self._on_mousewheel)
        # Final things
        self.update()

    def config_rm_button(self, tkButton, question):
        qId = (random.randint(0, 9999999999999999) + random.random()) * random.randint(1, 99)

        counter = 0
        while qId in self.id_assign:
            counter += 1
            qId = (random.randint(0, 9999999999999999) + random.random()) * random.randint(1, 99)
            if counter > 10000000:
                break

        self.id_assign[qId] = question.strip()

        tkButton.config(
            command=lambda: self.rm_q(qId)
        )

    def _on_mousewheel(self, event):
        """
        Straight out of stackoverflow
        Article: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
        Change
        : added "int" around the first arg
        """
        self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def onFrameConfig(self, event): # for scbar
        self.canv.configure(
            scrollregion=self.canv.bbox("all")
        )

        self.ws = [
            self.root.winfo_width(),
            self.root.winfo_height()
        ]
    
    def rm_q(self, ID) -> None:
        question = self.id_assign[ID]

        conf = tkmsb.askyesno("Confirm Removal", "Are you sure you want to remove the following question:\n\n'{}'".format(question))
        if not conf: return

        self.questions.pop(question)
        
        # Save
        save: str = QAQuestionStandard.dictToSaveStr(self.questions)
        io = IO(f"{QAInfo.appdataLoc}\\{QAInfo.qasFilename}", encrypt=True)
        io.save(save)
        
        # Reset UI
        children = self.frame.winfo_children()
        for i in children: i.pack_forget()
        
        self.run()
        
    def update_theme(self):
        self.theme = QATheme.Get().get('theme')
        
        self.root.config(
            bg=self.theme.get('bg')
        )

        self.vsb_style.configure(
            "TScrollbar",
            background=self.theme.get('bg'),
            arrowcolor=self.theme.get('fg'),
            bordercolor=self.theme.get('bg'),
            troughcolor=self.theme.get('bg')
        )

        self.vsb_style.map(
            "TScrollbar",
            background=[
                ("active", self.theme.get('ac')), ('disabled', self.theme.get('bg'))
            ]
        )

        # ttk::style configure TSeparator -background color
        self.sepStyle.configure(
            "TSeparator",
            background=self.theme.get('bg')
        )
        
        self.canv.config(
            bg=self.theme.get('bg'),
            bd=0
        )

        self.frame.config(
            bg=self.theme.get('bg')
        )
        
        for i in self.update_lbl:
            i.config(
                bg=self.theme.get('bg'),
                fg=self.theme.get('fg')
            )
            
        for i in self.update_accent_foreground:
            i.config(
                fg=self.theme.get('ac')
            )
        
        for i in self.update_text_font:
            i.config(
                font=self.update_text_font[i]
            )
        
    def update(self):
        self.update_theme()

def KWARGS(Object: object, call: str, flags: dict = {}, **kwargs) -> any: # KWARGS :: Object-Oriented flag handler (rev2)
    chKey = "c"; fHKey = "f"
    call = call.lower().strip()
    
    def flagsHandler(Object: object, kwargs: dict, __raiseErr: bool = True, __ignoreLen: bool = True):

        if len(kwargs) <= 0 and not __ignoreLen: return # Do not waste time
        # Actual - Filters
        ac_ks = [i.strip() for i in Object.flagsHandlerDict.keys()] # str
        ac_vs = [i for i in Object.flagsHandlerDict.values()] # list
        ac_fs = {ac_ks[i]: ac_vs[i] for i in range(0, len(ac_ks))} # Flags
        
        # Given - Filters
        g_ks = [i.strip() for i in kwargs.keys()] # str
        g_vs = [i for i in kwargs.values()] # list
        g_fs = {g_ks[i]: g_vs[i] for i in range(0, len(g_ks))} # Flags
        
        # Output
        out = ac_fs # Set all other flags automatically
        
        # Logic
        for i in g_fs:
            if not i in ac_fs and __raiseErr: raise QAExceptions.QA_InvalidFlag(f"Invalid flag name '{i}'")
            else:
                if not type(g_fs.get(i)) in ac_fs.get(i)[-1]:
                    raise QAExceptions.QA_InvalidFlag(f"Invalid data type {type(g_fs.get(i))} for flag '{i}'; expected one of: {ac_fs.get(i)[-1]}")
                
                else:
                    out[i] = [g_fs.get(i), ac_fs[i][-1]] # Reconstruct the specific flag with the new data
                    
        # Set
        # Flags for this function:
        Object.flagsHandlerDict = out
        
        # Plain + Set
        plain = {
            i: out[i][0] for i in out
        }; Object.flags = plain
        
        print((out, plain))
        
        return (out, plain) # Tuple; cannot change
                    
    if call == chKey:
        # change(Object, kwargs)
        return flagsHandler(Object, kwargs)
        
    elif call == fHKey:
        return flagsHandler(Object, flags)
        
    else:
        return {
            "change": chKey,
            "flagsHandler": fHKey
        }

def loadQuestions(__r=True) -> dict:
    out: dict = {}
    path = f"{QAInfo.appdataLoc}\\{QAInfo.qasFilename}"
    
    if not os.path.exists(path): return {"No questions found": "No answers found"} if __r else {}
    
    __io = IO(path)
    __raw = __io.autoLoad()
    
    out = QAQuestionStandard.convRawToDict(__raw)
    
    if len(out) <= 0: out = {"No questions found": "No answers found"} if __r else {}
    
    return out

def dict_getIndex(dictionary: dict, key: str, add: int = 0, changeToStr: bool = False):
    ind = None
    ls: list = [i.strip() for i in dictionary.keys()]
    
    for i in dictionary:
        try:
            if i.strip() == key.strip():
                ind = ls.index(i)
                break
            
        except: pass
    
    if ind is not None: ind += add
    elif changeToStr: ind = " << Unknown Index >> "
    
    return ind

if __name__ == "__main__":
    UI()
