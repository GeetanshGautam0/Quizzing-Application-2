import os, sys, ctypes, threading, shutil, traceback
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as tkmsb
import qa_appinfo as QAInfo
import qa_errors as QAErrors
import qa_time as QATime
import installer_options as IOptions

# Globals
apptitle = "QA Secondary Installer"
logFn = os.path.join(QAInfo.appdataLoc, IOptions.log_file_name)
ui = None
ui_est = False
icon = QAInfo.icons_ico['installer']


class UI(threading.Thread):

    def __init__(self):
        global apptitle

        self.thread = threading.Thread
        self.thread.__init__(self)

        self.root = tk.Toplevel()
        self.root_img_frame = tk.Label(self.root)
        self.main_content_frame = tk.Frame(self.root)

        self.padX = 20
        self.padY = self.padX/2

        self.canClose = True
        self.theme = load_theme()
        log("THEME_LOADED: ", self.theme)

        self.res = [(700 / 1920), (350 / 1080), 1.1]
        self.ws = [
            int(self.res[0] * self.root.winfo_screenwidth() * self.res[2]),
            int(self.res[1] * self.root.winfo_screenheight() * self.res[2])
        ]
        self.sp = (int(self.root.winfo_screenwidth() / 2 - self.ws[0] / 2),
                   int(self.root.winfo_screenheight() / 2 - self.ws[1] / 2))

        log("RES: ", self.res, "; WS: ", (*self.ws,), "; SP: ", self.sp)

        self.pbarStyle = ttk.Style()
        self.sb_style = ttk.Style()
        self.pbarStyle.theme_use('default')

        self.start_button = tk.Button(self.root)

        self.lb = tk.Listbox(self.main_content_frame)
        self.lb_vsb = ttk.Scrollbar(self.main_content_frame)
        self.lb_xsb = ttk.Scrollbar(self.main_content_frame, orient=tk.HORIZONTAL)

        self.title_lbl = tk.Label(self.main_content_frame)
        self.info_lbl = tk.Label(self.main_content_frame)
        self.pbar_info_lbl = tk.Label(self.main_content_frame)
        self.pbar_curr = ttk.Progressbar(self.main_content_frame)
        self.pbar_total = ttk.Progressbar(self.main_content_frame)

        self.rootTitle = apptitle + (" - Admin Mode" if is_admin() else " - Cannot Install Icon Files")

        self.btn_fsize = 13
        self.lb_counter = 0

        self.start()
        self.root.mainloop()

    def run(self):
        global icon, apptitle

        self.root.title(apptitle)
        self.root.geometry("%sx%s+%s+%s" % (
            self.ws[0], self.ws[1],
            self.sp[0], self.sp[1]
        ))
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.resizable(False, False)
        self.root.lift()
        self.root.iconbitmap(icon)

        self.start_button.config(text="Start Secondary\nInstallation", command=self.install)
        #  self.start_button.pack(fill=tk.BOTH, padx=(self.padX * 1.5, 0), pady=self.padX * 1.5, side=tk.LEFT, ipadx=self.padX/4)
        self.start_button.pack(fill=tk.BOTH, side=tk.LEFT)
        self.update_element_theme(self.start_button, 'button',
                                  font=(self.theme.get('font'), self.btn_fsize),
                                  fg=self.theme.get('hg'),
                                  bg=self.theme.get('ac'),
                                  ab=self.theme.get('hg'),
                                  af=self.theme.get('ac')
                                  )

        self.main_content_frame.config(bg=self.theme.get('bg'))
        #  self.main_content_frame.pack(fill=tk.BOTH, expand=True, padx=(0, self.padX * 1.5), pady=self.padX * 1.5, side=tk.RIGHT)
        self.main_content_frame.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)

        self.title_lbl.config(text="QA Secondary Installer", anchor=tk.NW, justify=tk.LEFT)
        self.title_lbl.pack(fill=tk.BOTH, padx=self.padX, pady=(self.padY, 0))
        self.update_element_theme(self.title_lbl, 'label', font=(self.theme.get('font'), 24), fg=self.theme.get('ac'))

        self.info_lbl.config(text="Please click 'Start Secondary Installation' to continue.", anchor=tk.NW, justify=tk.LEFT)
        self.info_lbl.pack(fill=tk.BOTH, padx=self.padX)
        self.update_element_theme(self.info_lbl, 'label', font=(self.theme.get('font'), 12))

        self.pbar_total['value'] = 0
        self.pbar_curr['value'] = 0

        self.pbar_total.pack(fill=tk.X, padx=self.padX, pady=(self.padY/2, self.padY), side=tk.BOTTOM)
        self.pbar_curr.pack(fill=tk.X, padx=self.padX, side=tk.BOTTOM)

        self.pbar_info_lbl.config(text="", wraplength=int(self.ws[0]-2*self.padX))
        self.pbar_info_lbl.pack(fill=tk.X, padx=self.padX, pady=(self.padY/2, self.padY), side=tk.BOTTOM)
        self.update_element_theme(self.pbar_info_lbl, 'label', font=(self.theme.get('font'), 10))

        self.update_element_theme(None, None)  # all the exceptions

    def update_element_theme(self, element, el_type, *args, **kwargs):
        if el_type == 'button':
            element.config(
                bd='0' if kwargs.get('bd') is None else str(kwargs.get('bd')),
                bg=self.theme.get('bg') if kwargs.get('bg') is None else str(kwargs.get('bg')),
                fg=self.theme.get("fg") if kwargs.get('fg') is None else str(kwargs.get('fg')),
                activebackground=self.theme.get('ac') if kwargs.get('ab') is None else str(kwargs.get('ab')),
                activeforeground=self.theme.get('hg') if kwargs.get('af') is None else str(kwargs.get('af'))
            )

        elif el_type == 'label':
            element.config(
                bg=self.theme.get('bg') if kwargs.get('bg') is None else kwargs.get('bg'),
                fg=self.theme.get('fg') if kwargs.get('fg') is None else kwargs.get('fg')
            )

        if type(kwargs.get('font')) is tuple:
            element.config(font=kwargs.get('font'))

        if element is None and el_type is None:
            self.root.config(bg=self.theme.get('ac'))

            self.lb.config(
                bg=self.theme.get('bg'),
                fg=self.theme.get('fg'),
                font=(self.theme.get('font'), self.theme.get('fsize_para')),
                selectmode=tk.EXTENDED,
                selectbackground=self.theme.get('ac'),
                selectforeground=self.theme.get('hg')
            )

            self.pbarStyle.configure(
                "Horizontal.TProgressbar",
                foreground=self.theme.get('ac'),
                background=self.theme.get('ac'),
                troughcolor=self.theme.get('bg'),
                borderwidth=0,
                thickness=15
            )

            self.sb_style.configure(
                "TScrollbar",
                background=self.theme.get('bg'),
                arrowcolor=self.theme.get('fg'),
                bordercolor=self.theme.get('bg'),
                troughcolor=self.theme.get('bg')
            )

            self.sb_style.map(
                "TScrollbar",
                background=[
                    ("active", self.theme.get('ac')), ('disabled', self.theme.get('bg'))
                ]
            )

    def install(self):
        global logFn

        self.canClose = False
        self.start_button.pack_forget()
        self.main_content_frame.pack_forget()
        self.main_content_frame.pack(fill=tk.BOTH, expand=True)

        self.info_lbl.config(text="Setting Up")
        self.root.title(self.rootTitle)

        self.lb_xsb.pack(fill=tk.X, expand=True, padx=(self.padX, self.padX), pady=(0, self.padY), side=tk.BOTTOM)
        self.lb.pack(
            fill=tk.BOTH,
            expand=True,
            padx=(self.padX, 0),
            pady=(self.padY, 0),
            side=tk.LEFT
        )
        self.lb_vsb.pack(fill=tk.Y, padx=(0, self.padX), pady=(self.padY, 0), side=tk.RIGHT)

        self.lb.config(yscrollcommand=self.lb_vsb.set, xscrollcommand=self.lb_xsb.set)
        self.lb_vsb.config(command=self.lb.yview)
        self.lb_xsb.config(command=self.lb.xview)

        self.root.update()

        divs = 3 if is_admin() else 2

        # Remove old files
        ap_o = os.listdir(QAInfo.appdataLoc)
        self.insert_into_lb("Removing old files (if any)")
        for i in ap_o:
            try:
                self.progress_bar_set(
                    ap_o.index(i),
                    divs, 0,
                    ap_o.index(i)+1, len(ap_o),
                    res=1, multiplier=100)

                path = os.path.join(QAInfo.appdataLoc, i)

                if i == logFn or path == logFn:
                    self.insert_into_lb(f"Skipped {i}")
                    continue

                if os.path.isfile(path):
                    os.remove(path)
                    log(f"REMOVED {path}")
                    self.lb_show_ok(
                        self.insert_into_lb(f"Removed {i}")
                    )

                elif os.path.isdir(path):
                    shutil.rmtree(path)
                    log(f"REMOVED {path} (DIR/TREE)")
                    self.lb_show_ok(
                        self.insert_into_lb(f"Removed {i}")
                    )

                else:
                    raise Exception("Cannot resolve file type")

            except Exception as E:
                self.lb_show_error(
                    self.insert_into_lb(f"Failed to remove {i}")
                )
                log(f"ERROR WHILST CLEARING FILE/DIR {i}: ", E, " TB: ", traceback.format_exc())
                pass

        self.pbar_curr['value'] = 0
        self.pbar_total['value'] = (1/divs) * 100
        self.insert_into_lb("")
        self.insert_into_lb("Creating new files")

        for i in QAInfo.QaFTSRAFiles:
            self.progress_bar_set(
                QAInfo.QaFTSRAFiles.index(i),
                divs, 1,
                QAInfo.QaFTSRAFiles.index(i) + 1, len(QAInfo.QaFTSRAFiles),
                res=1, multiplier=100)

            if i not in os.listdir(QAInfo.ftsFolder):
                self.lb_show_error(
                    self.insert_into_lb(f"File {i} not found; installation may be corrupted.")
                )

                continue

            src_path = os.path.join(QAInfo.ftsFolder, i)
            dst_path = os.path.join(QAInfo.appdataLoc, i)

            if os.path.isfile(src_path):
                with open(src_path, 'rb') as src, open(dst_path, 'wb') as dst:
                    dst.write(src.read())

                    src.close()
                    dst.close()

                self.lb_show_ok(
                    self.insert_into_lb(f"Created {i}.")
                )

            else:
                self.insert_into_lb(f"Skipped {i}")

        try:
            if not os.path.exists(os.path.join(QAInfo.appdataLoc, QAInfo.scoresFolderName)):
                os.makedirs(os.path.join(QAInfo.appdataLoc, QAInfo.scoresFolderName))

            self.lb_show_ok(
                self.insert_into_lb(f"Created Scores folder.")
            )

        except:
            self.lb_show_error(
                self.insert_into_lb(f"Failed to create Scores folder.")
            )

            self.canClose = True
        
        # When done
        self.pbar_curr['value'] = 0
        self.pbar_total['value'] = 100
        self.pbar_info_lbl.config(text="Completed")

        if is_admin():
            self.lb_show_ok(
                self.insert_into_lb(
                    "UAC elevation granted; setting file icons."
                )
            )

            os.system("{}".format(QAInfo.icons_regFile))

            self.lb_show_ok(
                self.insert_into_lb(
                    "Set icons; will sign out now."
                )
            )

            tkmsb.showwarning(
                apptitle,
                "You will be SIGNED OUT as soon as you click 'OK'; all unsaved work will be lost;\n\nPlease save all your work and only then click 'OK.'"
            )

            os.system("shutdown -l")

        else:
            self.lb_show_error(
                self.insert_into_lb(
                    "Cannot set associated file icons because UAC elevation was not provided."
                )
            )

            tkmsb.showerror(apptitle, "Cannot set associated file icons because UAC elevation (admin privileges) was not provided.\n\nNote that the application can run nominally without these icons.")

        self.canClose = True

        return None

    def clear_lb(self):
        self.lb_counter = 0

        self.lb.delete(0, tk.END)

    def insert_into_lb(self, string, index: int = tk.END) -> int:
        string = str(string)
        self.lb_counter += 1

        self.lb.insert(index, string)
        self.lb.yview(tk.END)
        self.root.update()

        return self.lb_counter - 1

    def lb_show_ok(self, index: int):
        if index < 0 or index > self.lb_counter: return

        self.lb.itemconfig(
            index,
            background="#ffffff", foreground="#00802b",
            selectbackground="#00802b",
            selectforeground="#ffffff"
        )

    def lb_show_error(self, index: int):
        if index < 0 or index > self.lb_counter: return

        self.lb.itemconfig(
            index,
            background="#ffffff", foreground="#800000",
            selectbackground="#800000",
            selectforeground="#ffffff"
        )

    def progress_bar_set(self, start: float, divisions: int, divIndex: int, end: float, total: float, res: int = 100, multiplier=100):

        print(start, end, divisions, divIndex, total, res, multiplier)

        for i in range(int(start*multiplier*res), int(end*multiplier*res)):
            c = (i/(end*multiplier*res))*multiplier
            t = (100/divisions * divIndex) + (((i/res))/total)/divisions

            self.pbar_curr['value'] = c
            self.pbar_total['value'] = t

            # print(c, t)

            self.pbar_info_lbl.config(
                anchor=tk.SW,
                justify=tk.LEFT,
                text="Progress - Current: {}%; Total: {}%".format(
                    str(c)[:4],
                    str(t)[:4]
                )
            )

            self.root.update()

    def close(self):
        global apptitle
        if not self.canClose: return

        if tkmsb.askyesno(
            apptitle,
            "Are you sure you want to exit?"
        ):
            self.root.quit()

    def __del__(self):
        self.thread.join(self, 0)


