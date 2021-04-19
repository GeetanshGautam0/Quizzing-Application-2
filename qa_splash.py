import os
from PIL import Image as PILImage, ImageTk as PILImageTk
from tkinter import *
import tkinter.ttk as ttk

import qa_appinfo as QAInfo


# theme = QATheme.Get().get('theme')

theme = {
    # Credit
    'Credit': 'Geetansh Gautam, Coding Made Fun',

    # Font
    'font': 'Century Gothic', # Font Face
    'fsize_para': 10, # Paragraph font size
    'sttl_base_fsize': 18, # Subtitle base font size
    'btn_fsize': 13, # Button Font Size
    'min_fsize': 10, # Minimum Font Size

    # Color
    'bg': '#ffffff', # Background
    'fg': '#000000', # Main foreground
    'ac': '#000000', # Accent Color
    'hg': '#ffffff', # Highlight color (back of fields)
    'border_color': '#ffffff', # Border color for buttons

    # Misc
    'border': '0' # Border width
}

class Splash(Toplevel):
    def __init__(self, master=None):
        global theme; self.theme = theme
        
        # UI Vars
        self.imgSize = (40, 40)
        
        self.pbarStyle = ttk.Style()
        self.pbarStyle.theme_use('default')
        
        self.root = master
        self.frame = Frame(self.root)
        
        self.geo = "600x225+{}+{}".format(
            int(self.root.winfo_screenwidth()/2 - 300),
            int(self.root.winfo_screenheight()/2 - 125)
        )
        
        self.root.geometry(self.geo)
        
        self.titleLbl = Label(self.frame)
        self.imgLbl = Button(self.frame, anchor=NE)
        self.pbar = ttk.Progressbar(self.frame,length=100, mode='determinate', orient=HORIZONTAL)
        self.infoLbl = Label(self.frame, justify=LEFT)
        
        self.title = "Quizzing Application"
        self.information = "Loading...\n\nCoding Made Fun"
        self.img = os.path.abspath(f"{QAInfo.icons_png['qt']}").replace('/', '\\')

        self.ac_start = "#000000"
        self.ac_end = "#00aeae"
        self.loadGrad = True
        self.grad = ["#000000"]
        self.complete = False

        self.pbarStyle.configure(
            "Horizontal.TProgressbar",
            foreground=self.grad[0],
            background=self.grad[0],
            troughcolor=self.theme.get('bg'),
            borderwidth=0,
            thickness=2
        )

        # UI Config
        self.run()

        # UI Update
        self.root.update()
    
    def run(self):
        self.root.overrideredirect(True)
        self.root.protocol("WM_DELETE_WINDOW", lambda: destroy(self))
        self.root.wm_attributes('-topmost', 1)
        
        ico = self.img.replace('.png', '.ico')
        self.root.iconbitmap(ico)
        
        self.frame.pack(fill=BOTH, expand=True)
        self.frame.config(bg=self.theme.get('bg'))
        
        image = PILImageTk.PhotoImage(PILImage.open(self.img).resize(self.imgSize), master=self.root)
        self.imgLbl.configure(
            image=image, 
            bg=self.theme.get('bg'), 
            command=sys.exit,
            bd=0,
            activebackground=self.theme.get('bg')
        )
        self.imgLbl.image = image
        
        self.titleLbl.config(text=self.title, bg=self.theme.get('bg'), fg=self.theme.get('ac'), font=(self.theme.get('font'), 36), anchor=SW)
        self.infoLbl.config(text=self.information, bg=self.theme.get('bg'), fg=self.theme.get('fg'), font=(self.theme.get('font'), self.theme.get('fsize_para')), anchor=NW)
        
        # self.imgLbl.pack(fill=BOTH, expand=True, padx=5, pady=5)
        self.titleLbl.pack(fill=BOTH, expand=True, padx=5)
        self.pbar.pack(fill=X, expand=1)
        self.infoLbl.pack(fill=X, expand=True, padx=5)

        self.root.update()
    
    def completeColor(self) -> None:
        import qa_theme as QATheme
        compTheme = QATheme.Get().get('theme')
        self.complete = True

        self.pbarStyle.configure(
            "Horizontal.TProgressbar",
            foreground=compTheme.get('ac'),
            background=compTheme.get('ac'),
            troughcolor=self.theme.get('bg')
        )
        self.titleLbl.config(
            fg=compTheme.get('ac'),
            bg=compTheme.get('bg')
        )
        self.frame.config(
            bg=compTheme.get('bg')
        )
        self.infoLbl.config(
            bg=compTheme.get('bg'),
            fg=compTheme.get('fg')
        )
        
        self.imgLbl.pack_forget()
        
        self.root.update()
    
    def setImg(self, img) -> None:
        self.img = img
        image = PILImageTk.PhotoImage(PILImage.open(self.img).resize(self.imgSize), master=self.root)
        self.imgLbl.configure(
            image=image
        )
        self.imgLbl.image = image
        self.root.update()
    
    def changePbar(self, per: float) -> None:
        if self.loadGrad:
            import qa_colors as QAColors
            self.grad = QAColors.monoFade(self.ac_start, self.ac_end, 0, 4, 4)
            self.loadGrad = False

        self.pbar['value'] = per

        if not self.complete:
            self.pbarStyle.configure(
                "Horizontal.TProgressbar",
                background=self.grad[int((len(self.grad) - 1) * (per/100)*0.8)],
                foreground=self.grad[int((len(self.grad) - 1) * (per/100)*0.8)],
                troughcolor=self.theme.get('bg')
            )
            self.titleLbl.config(fg=self.grad[int((len(self.grad) - 1) * per/100)])

        self.pbar.configure(
            style="Horizontal.TProgressbar"
        )

        self.root.update()
        
    def setInfo(self, text) -> None:
        self.information = text.strip()
        self.infoLbl.config(text=self.information)
        self.root.update()
    
    def setTitle(self, text: str) -> None:
        # self.title = text.replace(' ', '\n')
        self.title = text.strip()
        self.titleLbl.config(text=self.title)
        self.root.update()
    
    def update(self) -> None:
        self.root.update()

def Pass(): pass

def hide(__inst: object):
    __inst.root.overrideredirect(False)
    __inst.root.wm_attributes("-topmost", 0)
    __inst.root.iconify()
    __inst.root.withdraw()
    __inst.root.update_ui()
    return

def show(__inst: object):
    __inst.root.overrideredirect(True)
    __inst.root.deiconify()
    __inst.root.wm_attributes("-topmost", 1)
    __inst.root.update_ui()
    return

def destroy(__inst: object):
    __inst.root.after(0, __inst.root.destroy)
    return
