import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsb
import threading, os, sys

import qa_theme as QATheme
import qa_appinfo as QAInfo
import qa_fileIOHandler as QAFileIO
import qa_questions as QAQuestionStandard

class UI(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        
        self.theme = QATheme.Get().get('theme')
        
        self.root = tk.Toplevel()
        
        self.vsb_style = ttk.Style()
        self.vsb_style.theme_use('default')
        
        self.sep_style = ttk.Style()
        self.sep_style.theme_use('default')
        
        self.canv = tk.Canvas(self.root)
        self.frame = tk.Frame(self.root)
        self.vsb = ttk.Scrollbar(self.root)
        
        self.question_entry = tk.Text(self.frame); self.questionLbl = tk.Label(self.frame, text="Enter Question")
        self.answer_entry = tk.Text(self.frame); self.answerLbl = tk.Label(self.frame, text="Enter Correct Answer")

        self.selContainer = tk.LabelFrame(self.frame, bd='0', bg=self.theme.get('bg'))
        self.mcSel = tk.Button(self.selContainer, text="Multiple Choice", command=self.mc_click)
        self.tfSel = tk.Button(self.selContainer, text="True/False", command=self.tf_click)
        self.submitButton = tk.Button(self.frame, text="Add Question", command=self.add)
        
        self.clearButton = tk.Button(self.frame, text="Delete All Questions", command=self.delAll)
        self.helpButton = tk.Button(self.frame, text="Click here to\n view instructions", command=self.help)
        
        self.sep = ttk.Separator(self.frame)
        
        self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())
        self.ws = [680, 800]
        self.wp = [
            int(self.ss[0]/2 - self.ws[0]/2),
            int(self.ss[1]/2 - self.ws[1]/2)
        ]
        
        # Theme data sets
        self.theme_label: list = []
        self.theme_label_font: dict = {}
        self.theme_button: list = []
        self.theme_accent: list = []

        self.mc = False
        self.tf = False

        self.start()
        self.root.mainloop()
        
    def run(self):
        # Root configuration
        self.root.geometry(f"{self.ws[0]}x{self.ws[1]}+{self.wp[0]}+{self.wp[1]}")
        self.root.resizable(False, True)
        self.root.minsize(self.ws[0], int(self.ws[1]/2))
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.title("Add Question")
        self.root.iconbitmap(QAInfo.icons_ico.get('admt'))
        
        # Widget configuration + placement
        # The basic back
        self.canv.pack(fill=tk.BOTH, expand=1, side=tk.LEFT)
        self.vsb.pack(fill=tk.Y, expand=False, side=tk.RIGHT)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # The actual control
        
        ttl = tk.Label(self.frame, text="Add Question")
        ttl.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        self.theme_label.append(ttl)
        self.theme_accent.append(ttl)
        self.theme_label_font[ttl] = (
            self.theme.get('font'),
            32
        )
        
        self.helpButton.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        self.theme_button.append(self.helpButton)
        self.theme_label_font[self.helpButton] = (
            self.theme.get('font'),
            16
        )
        
        self.sep.pack(fill=tk.X, expand=True, padx=5) 
        
        self.questionLbl.config(anchor=tk.SW)
        self.theme_label.append(self.questionLbl)
        self.theme_accent.append(('bg', self.theme.get('bg'), self.questionLbl))
        
        self.questionLbl.pack(fill=tk.X, expand=True, padx=10, pady=(5, 0))
        self.question_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
        
        self.answerLbl.config(anchor=tk.SW)
        self.theme_label.append(self.answerLbl)
        self.theme_accent.append(('bg', self.theme.get('bg'), self.answerLbl))
        
        self.answerLbl.pack(fill=tk.X, expand=True, padx=10)
        self.answer_entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        self.selContainer.pack(fill=tk.BOTH, expand=True, padx=10)
        self.mcSel.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=(0, 5), side=tk.LEFT)
        self.tfSel.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=(5, 0), side=tk.RIGHT)
        self.theme_button.append(self.mcSel)
        self.theme_button.append(self.tfSel)
        self.theme_label_font[self.mcSel] = (
            self.theme.get('font'),
            14
        )
        self.theme_label_font[self.tfSel] = (
            self.theme.get('font'),
            14
        )
        
        self.submitButton.pack(
            fill=tk.BOTH,
            expand=True,
            padx=(10, 5),
            pady=(0, 5),
            side=tk.LEFT
        )
        self.theme_button.append(self.submitButton)        
        self.theme_label_font[self.submitButton] = (
            self.theme.get('font'),
            14
        )
        
        self.clearButton.pack(
            fill=tk.BOTH,
            expand=True,
            padx=(10, 5),
            pady=(0, 5),
            side=tk.RIGHT
        )
        self.theme_label_font[self.clearButton] = (
            self.theme.get('font'),
            14
        )
        
        # ttk :: SB conf. (After widget placement)
        self.vsb.configure(command=self.canv.yview)
        
        self.canv.configure(
            yscrollcommand=self.vsb.set
        )
        
        self.canv.create_window(
            (0,0),
            window=self.frame,
            anchor="nw",
            tags="self.frame"
        )
        
        # Final Things
        self.update()
        
        # Event Handlers
        self.frame.bind("<Configure>", self.onFrameConfig)
        self.frame.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        """
        Straight out of stackoverflow
        Article: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
        Change
        : added "int" around the first arg
        """
        # self.canv.yview_scroll(int(-1 * (event.delta / 120)), "units")
        pass
    
    def onFrameConfig(self, event): # for scbar
        self.canv.configure(
            scrollregion=self.canv.bbox("all")
        )
        
    def close(self):
        if __name__ == "__main__":
            sys.exit("WM_DELETE_WINDOW")
        else:
            self.root.after(0, self.root.destroy)
            return
    
    def update_theme(self):
        # Pre
        QATheme.Get().refresh_theme()
        self.theme = QATheme.Get().get('theme')
        
        # TTK
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

        self.sep_style.configure(
            "TSeparator",
            background=self.theme.get('fg')
        )
        
        # TK
        self.root.config(
            bg=self.theme.get('bg')
        )
        
        self.canv.config(
            bg=self.theme.get('bg')
        )
        
        self.frame.config(
            bg=self.theme.get('bg')
        )
        
        self.question_entry.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg')
        )
        
        self.answer_entry.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg')
        )
        
        # self.theme_label: list = []
        # self.theme_label_font: dict = {}
        # self.theme_button: list = []
        # theme_accent: list = []
        
        for i in self.theme_label:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg')
                )
            
            except: print('sdfsjhfhsdf', i)
            
        for i in self.theme_label_font:
            try:
                i.config(
                    font=self.theme_label_font.get(i)
                )

            except:
                print('sdfsasdjhfhsdf', i)
            
        for i in self.theme_button:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg'),
                    activebackground=self.theme.get('ac'),
                    activeforeground=self.theme.get('hg'),
                    bd=0
                )

            except: print('sdfsassdfdjhfhsdf', i)

        for i in self.theme_accent:
            try:
                if type(i) is tuple or type(i) is list:
                    
                    if i[0] == 'bg':
                        i[-1].config(
                            bg=self.theme.get('ac'),
                            fg=i[1]
                        )

                else:
                    i.config(
                        fg=self.theme.get('ac')
                    )

            except: print('sdfsjhsdffhsdf', i)
        
        # Exceptions
        self.clearButton.config(
            bg="red",
            fg="white",
            activebackground="white",
            activeforeground="red",
            bd=0
        )    

        self.question_entry.config(
            selectbackground=self.theme.get('ac'),
            selectforeground=self.theme.get('hg'),
            wrap=tk.WORD,
            font=(
                self.theme.get('font'),
                11
            )
        )

        self.answer_entry.config(
            selectbackground=self.theme.get('ac'),
            selectforeground=self.theme.get('hg'),
            wrap=tk.WORD,
            font=(
                self.theme.get('font'),
                11
            )
        )

    def update(self):
        self.update_theme()
    
    # Event Handlers
    
    # Button Handlers
    
    def help(self):
        pdf = QAInfo.QA_ENTRY_HELP
        os.startfile(f"\"{pdf}\"")

    def reformat_buttons(self):
        self.mcSel.config(
            bg=self.theme.get('ac' if self.mc else 'bg'),
            fg=self.theme.get('hg' if self.mc else 'fg'),
            text=(
                    self.mcSel.cget('text').replace('\u2713', '').strip() + (' \u2713' if self.mc else '')
            )
        )

        self.tfSel.config(
            bg=self.theme.get('ac' if self.tf else 'bg'),
            fg=self.theme.get('hg' if self.tf else 'fg'),
            text=(
                    self.tfSel.cget('text').replace('\u2713', '').strip() + (' \u2713' if self.tf else '')
            )
        )

    def mc_click(self):
        self.mc = not self.mc
        self.tf = False if self.mc else self.tf

        self.reformat_buttons()

    def tf_click(self):
        self.tf = not self.tf
        self.mc = False if self.tf else self.mc

        self.reformat_buttons()

    def delAll(self):
        conf = tkmsb.askyesno("Delete All Questions", "Are you sure you want to delete all questions? This process cannot be undone.")
        if not conf: return

        file = "{}\\{}".format(
            QAInfo.appdataLoc,
            QAInfo.qasFilename
        )
        IO(file, append=False, encrypt=True).save('')

        tkmsb.showinfo("Deleted All Questions", "Successfully deleted all questions.")

    def add(self):

        data = QAQuestionStandard.convertToQuestionStr(
            ((QAInfo.QAS_MCCode if self.mc else QAInfo.QAS_TFCode if self.tf else "") + self.question_entry.get("1.0", "end-1c")).strip(),
            self.answer_entry.get("1.0", "end-1c").strip()
        )

        file = "{}\\{}".format(
            QAInfo.appdataLoc,
            QAInfo.qasFilename
        )

        IO(file, encrypt=True, append=True, append_sep="\n").save(data)

        self.submitButton.config(
            state=tk.DISABLED,
            disabledforeground="#595959"
        )

        self.clearButton.config(
            state=tk.DISABLED,
            background=self.theme.get('bg'),
            disabledforeground="#595959"
        )

        self.helpButton.config(
            state=tk.DISABLED,
            background=self.theme.get('bg'),
            disabledforeground="#595959"
        )

        tkmsb.showinfo("QAS", "Added question successfully")

        self.close()

    def __del__(self):
        self.thread.join(0, self)