def _boot():
    global ui, ui_est, logFn

    if os.path.exists(os.path.join(QAInfo.appdataLoc, QAInfo.confFilename)):

        if not IOptions.allow_confFile_existence:
            cont = False

        elif IOptions.ask_owr:
            cont = tkmsb.askyesno(
                apptitle,
                "An older installation was found;\n\nDue to the current state of the installation, it is recommended "
                "to reset files exclusively through the QA Recovery Utilties application.\n\nAre you sure you want to "
                "continue with the 'Secondary Installer'? "
            )

        else:
            cont = False

    else:
        cont = True

    if not cont:
        if ui_est and type(ui) is object: ui.canClose = True
        error(e_quit=True, err=False, e_code='QSI-B:Cont=False')
        return  # fail-safe

    if os.path.exists(logFn):
        open(logFn, 'w').close()  # Clear

    log("SETUP_LOG_CLEAR_TIME = ", QATime.now());
    log("", nl=True)

    log(
        "_BOOT_CONDITION_ONE:!CONF_EX - ",
        str(not os.path.exists(os.path.join(QAInfo.appdataLoc, QAInfo.confFilename))).upper(),
        ", _CONT: TRUE; BOOT_FLAG_ALLOW: TRUE, CREATE_UI_FRAME: TRUE, EST_UI: TRUE"
    )

    ui = UI()
    ui_est = True