class IO:
    def __init__(self, fn: str, **kwargs):
        self.filename = fn
        self.object = QAFileIO.create_fileIO_object(self.filename)

        self.flagsHandlerDict = {
            'append': [False, (bool,)],
            'append_sep': ["\n", (str, bytes)],
            'suppressError': [False, (bool,)],
            'encoding': ['utf-8', (str,)],
            'encrypt': [False, (bool,)]
        }

        print(kwargs)

        self.flags = {};
        KWARGS(self, 'f', flags=kwargs)

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


def KWARGS(Object: object, call: str, flags: dict = {},
           **kwargs) -> any:  # KWARGS :: Object-Oriented flag handler (rev2)
    chKey = "c";
    fHKey = "f"
    call = call.lower().strip()

    def flagsHandler(Object: object, kwargs: dict, __raiseErr: bool = True, __ignoreLen: bool = True):

        if len(kwargs) <= 0 and not __ignoreLen: return  # Do not waste time
        # Actual - Filters
        ac_ks = [i.strip() for i in Object.flagsHandlerDict.keys()]  # str
        ac_vs = [i for i in Object.flagsHandlerDict.values()]  # list
        ac_fs = {ac_ks[i]: ac_vs[i] for i in range(0, len(ac_ks))}  # Flags

        # Given - Filters
        g_ks = [i.strip() for i in kwargs.keys()]  # str
        g_vs = [i for i in kwargs.values()]  # list
        g_fs = {g_ks[i]: g_vs[i] for i in range(0, len(g_ks))}  # Flags

        # Output
        out = ac_fs  # Set all other flags automatically

        # Logic
        for i in g_fs:
            if not i in ac_fs and __raiseErr:
                raise QAExceptions.QA_InvalidFlag(f"Invalid flag name '{i}'")
            else:
                if not type(g_fs.get(i)) in ac_fs.get(i)[-1]:
                    raise QAExceptions.QA_InvalidFlag(
                        f"Invalid data type {type(g_fs.get(i))} for flag '{i}'; expected one of: {ac_fs.get(i)[-1]}")

                else:
                    out[i] = [g_fs.get(i), ac_fs[i][-1]]  # Reconstruct the specific flag with the new data

        # Set
        # Flags for this function:
        Object.flagsHandlerDict = out

        # Plain + Set
        plain = {
            i: out[i][0] for i in out
        };
        Object.flags = plain

        print((out, plain))

        return (out, plain)  # Tuple; cannot change

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

if __name__ == "__main__":
    UI()