def error(err=True, e_quit=False, err_info: str = "", e_code='1', exc_type=Exception):
    global ui, ui_est
    if ui_est and type(ui) is object: ui.canClose = True

    if err:
        raise exc_type(err_info)

    if e_quit:
        if ui_est and type(ui) is object:
            ui.root.quit()

        else:
            sys.exit(e_code)


def log(d, *data, nl=False):
    global logFn

    _d = str(d) + "".join(str(i) for i in data)
    _d = "%s%s %s" % ("\n", (QATime.forLog() + ":") if not nl else "", _d.strip())

    print(_d)

    with open(logFn, 'a') as logFile:
        logFile.write(_d)
        logFile.close()


def load_theme() -> dict:
    output = {}
    theme_file = IOptions.themeFile if os.path.exists(IOptions.themeFile) else os.path.join(
        QAInfo.appdataLoc,
        QAInfo.themeFilename
    )

    with open(theme_file, 'r') as theme_file:
        _rTheme = theme_file.read()
        theme_file.close()

    for i in _rTheme.split("\n"):
        if len(i.strip()) > 0:
            if i.strip()[0] != "#":
                k = i.strip().split(" ")[0].strip()
                v = i.replace(k, "", 1).strip()

                output[k] = (v if 'fsize' not in k else int(v))

    return output


def is_admin() -> bool:
    try:
        ia = (os.getuid() == 0)

    except AttributeError:
        ia = ctypes.windll.shell32.IsUserAnAdmin() != 0

    return ia


_boot()
