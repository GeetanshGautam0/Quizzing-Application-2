import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as tkfld
from tkinter import messagebox as tkmsb
import os, sys

import qa_appinfo as QAInfo
import qa_splash as QASplash

boot_steps = {
    1: 'Loading Variables',
    2: 'Loading Classes',
    3: 'Loading Functions',
    4: 'Running Boot Checks',
    5: 'Fetching Version Information (Online)\n(This process will timeout automatically if needed)'
};
boot_steps_amnt = len(boot_steps)

if not QAInfo.doNotUseSplash:
    splRoot = tk.Toplevel()
    splObj = QASplash.Splash(splRoot)

    splObj.setImg(QAInfo.icons_png.get('qt'))
    splObj.setTitle("Quizzing Form")


def set_boot_progress(ind, resolution=100):
    if QAInfo.doNotUseSplash: return

    global boot_steps;
    global boot_steps_amnt;
    global splObj

    splObj.setInfo(boot_steps[ind])

    ind -= 1  # 0 >> Max
    prev = ind - 1 if ind > 0 else ind

    for i in range(prev * resolution, ind * resolution):
        for j in range(20): pass  # < 0.01 sec delay

        splObj.changePbar(
            (i / boot_steps_amnt) / (resolution / 100)
        )


def show_splash_completion(resolution=100):
    if QAInfo.doNotUseSplash: return

    global boot_steps_amnt;
    global splObj

    ind = boot_steps_amnt - 1

    splObj.completeColor()
    splObj.setInfo(f"Completed Boot Process")

    for i in range(ind * resolution, boot_steps_amnt * resolution):
        for j in range(20): pass  # < 0.01 sec delay

        splObj.changePbar(
            (i / boot_steps_amnt) / (resolution / 100)
        )

    time.sleep(0.5)


# Adjust Splash
set_boot_progress(1)

try:
    import qa_typeConvertor as QAConvertor
    import qa_logging as QALogging
    import qa_fileIOHandler as QAFileIO
    import qa_onlineVersCheck as QA_OVC
    import qa_win10toast as QAWin10Toast
    import qa_time as QATime
    import qa_globalFlags as QAJSONHandler
    import qa_errors as QAErrors
    import qa_questions as QAQuestionStandard
    import qa_theme as QATheme
    import qa_diagnostics as QADiagnostics

    import threading, shutil, time, json, sqlite3, playsound, re, random, traceback

except:
    sys.exit(-1)

# Globals
apptitle = f"Quizzing Form v{QAInfo.versionData[QAInfo.VFKeys['v']]}"
QAS_encoding = 'utf-8'
self_icon = QAInfo.icons_ico.get('qt')
defs_configruationFilename = '{}\\{}'.format(QAInfo.appdataLoc.strip('\\').strip(), QAInfo.confFilename)

# Adjust Splash
set_boot_progress(2)


class IO:  # Object Oriented like FileIOHandler
    def __init__(self, fn: str, **kwargs):
        self.filename = fn
        self.object = QAFileIO.create_fileIO_object(self.filename)
        self.flags = {
            'append': [False, (bool,)],
            'append_sep': ["\n", (str, bytes)],
            'suppressError': [False, (bool,)],
            'encoding': ['utf-8', (str,)],
            'encrypt': [False, (bool,)]
        }
        self.kwargs = kwargs

        self.reload_kwargs()

    def rawLoad(self, *args, **kwargs) -> bytes:
        return QAFileIO.load(self.object)

    def saveData(self, Data, **kwargs):  # Secure Save
        self.flags = flags_handler(self.flags, kwargs)  # Same flags
        flags = dc_lst(self.flags, 0)
        QAFileIO.save(
            self.object,
            Data,
            append=flags['append'],
            appendSeperator=flags['append_sep'],
            encryptData=flags['encrypt'],
            encoding=flags['encoding']
        )

    def clear(self, *args, **kwargs) -> None:
        open(self.object.filename, 'w').close()

    def autoLoad(self, *args, **kwargs) -> str:
        return QAFileIO.read(self.object)

    def encrypt(self, *args, **kwargs) -> None:
        QAFileIO.encrypt(self.object)

    def decrypt(self, *args, **kwargs) -> None:
        QAFileIO.decrypt(self.object)

    def reload_kwargs(self) -> None:
        self.flags = flags_handler(self.flags, self.kwargs)


def dc_lst(Dict: dict, index) -> dict:
    out: dict = {}
    for i in Dict:
        out[i] = (Dict[i][index])

    return out


class LoginUI(threading.Thread):

    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.root = tk.Toplevel()
        self.root.withdraw()

        # Theme
        self.theme = QATheme.Get().get('theme')

        # Other variables (theme)
        self.lblFrame_font = (self.theme.get('font'), 11)
        self.dsb_fg = '#595959'

        # Geometry
        self.txy = {'x': 0, 'y': 1}  # Coordinate template
        self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())  # Screen size
        self.ds_ratio = (
            1000 / 1920,  # Width
            900 / 1080  # Height
        )
        self.ds = (int(self.ds_ratio[0] * self.ss[0]),
                   int(self.ds_ratio[1] * self.ss[1]))  # Default size
        self.ws = [
            self.ds[self.txy['x']] if self.ds[self.txy['x']] < self.ss[self.txy['x']] else int(
                self.ss[self.txy['x']] * self.ds_ratio[0]),
            self.ds[self.txy['y']] if self.ds[self.txy['y']] < self.ss[self.txy['y']] else int(
                self.ss[self.txy['y']] * self.ds_ratio[1])
        ]  # Window size (adjustable)
        self.sp = (int(self.ss[self.txy['x']] / 2 - self.ws[self.txy['x']] / 2),
                   int(self.ss[self.txy['y']] / 2 - self.ws[self.txy['y']] / 2))  # Position on screen

        self.gem = "{}x{}+{}+{}".format(self.ws[0], self.ws[1], self.sp[0], self.sp[1])

        # Padding x and y
        self.padX = 10
        self.padY = 5

        # Frames
        self.dbSelctFrame = tk.Frame(self.root)
        self.credFrame = tk.Frame(self.root)
        self.configFrame = tk.Frame(self.root)
        self.finalFrame = tk.Frame(self.root)

        # Screen Indexing System
        self.screen_index = 0
        self.scI_mapping = {
            0: ["Database Selection", self.dbSelctFrame, self.screen_1],
            1: ["Credentials", self.credFrame, self.screen_2],
            2: ["Configuration", self.configFrame, self.screen_3],
            3: ["Summary", self.finalFrame, self.screen_4]
        }

        self.sc_navButton_next_states = {
            0: True,
            1: True,
            2: True,
            3: True
        };
        self.screen_data = {
            0: {
                'defaults': {
                    'i': 'Internal Database',
                    'e': 'External Database'
                },
                'flags': {
                    'selected': False
                },
                'strs': {
                    'errors': {
                        'selectDB': '\u26a0 ERROR: Please select a database',
                        'notValid': '\u26a0 ERROR: Invalid DB file selected',
                        'unknown': '\u26a0 ERROR: Unknown error (logged)',
                        'invalidDB': '\u26a0 ERROR: Invalid Database (logged; ID=0)',
                        'invalidDB_noQs': '\u26a0 ERROR: Invalid Database - no questions found (logged; ID=1)'
                    }
                }
            },
            1: {
                'strs': {
                    'errors': {
                        'addInformation': '\u26a0 ERROR: Please enter the requested information'
                    }
                }
            },
            2: {
                'defaults': {
                    'strs': {
                        'POA_part': "Selected: Part of all Questions",
                        'POA_all': "Selected: All Questions",
                        "QDF_enb": "Enabled Point Deductions",
                        "QDF_dsb": "No Deductions",
                        "acqc_disabled": "The administrator has disabled custom quiz configuration."
                    },
                    'information_strs': {
                        'POA': "Description:\nShould all questions be included in the quiz, or only a part of the questions; click on the button below to toggle the option. If you choose to only answer a part of the questions, enter the divisor amount (1/n questions will be used, where n is the number you provide)",
                        'QDF': "Description:\nShould the application deduct points when an incorrect response is given; click on the button below to toggle to option - enter the amount of points that you wish to be deducted for every incorrect option in the field below."
                    },
                    'errors': {
                        'POA_unfilled': '\u26a0 ERROR: Please fill out the "Divisor" field (Question Selection; only numbers are accepted)',
                        'QDF_unfilled': '\u26a0 ERROR: Please fill out the "Penalty" field (Incorrect Response Penalty; only numbers are accepted)'
                    }
                }
            },
            3: {
                'start_requested': {

                }
            },
            'nav': {
                'next': {
                    'defaults': {
                        'str_next': "Next \u2b9e",
                        'str_start': "Start Quiz \u2713"
                    }
                },
                'prev': {
                    'defaults': {
                        'str_prev': '\u2b9c Back'
                    }
                }
            }
        }

        # Frame Elements
        # Root Elements *excluding frames
        self.previous_button = tk.Button(self.root)
        self.next_button = tk.Button(self.root)

        self.creditLbl = tk.Label(self.root)

        #   - Frame 1: Database selection
        self.dbSel_ttl = tk.Label(self.dbSelctFrame)
        self.dbSel_info = tk.Label(self.dbSelctFrame)
        self.dbSel_btnContainer = tk.LabelFrame(self.dbSelctFrame)
        self.dbSel_btns_external = tk.Button(self.dbSel_btnContainer)
        self.dbSel_btns_internal = tk.Button(self.dbSel_btnContainer)
        self.dbSel_error_lbl = tk.Label(self.dbSelctFrame)

        #   - Frame 2: Credentials
        self.cred_ttl = tk.Label(self.credFrame)
        self.cred_info = tk.Label(self.credFrame)
        self.cred_container = tk.LabelFrame(self.credFrame)
        self.cred_name_cont = tk.LabelFrame(self.cred_container)
        self.cred_first_invis_cont = tk.LabelFrame(self.cred_name_cont)
        self.cred_first = tk.Entry(self.cred_first_invis_cont)
        self.cred_first_lbl = tk.Label(self.cred_first_invis_cont)
        self.cred_last_invis_cont = tk.LabelFrame(self.cred_name_cont)
        self.cred_last = tk.Entry(self.cred_last_invis_cont)
        self.cred_last_lbl = tk.Label(self.cred_last_invis_cont)
        self.cred_studentID_invis_cont = tk.LabelFrame(self.cred_container)
        self.cred_studentID_lbl = tk.Label(self.cred_studentID_invis_cont)
        self.cred_studentID_field = tk.Entry(self.cred_studentID_invis_cont)
        self.cred_error_lbl = tk.Label(self.credFrame)

        #    - Frame 3: Configuration
        self.config_ttl = tk.Label(self.configFrame)
        self.config_info = tk.Label(self.configFrame)
        self.config_disallowed_LBL = tk.Label(self.configFrame)
        self.config_container1 = tk.LabelFrame(self.configFrame)
        self.config_container2 = tk.LabelFrame(self.configFrame)
        self.config_poa_button = tk.Button(self.config_container1)
        self.config_poa_descLbl = tk.Label(self.config_container1)
        self.config_poa_df_field = tk.Entry(self.config_container1)
        self.config_qdf_button = tk.Button(self.config_container2)
        self.config_qdf_descLbl = tk.Label(self.config_container2)
        self.config_qdf_field = tk.Entry(self.config_container2)
        self.config_error_label = tk.Label(self.configFrame)
        self.config_poaField_descLbl = tk.Label(self.config_container1)
        self.config_qdfField_descLbl = tk.Label(self.config_container2)

        #   - Frame 4: Summary
        self.summary_ttl_lbl = tk.Label(self.finalFrame)
        self.summary_info_lbl = tk.Label(self.finalFrame)
        self.summary_DB_information_container = tk.LabelFrame(self.finalFrame)
        self.summary_DB_lbl = tk.Label(self.summary_DB_information_container)
        self.summary_student_information_container = tk.LabelFrame(self.finalFrame)
        self.summary_student_name_lbl = tk.Label(self.summary_student_information_container)
        self.summary_student_id_lbl = tk.Label(self.summary_student_information_container)
        self.summary_config_container = tk.LabelFrame(self.finalFrame)
        self.summary_config_acqc_lbl = tk.Label(self.summary_config_container)
        self.summary_config_poa_lbl = tk.Label(self.summary_config_container)
        self.summary_config_qdf_lbl = tk.Label(self.summary_config_container)
        self.summary_error_lbl = tk.Label(self.finalFrame)
        self.summary_request_start = tk.Label(self.finalFrame)

        self.summary_vsb_style = ttk.Style()
        self.summary_vsb_style.theme_use('alt')
        self.summary_vsb_style.configure(
            "TScrollbar",
            background=self.theme.get('bg'),
            arrowcolor=self.theme.get('fg'),
            bordercolor=self.theme.get('bg'),
            troughcolor=self.theme.get('bg')
        )

        # UI Update System
        self.update_element = {
            'lbl': [],
            'btn': [],
            'acc_fg': [],
            'acc_bg': [],
            'font': [],
            'frame': [],
            'error_lbls': [],
            'enteries': []
        }

        self.configuration = {}
        self.questions = {}
        self.canClose = True
        self.masterUpdateRoutine_enable = True

        # Final calls
        self.start()
        self.root.mainloop()

    def close(self):
        if not self.canClose:
            tkmsb.showerror(apptitle, "The quiz is now in progress; you cannot exit\n\nPress ok to return to quiz.")
            return

        conf = tkmsb.askyesno(apptitle, "Are you sure you want to exit?")
        if conf: sys.exit(0)

    def run(self):
        global apptitle, self_icon

        self.root.title(apptitle)
        self.root.geometry(self.gem)
        self.root.iconbitmap(self_icon)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        self.update_element['lbl'].extend([
            self.dbSel_ttl,
            self.dbSel_btnContainer,
            self.dbSel_info,
            self.dbSel_error_lbl,

            self.cred_ttl,
            self.cred_info,
            self.cred_container,
            self.cred_name_cont,
            self.cred_first_lbl,
            self.cred_last_lbl,
            self.cred_studentID_lbl,
            self.cred_error_lbl,

            self.config_ttl,
            self.config_info,
            self.config_disallowed_LBL,
            self.config_container1,
            self.config_container2,
            self.config_qdf_descLbl,
            self.config_poa_descLbl,
            self.config_qdfField_descLbl,
            self.config_poaField_descLbl,

            self.summary_ttl_lbl,
            self.summary_info_lbl,
            self.summary_DB_information_container,
            self.summary_DB_lbl,
            self.summary_student_information_container,
            self.summary_student_name_lbl,
            self.summary_student_id_lbl,
            self.summary_config_container,
            self.summary_config_poa_lbl,
            self.summary_config_qdf_lbl,
            self.summary_error_lbl,
            self.summary_request_start,
            self.summary_config_acqc_lbl
        ])

        self.update_element['btn'].extend([
            self.dbSel_btns_external,
            self.dbSel_btns_internal,

            self.config_poa_button,
            self.config_qdf_button
        ])

        self.update_element['acc_fg'].extend([
            self.dbSel_btnContainer,
            self.dbSel_ttl,

            self.cred_ttl,
            self.cred_container,
            self.cred_name_cont,

            self.config_ttl,
            self.config_disallowed_LBL,
            self.config_container1,
            self.config_container2,
            self.config_qdf_button,
            self.config_poa_button,
            self.config_error_label,

            self.summary_ttl_lbl,
            self.summary_DB_information_container,
            self.summary_student_information_container,
            self.summary_config_container,
            self.summary_request_start,
            self.summary_config_acqc_lbl
        ])

        self.update_element['acc_bg'].extend([
            self.root
        ])

        self.update_element['font'].extend([
            [self.next_button, (self.theme.get('font'), 12)],
            [self.previous_button, (self.theme.get('font'), 12)],
            [self.creditLbl, (self.theme.get('font'), 8)],

            [self.dbSel_ttl, (self.theme.get('font'), 32)],
            [self.dbSel_info, (self.theme.get('font'), 12)],
            [self.dbSel_btnContainer, (self.theme.get('font'), 10)],
            [self.dbSel_btns_external, (self.theme.get('font'), 14)],
            [self.dbSel_btns_internal, (self.theme.get('font'), 14)],
            [self.dbSel_error_lbl, (self.theme.get('font'), 11)],

            [self.cred_ttl, (self.theme.get('font'), 32)],
            [self.cred_info, (self.theme.get('font'), 12)],
            [self.cred_container, (self.theme.get('font'), 10)],
            [self.cred_name_cont, (self.theme.get('font'), 10)],
            [self.cred_first, (self.theme.get('font'), 13)],
            [self.cred_last, (self.theme.get('font'), 13)],
            [self.cred_first_lbl, (self.theme.get('font'), 13)],
            [self.cred_last_lbl, (self.theme.get('font'), 13)],
            [self.cred_studentID_field, (self.theme.get('font'), 13)],
            [self.cred_studentID_lbl, (self.theme.get('font'), 13)],
            [self.cred_error_lbl, (self.theme.get('font'), 11)],

            [self.config_ttl, (self.theme.get('font'), 32)],
            [self.config_info, (self.theme.get('font'), 12)],
            [self.config_disallowed_LBL, (self.theme.get('font'), 14)],
            [self.config_container1, (self.theme.get('font'), 10)],
            [self.config_container2, (self.theme.get('font'), 10)],
            [self.config_poa_button, (self.theme.get('font'), 14)],
            [self.config_poa_descLbl, (self.theme.get('font'), 13)],
            [self.config_poa_df_field, (self.theme.get('font'), 13)],
            [self.config_qdf_button, (self.theme.get('font'), 14)],
            [self.config_qdf_descLbl, (self.theme.get('font'), 13)],
            [self.config_qdf_field, (self.theme.get('font'), 13)],
            [self.config_error_label, (self.theme.get('font'), 11)],
            [self.config_qdfField_descLbl, (self.theme.get('font'), 13)],
            [self.config_poaField_descLbl, (self.theme.get('font'), 13)],

            [self.summary_ttl_lbl, (self.theme.get('font'), 32)],
            [self.summary_info_lbl, (self.theme.get('font'), 12)],
            [self.summary_DB_information_container, (self.theme.get('font'), 10)],
            [self.summary_DB_lbl, (self.theme.get('font'), 13)],
            [self.summary_student_information_container, (self.theme.get('font'), 10)],
            [self.summary_student_name_lbl, (self.theme.get('font'), 13)],
            [self.summary_student_id_lbl, (self.theme.get('font'), 13)],
            [self.summary_config_container, (self.theme.get('font'), 10)],
            [self.summary_config_poa_lbl, (self.theme.get('font'), 13)],
            [self.summary_config_qdf_lbl, (self.theme.get('font'), 13)],
            [self.summary_config_acqc_lbl, (self.theme.get('font'), 13)],
            [self.summary_error_lbl, (self.theme.get('font'), 11)],
            [self.summary_request_start, (self.theme.get('font'), 14)]
        ])

        self.update_element['frame'].extend([
            self.configFrame,
            self.dbSelctFrame,
            self.credFrame,
            self.finalFrame
        ])

        self.update_element['error_lbls'].extend([
            self.dbSel_error_lbl,
            self.cred_error_lbl,
            self.config_error_label,
            self.summary_error_lbl
        ])

        self.update_element['enteries'].extend([
            self.cred_first,
            self.cred_last,
            self.cred_studentID_field,

            self.config_qdf_field,
            self.config_poa_df_field
        ])

        self.next_button.config(
            text=self.screen_data['nav']['next']['defaults']['str_next'],
            command=self.next_page,
            anchor=tk.E
        )

        self.previous_button.config(
            text=self.screen_data['nav']['prev']['defaults']['str_prev'],
            command=self.prev_page,
            anchor=tk.W
        )

        self.creditLbl.config(
            text="Coding Made Fun, {}".format(QATime.form('%Y')),
            anchor=tk.E,
            justify=tk.RIGHT
        )

        self.update_ui(0, True)
        self.root.deiconify()

    def update_ui(self, screenI_counter=0, force_refresh=False, mqprpf=False):
        if mqprpf:
            self.start_quiz_mf()

        # Check if update_ui is enabled
        if not self.masterUpdateRoutine_enable:
            debug(
                "QF::553 - LoginUI.update_ui was called, but the masterUpdateRoutine_enable flag is set to DISABLED (bool:False)")
            return

        # Config.
        self.screen_index += screenI_counter
        if self.screen_index < 0:
            self.screen_index = 0
        elif self.screen_index >= len(self.scI_mapping):
            self.screen_index = len(self.scI_mapping) - 1

        self.title()

        debug("Screen re-draw params: i. scic = ", screenI_counter, "; ii. f_r = ", force_refresh)

        if screenI_counter != 0 or force_refresh:
            self.clear_screen()

            self.scI_mapping.get(self.screen_index)[-1]()  # Call the screen setup function

            # if self.screen_index > 0: self.previous_button.pack(fill=tk.X, expand=True, side=tk.LEFT)
            # if self.screen_index < len(self.scI_mapping) - 1: self.next_button.pack(fill=tk.X, expand=True, side=tk.RIGHT)

            self.creditLbl.pack(fill=tk.X, expand=False, side=tk.BOTTOM)

            self.previous_button.pack(fill=tk.X, expand=True, side=tk.LEFT)
            self.next_button.pack(fill=tk.X, expand=True, side=tk.RIGHT)
            self.config_nav_buttons()

        # Theme
        self.root.config(bg=self.theme.get('bg'))

        for i in self.scI_mapping:
            self.scI_mapping[i][1].config(bg=self.theme.get('bg'))

        for i in self.update_element['lbl']:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg')
                )
            except Exception as e:
                debug(f"An exception occurred whilst theming lbl {i}: {e}")

        for i in self.update_element['btn']:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg'),
                    activebackground=self.theme.get('ac'),
                    activeforeground=self.theme.get('hg'),
                    bd='0'
                )
            except Exception as e:
                debug(f"An exception occurred whilst theming btn {i}: {e}")

        for i in self.update_element['acc_fg']:
            try:
                i.config(
                    fg=self.theme.get('ac')
                )
            except Exception as e:
                debug(f"An exception occurred whilst applying the accent color as fg to {i}: {e}")

        for i in self.update_element['acc_bg']:
            try:
                i.config(
                    bg=self.theme.get('ac')
                )
            except Exception as e:
                debug(f"An exception occurred whilst applying the accent color as bg to {i}: {e}")

        for i in self.update_element['font']:
            try:
                i[0].config(
                    font=i[1]
                )
            except Exception as e:
                debug(f"An exception occurred whilst applying font {i[1]} to {i[0]}: {e}")

        for i in self.update_element['frame']:
            try:
                i.config(
                    bg=self.theme.get('bg')
                )
            except Exception as e:
                debug(f"An exception occurred whilst theming frame {i}: {e}")

        for i in self.update_element['error_lbls']:
            i.config(
                fg=self.theme.get('ac'),
                bg=self.theme.get('bg'),
                text=""
            )

        for i in self.update_element['enteries']:
            i.config(
                fg=self.theme['fg'],
                bg=self.theme['bg'],
                selectforeground=self.theme['hg'],
                selectbackground=self.theme['ac'],
                insertbackground=self.theme['ac']
            )

        # Exceptions

        for i in [self.next_button, self.previous_button]:
            i.config(
                bg=self.theme.get('ac'),
                fg=self.theme.get('hg'),
                activebackground=self.theme.get('hg'),
                activeforeground=self.theme.get('ac'),
                bd='0'
            )

        self.creditLbl.config(
            bg=self.theme.get('ac'),
            fg=self.theme.get('hg')
        )

        for i in [self.dbSel_btns_external, self.dbSel_btns_internal]:
            i.config(
                disabledforeground=self.theme.get('hg')
            )

        for i in [self.cred_last_invis_cont, self.cred_first_invis_cont, self.cred_studentID_invis_cont]:
            i.config(bd='0', bg=self.theme.get('bg'))

        if screenI_counter != 0 or force_refresh:
            self.update_ui_elements()

        # --- end ---

    def update_ui_elements(self):
        if self.screen_data[0]['flags']['selected']:

            debug("screen_data[0].get('database_selection'): ", self.screen_data[0].get('database_selection'))

            if self.screen_data[0].get('database_selection') == 'i':
                self.dbSel_btns_external.config(state=tk.NORMAL, bg=self.theme.get('bg'))
                self.dbSel_btns_internal.config(
                    state=tk.DISABLED, bg=self.theme.get('ac'),
                    text=self.screen_data[0]['defaults']['i'] + ' \u2713'
                )

            elif self.screen_data[0].get('database_selection') == 'e':
                self.dbSel_btns_internal.config(state=tk.NORMAL, bg=self.theme.get('bg'))
                self.dbSel_btns_external.config(
                    state=tk.DISABLED, bg=self.theme.get('ac'),
                    text=self.screen_data[0]['defaults']['e'] + ' \u2713\n' +
                         self.screen_data[0]['external_database']['filename'].split('\\')[-1]
                )

    def all_screen_widgets(self) -> list:
        _db = self.dbSelctFrame.winfo_children()
        _cred = self.credFrame.winfo_children()
        _conf = self.configFrame.winfo_children()
        _fin = self.finalFrame.winfo_children()
        __all = self.root.winfo_children()

        for item in _db:
            if item.winfo_children(): _db.extend(item.winfo_children())

        for item in _cred:
            if item.winfo_children(): _cred.extend(item.winfo_children())

        for item in _conf:
            if item.winfo_children(): _conf.extend(item.winfo_children())

        for item in _fin:
            if item.winfo_children(): _fin.extend(item.winfo_children())

        for item in __all:
            if item.winfo_children(): __all.extend(item.winfo_children())

        return [__all, _db, _cred, _conf, _fin]

    def clear_screen(self):
        widgets = self.all_screen_widgets()[0]

        for i in widgets:
            try:
                i.pack_forget()
            except Exception as e:
                debug(f'Exception whilst clearing screen: {e}')

    def title(self):
        global apptitle
        self.root.title(f"{apptitle} - {self.scI_mapping.get(self.screen_index)[0]}")

    def screen_1(self):  # DB Selection
        debug(f"Setting up DB Select Page (ind = {self.screen_index})")

        self.dbSelctFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.dbSel_ttl.config(text="Quizzing Form", anchor=tk.W)
        self.dbSel_ttl.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4))

        self.dbSel_info.config(
            text="Step 1/{}: Question Database Selection;\nSelect a database from an external file, or the internal database by selecting the appropriate buttons below.".format(
                len(self.scI_mapping)
            ),
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=int(self.ws[0] - self.padX * 2)
        )
        self.dbSel_info.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY / 4, self.padY))

        self.dbSel_btnContainer.config(text="Options")
        self.dbSel_btnContainer.pack(
            fill=tk.BOTH,
            expand=True,
            padx=self.padX,
            pady=self.padY * 3
        )

        self.dbSel_btns_internal.config(text=self.screen_data[0]['defaults']['i'], command=self.btns_dbSel_int)
        self.dbSel_btns_internal.pack(fill=tk.BOTH, expand=True, padx=(self.padX / 2, self.padX), pady=self.padY,
                                      side=tk.LEFT)

        self.dbSel_btns_external.config(text=self.screen_data[0]['defaults']['e'], command=self.btns_dbSel_ext)
        self.dbSel_btns_external.pack(fill=tk.BOTH, expand=True, padx=(self.padX, self.padX / 2), pady=self.padY,
                                      side=tk.LEFT)

        self.dbSel_error_lbl.config(
            wraplength=(self.ws[0] - self.padX * 2)
        )
        self.dbSel_error_lbl.pack(
            fill=tk.X,
            expand=False,
            side=tk.BOTTOM
        )

    def screen_2(self):  # Credentials
        debug(f"Setting up Credentials Page (ind = {self.screen_index})")

        self.credFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.cred_ttl.config(text="Quizzing Form", anchor=tk.W, justify=tk.LEFT)
        self.cred_ttl.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4))

        self.cred_info.config(
            text="Step 2/{}: Credentials;\nEnter the information requested in the form below.".format(
                len(self.scI_mapping)
            ),
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=int(self.ws[0] - self.padX * 2)
        )
        self.cred_info.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY / 4, self.padY))

        self.cred_container.config(text="Information Required")
        self.cred_container.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

        self.cred_name_cont.config(text="Full Name")
        self.cred_name_cont.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY, self.padY / 2))

        self.cred_first_invis_cont.pack(fill=tk.BOTH, expand=False, pady=(self.padY, self.padY / 2))
        self.cred_last_invis_cont.pack(fill=tk.BOTH, expand=False, pady=(self.padY / 2, self.padY))

        self.cred_first_lbl.config(text="First Name")
        self.cred_first_lbl.pack(fill=tk.X, expand=False, side=tk.LEFT, padx=(self.padX, 0))

        self.cred_first.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, self.padX))

        self.cred_last_lbl.config(text="Last Name")
        self.cred_last_lbl.pack(fill=tk.X, expand=False, side=tk.LEFT, padx=(self.padX, 0))

        self.cred_last.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, self.padX))

        self.cred_studentID_invis_cont.pack(fill=tk.BOTH, expand=False, pady=(self.padY / 2, self.padY))

        self.cred_studentID_lbl.config(text="Student ID")
        self.cred_studentID_lbl.pack(fill=tk.X, expand=False, side=tk.LEFT, padx=(self.padX, 0))

        self.cred_studentID_field.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, self.padX))

        self.cred_error_lbl.config(
            wraplength=(self.ws[0] - self.padX * 2)
        )
        self.cred_error_lbl.pack(
            fill=tk.X,
            expand=False,
            side=tk.BOTTOM
        )

    def screen_3(self):  # Configuration
        debug(f"Setting up Configuration Page (ind = {self.screen_index})")

        self.configFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.config_ttl.config(text="Quizzing Form", anchor=tk.W, justify=tk.LEFT)
        self.config_ttl.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4))

        self.config_info.config(
            text="Step 3/{}: Configuration;\nConfigure the quiz you're about to take (if allowed by the administrator)".format(
                len(self.scI_mapping)
            ),
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=int(self.ws[0] - self.padX * 2)
        )
        self.config_info.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY / 4, self.padY))

        if not self.configuration['customQuizConfig']:
            self.config_disallowed_LBL.config(
                text=self.screen_data[2]['defaults']['strs']['acqc_disabled'],
                wraplength=int(self.ws[0] - self.padX * 2)
            )
            self.config_disallowed_LBL.pack(fill=tk.BOTH, expand=True, padx=self.padX, pady=self.padY)

        else:

            self.config_container1.config(
                text="Question Selection"
            )
            self.config_container1.pack(
                fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4)
            )

            self.config_poa_descLbl.config(
                text=self.screen_data[2]['defaults']['information_strs']['POA'],
                wraplength=int(self.ws[0] - self.padX * 2),
                justify=tk.LEFT,
                anchor=tk.W
            )
            self.config_poa_descLbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

            self.config_poa_button.config(
                text=self.screen_data[2]['defaults']['strs'][
                    'POA_part' if self.configuration.get('partOrAll') == 'part' else 'POA_all'],
                command=self.config_poa
            )

            self.config_poa_button.pack(
                fill=tk.BOTH,
                expand=False,
                padx=self.padX,
                pady=self.padY,
                ipadx=self.padX / 4,
                ipady=self.padY / 4,
                side=tk.LEFT
            )

            if self.configuration.get('partOrAll') == 'part':
                self.config_poa_df_field.delete(0, tk.END)
                self.config_poa_df_field.insert(0, str(self.configuration['poa_divF']))

                self.config_poa_df_field.pack(
                    fill=tk.X, expand=True,
                    padx=(self.padX, self.padX / 4), pady=self.padY,
                    side=tk.RIGHT
                )

                self.config_poaField_descLbl.config(
                    text="Divisor: ",
                    wraplength=int(self.ws[0] - self.padX * 2),
                    justify=tk.RIGHT,
                    anchor=tk.E
                )

                self.config_poaField_descLbl.pack(
                    fill=tk.X, expand=False,
                    padx=(self.padX, self.padX / 4), pady=self.padY,
                    side=tk.RIGHT
                )

            self.config_container2.config(
                text="Incorrect Response Penalty"
            )
            self.config_container2.pack(
                fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4)
            )

            self.config_qdf_descLbl.config(
                text=self.screen_data[2]['defaults']['information_strs']['QDF'],
                wraplength=int(self.ws[0] - self.padX * 2),
                justify=tk.LEFT,
                anchor=tk.W
            )

            self.config_qdf_descLbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

            self.config_qdf_button.config(
                text=self.screen_data[2]['defaults']['strs'][
                    'QDF_enb' if bool(self.configuration.get('a_deduc')) else 'QDF_dsb'],
                command=self.config_qdf
            )

            self.config_qdf_button.pack(
                fill=tk.BOTH,
                expand=False,
                padx=self.padX,
                pady=self.padY,
                ipadx=self.padX / 4,
                ipady=self.padY / 4,
                side=tk.LEFT
            )

            if bool(self.configuration.get('a_deduc')):
                self.config_qdf_field.delete(0, tk.END)
                self.config_qdf_field.insert(0, str(self.configuration['deduc_amnt']))

                self.config_qdf_field.pack(
                    fill=tk.X, expand=True,
                    padx=(self.padX, self.padX / 4), pady=self.padY,
                    side=tk.RIGHT
                )

                self.config_qdfField_descLbl.config(
                    text="Penalty: ",
                    wraplength=int(self.ws[0] - self.padX * 2),
                    justify=tk.RIGHT,
                    anchor=tk.E
                )

                self.config_qdfField_descLbl.pack(
                    fill=tk.X, expand=False,
                    padx=(self.padX, self.padX / 4), pady=self.padY,
                    side=tk.RIGHT
                )

        self.config_error_label.config(wraplength=int(self.ws[0] - self.padX * 2))
        self.config_error_label.pack(
            fill=tk.X, expand=False,
            padx=self.padX, pady=self.padY,
            side=tk.BOTTOM
        )

    def screen_4(self):  # Final (Summary)
        debug(f"Setting up final page (ind = {self.screen_index})")

        self.finalFrame.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        self.summary_ttl_lbl.config(text="Quizzing Form", anchor=tk.W, justify=tk.LEFT)
        self.summary_ttl_lbl.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4))

        self.summary_info_lbl.config(
            text="Step 4/{}: Summary;\nThe quiz is ready! Review the information below and finally click \"{}\" in the bottom right hand corner of the screen.".format(
                len(self.scI_mapping),
                self.screen_data['nav']['next']['defaults']['str_start']
            ),
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=int(self.ws[0] - self.padX * 2)
        )
        self.summary_info_lbl.pack(fill=tk.X, expand=False, padx=self.padX, pady=(self.padY / 4, self.padY))

        self.summary_error_lbl.config(text="", wraplength=int(self.ws[0] - self.padX * 2))
        self.summary_error_lbl.pack(
            fill=tk.X,
            expand=False,
            side=tk.BOTTOM,
            padx=self.padX,
            pady=self.padY
        )

        self.summary_request_start.config(
            text="Click \"%s\" to start the quiz" % self.screen_data['nav']['next']['defaults']['str_start'])
        self.summary_request_start.pack(
            fill=tk.X,
            expand=False,
            side=tk.BOTTOM,
            padx=self.padX,
            pady=self.padY
        )

        # DB Select Summary
        self.summary_DB_information_container.config(text="Selected Database")
        self.summary_DB_information_container.pack(fill=tk.BOTH, expand=False, padx=self.padX,
                                                   pady=(self.padY, self.padY / 2))

        self.summary_DB_lbl.config(
            text="Selected Database: %s" % ("External Database ({})".format(
                self.screen_data[0]['external_database']['filename'].split('\\')[-1]
            ) if self.screen_data[0].get('database_selection') == 'e' else "Local (Internal) Database"),
            wraplength=self.ws[0] - self.padX * 4,
            anchor=tk.W,
            justify=tk.LEFT
        )
        self.summary_DB_lbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

        self.summary_student_information_container.config(text="Student Information")
        self.summary_student_information_container.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY / 2)

        self.summary_student_name_lbl.config(
            text="Student Name: %s, %s" % (
                self.cred_last.get()[0].upper() + self.cred_last.get().lower().replace(self.cred_last.get()[0].lower(),
                                                                                       '', 1),
                self.cred_first.get()[0].upper() + self.cred_first.get().lower().replace(
                    self.cred_first.get()[0].lower(), '', 1)
            ),
            wraplength=self.ws[0] - self.padX * 2,
            anchor=tk.W,
            justify=tk.LEFT
        )
        self.summary_student_name_lbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4))

        self.summary_student_id_lbl.config(
            text="Student ID: %s" % self.cred_studentID_field.get(),
            wraplength=self.ws[0] - self.padX * 2,
            anchor=tk.W,
            justify=tk.LEFT
        )
        self.summary_student_id_lbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY / 4, self.padY))

        self.summary_config_container.config(text="Quiz Configuration")
        self.summary_config_container.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY / 2, 0))

        self.summary_config_acqc_lbl.config(
            text="Custom Quiz Configuration %s by Admin" % (
                "Enabled" if bool(self.configuration.get('customQuizConfig')) else "Disabled"
            ),
            wraplength=self.ws[0] - self.padX * 2,
            anchor=tk.W,
            justify=tk.LEFT
        )
        self.summary_config_acqc_lbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4))

        self.summary_config_poa_lbl.config(
            text="Question Segmentation:\n    - %s of the questions are to be asked%s" % (
                "A part" if self.configuration.get('partOrAll') == 'part' else "All",
                "\n    - 1/{} of all questions will be asked (min = 1)".format(
                    self.configuration['poa_divF']) if self.configuration.get('partOrAll') == 'part' else ""
            ),
            wraplength=self.ws[0] - self.padX * 2,
            anchor=tk.W,
            justify=tk.LEFT
        )
        self.summary_config_poa_lbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY / 4)

        self.summary_config_qdf_lbl.config(
            text="Incorrect Response Penalty:\n    - %s point(s) are to be deducted when an incorrect response is given." % (
                str(self.configuration['deduc_amnt']) if bool(self.configuration['a_deduc']) else '0'
            ),
            wraplength=self.ws[0] - self.padX * 2,
            anchor=tk.W,
            justify=tk.LEFT
        )
        self.summary_config_qdf_lbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY / 4, self.padY))

    def config_nav_buttons(self, index=None, setTo=None):
        if self.screen_index == 0:
            self.previous_button.config(state=tk.DISABLED)
        else:
            self.previous_button.config(state=tk.NORMAL)

        if self.screen_index == len(self.scI_mapping) - 1:
            self.next_button.config(text=self.screen_data['nav']['next']['defaults']['str_start'])
        else:
            self.next_button.config(text=self.screen_data['nav']['next']['defaults']['str_next'])

        if type(index) is int and type(setTo) is bool:
            self.sc_navButton_next_states[index] = setTo

        if self.sc_navButton_next_states[self.screen_index]:
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)

    # Button Handlers
    def config_qdf(self):
        if bool(self.configuration.get('a_deduc')):
            self.configuration['a_deduc'] = 0
        else:
            self.configuration['a_deduc'] = 1

        self.update_ui(force_refresh=True)

    def config_poa(self):
        if self.configuration['partOrAll'] == 'part':
            self.configuration['partOrAll'] = 'all'
        else:
            self.configuration['partOrAll'] = 'part'

        self.update_ui(force_refresh=True)

    def btns_dbSel_int(self):
        # Reset
        self.dbSel_btns_external.config(
            state=tk.NORMAL, bg=self.theme.get('bg'),
            text=self.screen_data[0]['defaults']['e']
        )

        self.screen_data[0]['flags']['selected'] = False

        # Check
        try:
            eCode = "<!ERROR:QAS_173462374&*^^783845783845*&^*&67df7**&63569^^87>%"
            ra = loadData_intern(eCode)

            debug(f"External DB: raw load (debID: 141) : ", ra)

            if ra == eCode:
                esfx()
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif ra[0] == eCode:
                esfx()
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif ra[1] == eCode:
                esfx()
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif len(ra[1]) <= 0:
                esfx()
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB_noQs']
                )
                return

            self.configuration = ra[0]
            self.questions = ra[1]

        except Exception as E:
            debug("Error whilst loading extern_db: ", E)
            esfx()
            self.dbSel_error_lbl.config(
                text=self.screen_data[0]['strs']['errors']['unknown']
            )

            return

        # Set

        self.dbSel_btns_internal.config(
            state=tk.DISABLED, bg=self.theme.get('ac'),
            text=self.screen_data[0]['defaults']['i'] + ' \u2713'
        )

        self.dbSel_error_lbl.config(
            text=""
        )

        self.screen_data[0]['database_selection'] = 'i'
        self.screen_data[0]['flags']['selected'] = True
        self.config_nav_buttons(0, True)

    def btns_dbSel_ext(self):
        # Checks
        self.dbSel_btns_internal.config(
            state=tk.NORMAL, bg=self.theme.get('bg'),
            text=self.screen_data[0]['defaults']['i']
        )

        self.screen_data[0]['flags']['selected'] = False

        file = tkfld.askopenfilename(
            defaultextension=f".{QAInfo.export_quizFile}",
            filetypes=((f"QA Quiz Database (*.{QAInfo.export_quizFile})", f"*.{QAInfo.export_quizFile}"),)
        )

        ret = type(file) is not str
        if not ret:
            file = file.replace('/', '\\')
            ret = ret or not ((file.strip() != "") and os.path.exists(file))

        try:
            eCode = "<!ERROR:QAS_173462374&*^^783845783845*&^*&67df7**&63569^^87>%"
            ra = loadData_extern(file, eCode)

            debug(f"External DB: raw load (debID: 142) : ", ra)

            if ra == eCode:
                esfx()
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif ra[0] == eCode:
                esfx()
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif ra[1] == eCode:
                esfx()
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB']
                )
                return

            elif len(ra[1]) <= 0:
                esfx()
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['invalidDB_noQs']
                )
                return

            self.configuration = ra[0];
            self.questions = ra[1]

        except Exception as E:
            debug("Error whilst loading extern_db: ", E)
            esfx()
            self.dbSel_error_lbl.config(
                text=self.screen_data[0]['strs']['errors']['unknown']
            )

            return

        # All good
        debug("External database selected: ", file, "; exit = ", ret)

        if ret:
            self.screen_data[0]['flags']['selected'] = False
            esfx()
            self.dbSel_error_lbl.config(
                text=self.screen_data[0]['strs']['errors']['notValid']
            )
            return

        self.screen_data[0]['flags']['selected'] = True
        self.dbSel_error_lbl.config(
            text=""
        )

        self.dbSel_btns_external.config(
            state=tk.DISABLED, bg=self.theme.get('ac'),
            text=self.screen_data[0]['defaults']['e'] + ' \u2713\n' + file.split('\\')[-1]
        )

        self.screen_data[0]['database_selection'] = 'e'
        self.screen_data[0]['external_database'] = {};
        self.screen_data[0]['external_database']['filename'] = file
        self.config_nav_buttons(0, True)

    def next_page(self):

        # Checks
        if self.screen_index == 0:  # DB Select
            if not self.screen_data[0]['flags']['selected']:
                esfx()
                self.dbSel_error_lbl.config(
                    text=self.screen_data[0]['strs']['errors']['selectDB']
                )

                return

            if self.screen_data[0]['database_selection'] == 'e':
                try:
                    eCode = "<!ERROR:QAS_173462374&*^^783845783845*&^*&67df7**&63569^^87>%"
                    ra = loadData_extern(self.screen_data[0]['external_database']['filename'], eCode)

                    if ra[0] == eCode:
                        esfx()
                        self.dbSel_error_lbl.config(
                            text=self.screen_data[0]['strs']['errors']['invalidDB']
                        )
                        return

                    elif ra[1] == eCode:
                        esfx()
                        self.dbSel_error_lbl.config(
                            text=self.screen_data[0]['strs']['errors']['invalidDB']
                        )
                        return

                    elif len(ra[1]) <= 0:
                        esfx()
                        self.dbSel_error_lbl.config(
                            text=self.screen_data[0]['strs']['errors']['invalidDB_noQs']
                        )
                        return

                except Exception as E:
                    debug("Error whilst loading extern_db: ", E)
                    esfx()
                    self.dbSel_error_lbl.config(
                        text=self.screen_data[0]['strs']['errors']['unknown']
                    )

                    return

        elif self.screen_index == 1:  # Credentials
            if len(self.cred_first.get()) <= 0 or len(self.cred_last.get()) <= 0 or len(
                    self.cred_studentID_field.get()) <= 0:
                esfx()
                self.cred_error_lbl.config(
                    text=self.screen_data[1]['strs']['errors']['addInformation']
                )
                return

        elif self.screen_index == 2:  # Configuration

            if self.configuration['customQuizConfig']:
                poa_df = "".join(
                    i for i in re.findall("\d", self.config_poa_df_field.get().split('.')[0]))  # \d = digits
                qdf_df = "".join(i for i in re.findall("\d", self.config_qdf_field.get().split('.')[0]))

                if len(poa_df) <= 0 and self.configuration['partOrAll'] == 'part' or poa_df == "0":
                    esfx()
                    self.config_error_label.config(
                        text=self.screen_data[2]['defaults']['errors']['POA_unfilled']
                    )

                    return

                elif len(qdf_df) <= 0 and bool(self.configuration['a_deduc']) or qdf_df == "0":
                    esfx()
                    self.config_error_label.config(
                        text=self.screen_data[2]['defaults']['errors']['QDF_unfilled']
                    )
                    return

                self.configuration['poa_divF'] = int(poa_df if self.configuration['partOrAll'] == 'part' else '0')
                self.configuration['deduc_amnt'] = int(qdf_df if bool(self.configuration['a_deduc']) else '0')

        elif self.screen_index == 3:  # Final
            self.previous_button.config(
                state=tk.DISABLED
            )
            self.next_button.config(
                state=tk.DISABLED
            )

            self.start_quiz()

            return

        self.update_ui(1)

    def prev_page(self):
        self.update_ui(-1)

    def start_quiz(self):
        self.clear_screen()  # Clear the screen
        self.canClose = False
        self.masterUpdateRoutine_enable = False
        self.root.config(bg=self.theme.get('bg'))
        self.root.title("%s - Preparing Quiz" % apptitle)

        self.update_ui(0, False, True)

    def start_quiz_mf(self):
        global apptitle

        threaded_start_quiz_mf(self)

    def __del__(self):
        self.thread.join(self, 0)


class threaded_start_quiz_mf(threading.Thread):
    def __init__(self, Obj):
        self.master = Obj
        self.thread = threading.Thread
        self.thread.__init__(self)
        self.start()

    def run(self):
        ttlLbl = tk.Label(
            self.master.root,
            text="Quizzing Form",
            anchor=tk.W,
            justify=tk.LEFT
        )
        ttlLbl.pack(fill=tk.BOTH, expand=False, padx=self.master.padX, pady=(self.master.padY, self.master.padY / 2))

        self.qpsu_ui(ttlLbl, "lbl")
        self.qpsu_ui(ttlLbl, "font", 32)
        self.qpsu_ui(ttlLbl, "ac_fg")

        infoLbl_base = "Preparing Quiz"
        infoLbl = tk.Label(
            self.master.root,
            text=infoLbl_base,
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=int(self.master.ws[0] - self.master.padX * 2)
        )
        infoLbl.pack(fill=tk.BOTH, expand=False, padx=self.master.padX, pady=(self.master.padY / 2, self.master.padY))

        self.qpsu_ui(infoLbl, "lbl")
        self.qpsu_ui(infoLbl, "font", 12)

        cred_lbl = tk.Label(
            self.master.root,
            text="Coding Made Fun, %s" % QATime.form("%Y"),
            anchor=tk.E,
            justify=tk.RIGHT,
            wraplength=self.master.ws[0] - self.master.padX * 2
        )
        cred_lbl.pack(fill=tk.BOTH, expand=False, padx=self.master.padX, side=tk.BOTTOM)

        self.qpsu_ui(cred_lbl, "lbl")
        self.qpsu_ui(cred_lbl, "font", 8)
        self.qpsu_ui(cred_lbl, "ac_fg")

        errorLabel = tk.Label(
            self.master.root,
            text="",
            wraplength=self.master.ws[0] - self.master.padX * 2
        )
        errorLabel.pack(fill=tk.BOTH, expand=False, padx=self.master.padX, pady=self.master.padY, side=tk.BOTTOM)

        self.qpsu_ui(errorLabel, "lbl")
        self.qpsu_ui(errorLabel, "font", 11)
        self.qpsu_ui(errorLabel, "ac_fg")

        progBarStyle = ttk.Style()
        progBarStyle.theme_use("alt")
        progBarStyle.configure(
            "Horizontal.TProgressbar",
            background=self.master.theme.get('ac'),
            foreground=self.master.theme.get('ac'),
            troughcolor=self.master.theme.get('bg')
        )

        progBar = ttk.Progressbar(self.master.root)
        progBar.pack(fill=tk.X, expand=False, padx=self.master.padX, pady=(self.master.padY / 4, self.master.padY),
                     side=tk.BOTTOM)

        progBar_desc_base = "Progress: "
        progBar_desc = tk.Label(
            self.master.root,
            text=progBar_desc_base,
            justify=tk.LEFT,
            anchor=tk.W,
            wraplength=self.master.ws[0] - self.master.padX * 2
        )
        progBar_desc.pack(fill=tk.BOTH, expand=False, padx=self.master.padX, side=tk.BOTTOM)

        self.qpsu_ui(progBar_desc, "lbl")
        self.qpsu_ui(progBar_desc, "font", 10)

        reSpl = "<<QAS::ForUser!::>>"
        try:
            infoLbl.config(
                text=infoLbl_base + ": Loading Configuration and Question Database"
            )

            progBar_desc.config(
                text=progBar_desc_base + "> 0%; Loading Questions Database"
            )

            # Step 1: Load Data
            eCode = "<!QAS::612367686^*&*567sdf7&^&*%^&7f776s987nf67^&N*F^sd7f6&^&^N^8*hgasdhfkhl7O*&s6df7dn86n8p7df6gn9fd7yh6no9Y&5t7nn77d"
            if self.master.screen_data[0]['database_selection'] == 'e':
                filename = self.master.screen_data[0]['external_database']['filename']
                ra = loadData_extern(filename, eCode)
                if ra == eCode:
                    raise Exception(f"{reSpl} Failed to read external database (Logged)")

                elif ra[0] == eCode or ra[1] == eCode:
                    raise Exception(f"{reSpl} Failed to read external database (Logged)")

            elif self.master.screen_data[0]['database_selection'] == 'i':
                ra = loadData_intern(eCode)
                if ra == eCode:
                    raise Exception(f"{reSpl} Failed to read local database (Logged)")

                elif ra[0] == eCode or ra[1] == eCode:
                    raise Exception(f"{reSpl} Failed to read local database (Logged)")

            self.spbar(progBar, 50)

            qas = ra[1]
            config = self.master.configuration

            debug("QAS::1521_PRP_QUIZ : Loaded qas database and configuration: ", config, qas)

            # Step 2: Randomize Questions + Select Length
            infoLbl.config(text=infoLbl_base + ": Randomizing Questions Database")
            progBar_desc.config(text=progBar_desc_base + "50%; Randomizing Questions Database")

            qas_qs = [i for i in qas.keys()]
            Len = int(
                len(qas_qs) * 1 / (
                    self.master.configuration['poa_divF'] if self.master.configuration['partOrAll'] == 'part' else 1))
            Len = 1 if Len <= 0 else (len(qas_qs) if Len > len(qas_qs) else Len)

            debug(f"Selecting %x questions from qas database" % Len)

            toUse = {}
            inds = []
            for i in range(Len):
                index = random.randint(0, len(qas_qs) - 1)
                while index in inds:
                    index = random.randint(0, len(qas_qs) - 1)

                self.spbar(progBar, int(50 + ((i / Len) * 50)))
                progBar_desc.config(
                    text=progBar_desc_base + "%s; Randomizing Questions Database" % (
                                ("{}".format(50 + ((i / Len) * 50)) + "000")[:4] + "%")
                )

                inds.append(index)
                toUse[qas_qs[index]] = qas[qas_qs[index]]  # Q:A

            debug(f"Selected Questions: ", toUse)

            self.spbar(progBar, 100)
            infoLbl.config(text=infoLbl_base + ": Finishing Up")
            progBar_desc.config(text=progBar_desc_base + "~100%; Finishing up")

            FormUI(self.master, toUse)

        except Exception as E:
            self.master.canClose = True
            debug("Failed to read DB (QAS::1487_PRP_QUIZ) :: ", str(E), "\n", traceback.format_exc())
            esfx()
            errorLabel.config(
                text="\u26a0: ERROR: %s" % (
                    "An Unknown error occurred whilst preparing the quiz (Logged)" if not reSpl in str(E) else
                    str(E).split(reSpl)[-1])
            )

    def spbar(self, __instance, val, res=100):

        for i in range(int(__instance['value'] * res), val * res):
            for timeOut in range(20): pass
            __instance['value'] = i / res

    def qpsu_ui(self, __instance, __type, arg=None, *args, **kwargs):
        """
        :param __instance: Instance
        :param __type: Type (lbl, btn, ac_fg, ac_bg, or font)
        :param arg: argument (used in 'font', )
        :param args: *args
        :param kwargs: **kwargs (see flags)
        :return: None

        Flags:
            * useAsTuple: if set to 'True,' 'font' will use the 'arg' argument as a tuple (font = arg, instead of font=(self.theme.get('font'), arg))

        """

        try:
            if __type == 'lbl':
                __instance.config(
                    bg=self.master.theme.get('bg'),
                    fg=self.master.theme.get('fg')
                )

            elif __type == 'btn':
                __instance.config(
                    bg=self.master.theme.get('bg'),
                    fg=self.master.theme.get('ac'),
                    activebackground=self.master.theme.get('ac'),
                    activeforeground=self.master.theme.get('hg')
                )

            elif __type == "ac_fg":
                __instance.config(
                    fg=self.master.theme.get('ac')
                )

            elif __type == "ac_bg":
                __instance.config(
                    fg=self.master.theme.get('hg'),
                    bg=self.master.theme.get('ac')
                )

            elif __type == "font":
                __instance.config(
                    font=((self.master.theme.get("font"), arg) if not kwargs.get('useAsTuple') == True else arg)
                )

            else:
                raise NameError(f"Invalid __type argument \"{__type}\"")

        except Exception as E:
            debug(f"Exception whilst theming quiz_prep item {__instance}: {E}")
            return E

    def __del__(self):
        self.thread.join(self, 0)


class FormUI(threading.Thread):

    def __init__(self, master, qasDict):
        self.loginUI_master = master
        self.qas = qasDict

        self.thread = threading.Thread
        self.thread.__init__(self)

        # Misc. Vars
        self.theme = self.loginUI_master.theme
        self.padX = self.loginUI_master.padX
        self.padY = self.loginUI_master.padY

        # UI Vars
        self.root = tk.Tk()
        self.root.withdraw()

        self.title_lbl = tk.Label(self.root)
        self.stu_information = tk.Label(self.root)
        self.questions_frame_container = tk.Frame(self.root)
        self.questions_canvas = tk.Canvas(self.questions_frame_container, borderwidth=0,
                                          highlightcolor=self.theme['bg'])
        self.questions_frame = tk.Frame(self.questions_canvas)
        self.questions_vsb = ttk.Scrollbar(self.questions_frame_container, orient=tk.VERTICAL)
        self.error_frame = tk.Frame(self.root)
        self.error_canvas = tk.Canvas(self.error_frame)
        self.error_main_container = tk.Frame(self.error_canvas)
        self.error_vsb = ttk.Scrollbar(self.error_frame)
        self.creditLbl = tk.Label(self.root)
        self.submit_answers_button = tk.Button(self.questions_frame)
        self.global_err_label = tk.Label(self.root)

        self.questions_vsb_style = ttk.Style()
        self.questions_vsb_style.theme_use('alt')
        self.questions_vsb_style.configure(
            "TScrollbar",
            background=self.theme.get('bg'),
            arrowcolor=self.theme.get('fg'),
            bordercolor=self.theme.get('bg'),
            troughcolor=self.theme.get('bg')
        )

        # Update Vars
        self.update_element = {
            'lbl': [],
            'btn': [],
            'acc_fg': [],
            'acc_bg': [],
            'font': [],
            'frame': [],
            'error_lbls': [],
            'enteries': []
        }

        # Misc. Vars
        self.canClose = False
        self.question_data = {}
        self.close_index = 1
        self.mc_rb_id_ref = {}
        self.mc_rb_qs_ref = {}
        self.error_questions = {}
        self.norm_answer_fields_ref = {}
        self.mc_o_tf_configured_iVars = {}

        self.NORMAL_QUESTION = 'nmrq'
        self.MC_QUESTION = 'mcq'
        self.TF_QUESTION = "tfq"
        self.CORR_QUESTION = "corrupted_question"

        # Final Things
        self.start()
        self.start_time = QATime.form("%H:%M:%S %b %d, %Y")
        self.root.mainloop()

    def _config_on_backendErr_(self):
        self.canClose = True
        self.root.wm_attributes("-topmost", False)
        self.root.overrideredirect(False)
        self.root.geometry("%sx%s+%s+%s" % (
            self.loginUI_master.ws[0],
            self.loginUI_master.ws[1],
            self.loginUI_master.sp[0],
            self.loginUI_master.sp[1])
                           )

    def _close_app(self):
        if self.loginUI_master.canClose or self.canClose:
            try:
                self.root.after(0, self.root.quit)
                self.loginUI_master.root.after(0, self.loginUI_master.root.quit)

            except:
                try:
                    sys.exit(0)
                except:
                    pass

        else:
            esfx()

    def run(self):
        global self_icon

        # Root Frame Configuration
        self.root.title(
            "Quizzing Application Quizzing Form; BTW, you're no supposed to see this so hi! - Geetansh G, own. and dev. of Coding Made Fun; did I just add this bit of code for no reason? yes, yes I did. This is what coding does to you; don't code kids.")
        self.root.geometry("{}x{}+0+0".format(self.root.winfo_screenwidth(), self.root.winfo_screenheight()))
        self.root.iconbitmap(self_icon)
        self.root.protocol("WM_DELETE_WINDOW", self._close_app)
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)

        self.fontFam = self.theme.get('font')
        self.ttlFont_size = 32
        self.cred_size = 8
        self.lblf_size = 10
        self.pF_size = 11
        self.inputF_size = 13

        self.update_element['lbl'].extend([
            self.title_lbl,
            self.creditLbl,
            self.stu_information
        ])

        self.update_element['acc_fg'].extend([
            self.title_lbl,
            self.creditLbl
        ])

        self.update_element['font'].extend([
            [self.title_lbl, (self.fontFam, self.ttlFont_size)],
            [self.creditLbl, (self.fontFam, self.cred_size)],
            [self.stu_information, (self.fontFam, self.pF_size)],
            [self.submit_answers_button, (self.fontFam, self.inputF_size)],
            [self.global_err_label, (self.fontFam, self.pF_size)]
        ])

        self.update_element['frame'].extend([
            self.questions_frame_container,
            self.questions_canvas,
            self.error_frame,
            self.questions_frame,
            self.error_canvas,
            self.error_main_container
        ])

        self.update_element['btn'].extend([
            self.submit_answers_button
        ])

        self.update_element['error_lbls'].extend([
            self.global_err_label
        ])

        self.title_lbl.config(
            text="Quizzing Form",
            anchor=tk.W,
            justify=tk.LEFT
        )
        self.title_lbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY, self.padY / 4))

        self.creditLbl.config(
            text="Coding Made Fun, %s" % QATime.form("%Y"),
            anchor=tk.E,
            justify=tk.RIGHT
        )
        self.creditLbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, side=tk.BOTTOM)

        self.global_err_label.pack(fill=tk.BOTH, expand=False, padx=self.padX, side=tk.BOTTOM)

        self.user_last = self.loginUI_master.cred_last.get()[
                             0].upper() + self.loginUI_master.cred_last.get().lower().replace(
            self.loginUI_master.cred_last.get()[0].lower(), '', 1).strip()
        self.user_first = self.loginUI_master.cred_first.get()[
                              0].upper() + self.loginUI_master.cred_first.get().lower().replace(
            self.loginUI_master.cred_first.get()[0].lower(), '', 1).strip()
        self.user_id = self.loginUI_master.cred_studentID_field.get().strip()

        self.stu_information.config(
            text="Student Information:\n    - Name: %s, %s\n    - Student ID: %s" % (
                self.user_last,
                self.user_first,
                self.user_id
            ),
            wraplength=self.root.winfo_screenwidth() - 2 * self.padX,
            anchor=tk.W,
            justify=tk.LEFT
        )

        # Final Things
        self.questions_vsb.configure(command=self.questions_canvas.yview)

        self.questions_canvas.configure(
            yscrollcommand=self.questions_vsb.set
        )

        self.questions_canvas.create_window(
            (0, 0),
            window=self.questions_frame,
            anchor="nw",
            tags="self.questions_frame"
        )

        self.questions_frame.bind("<Configure>", self.onFrameConfig)

        self.error_vsb.configure(command=self.error_canvas.yview)
        self.error_canvas.configure(
            yscrollcommand=self.error_vsb.set
        )
        self.error_canvas.create_window(
            (0, 0),
            window=self.error_main_container,
            anchor=tk.NW,
            tags="self.error_main_container"
        )

        self.error_main_container.bind("<Configure>", self.onFrameConfig)

        self.update_ui()

        self.loginUI_master.root.after(0, self.loginUI_master.root.destroy)
        self.root.deiconify()

    def update_ui(self, error=False, refresh=True):
        try:
            if error and refresh:
                self.__errorScreen()

            elif refresh:
                self.__questionsScreen()

        except Exception as E:
            esfx()
            try:
                debug("Exception whilst creating form: ", E, traceback.format_exc())
            except:
                pass
            self.loginUI_master.canClose = True
            self.canClose = True

        # Theme
        self.root.config(bg=self.theme.get('bg'))

        for i in self.update_element['lbl']:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg')
                )
            except Exception as e:
                debug(f"An exception occurred whilst theming lbl {i}: {e}")

        for i in self.update_element['btn']:
            try:
                i.config(
                    bg=self.theme.get('bg'),
                    fg=self.theme.get('fg'),
                    activebackground=self.theme.get('ac'),
                    activeforeground=self.theme.get('hg'),
                    bd='0'
                )
            except Exception as e:
                debug(f"An exception occurred whilst theming btn {i}: {e}")

        for i in self.update_element['acc_fg']:
            try:
                i.config(
                    fg=self.theme.get('ac')
                )
            except Exception as e:
                debug(f"An exception occurred whilst applying the accent color as fg to {i}: {e}")

        for i in self.update_element['acc_bg']:
            try:
                i.config(
                    bg=self.theme.get('ac')
                )
            except Exception as e:
                debug(f"An exception occurred whilst applying the accent color as bg to {i}: {e}")

        for i in self.update_element['font']:
            try:
                i[0].config(
                    font=i[1]
                )
            except Exception as e:
                debug(f"An exception occurred whilst applying font {i[1]} to {i[0]}: {e}")

        for i in self.update_element['frame']:
            try:
                i.config(
                    bg=self.theme.get('bg')
                )
            except Exception as e:
                debug(f"An exception occurred whilst theming frame {i}: {e}")

        for i in self.update_element['error_lbls']:
            i.config(
                fg=self.theme.get('ac'),
                bg=self.theme.get('bg'),
                text=""
            )

        for i in self.update_element['enteries']:
            i.config(
                fg=self.theme['fg'],
                bg=self.theme['bg'],
                selectforeground=self.theme['hg'],
                selectbackground=self.theme['ac'],
                insertbackground=self.theme['ac']
            )

        # Exceptions

        self.creditLbl.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('ac')
        )

        for i in []:  # Any btns
            i.config(
                disabledforeground=self.theme.get('hg')
            )

        for i in []:  # Invis. LBLFs
            i.config(bd='0', bg=self.theme.get('bg'))

        # --- end ---

    def __errorScreen(self, error_information=None, __backendErr=False, eCode="Unknown", tBack=None):
        esfx()
        if __backendErr:
            self._config_on_backendErr_()

        self.title_lbl.config(
            text="\u26a0 %s Error" % "Fatal" if __backendErr else "Non-Fatal"
        )

        self.root.title("Quizzing Form - %s Error" % str(eCode))

        try:
            debug("QF:__ES: E_I, __BE, EC, TBack", error_information, __backendErr, eCode, tBack)
        except:
            pass

        try:
            self.questions_frame_container.pack_forget()
            self.stu_information.pack_forget()
        except:
            pass

        try:
            self.error_frame.pack(fill=tk.BOTH, expand=True)
            self.error_canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
            self.error_vsb.pack(fill=tk.Y, expand=False, side=tk.RIGHT)

        except:
            pass

        err_lbl = tk.Label(self.error_main_container)

        err_txt = error_information if type(error_information) is str else "An unknown error occurred"
        err_txt += "; more information:\n\n    - Logged: True,\n    - User Induced Error: %s\n    - Error Code: '%s'\n    - User can exit: %s%s" % (
            str(not (__backendErr)),
            str(eCode),
            str(__backendErr),
            ("\n\n\nTechnical Information: {}".format(tBack)) if tBack is not None else ""
        )

        err_lbl.config(
            text=err_txt,
            wraplength=self.loginUI_master.ws[0] - self.padX * 3,
            anchor=tk.W,
            justify=tk.LEFT,
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg'),
            font=(self.fontFam, 11)
        )

        err_lbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

    def __questionsScreen(self):
        try:
            self.error_frame.pack_forget()
        except:
            pass

        self.global_err_label.config(text="")

        self.title_lbl.config(text="Quizzing Form")

        self.stu_information.pack(
            fill=tk.BOTH, expand=False, padx=self.padX, pady=(self.padY / 4, self.padY)
        )

        self.questions_frame_container.pack(fill=tk.BOTH, expand=True)
        self.questions_canvas.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.questions_vsb.pack(fill=tk.Y, expand=False, side=tk.RIGHT)

        toPop = []

        try:
            for i in self.qas:
                self.question_data[i] = {}

                # Step 0: Checks
                val = True
                valCode = "000"
                if QAInfo.QAS_MCCode in i and not QAInfo.QAS_MC_OPTION_CODE in i:
                    val = False;
                    valCode = "001 - No options in question"

                elif QAInfo.QAS_MC_OPTION_CODE in i and not QAInfo.QAS_MCCode in i:
                    val = False;
                    valCode = "002 - MC Option code available but not MC Question code"

                elif QAInfo.QAS_TFCode in i:
                    if not (('t' in self.qas[i].lower()) ^ ('f' in self.qas[i].lower())):
                        val = False;
                        valCode = "003 - Invalid answer expected (True/False)"

                # Step 1: Create (no longer) invis container
                temp_q_container = tk.LabelFrame(self.questions_frame,
                                                 text="Question %s" % str(list(self.qas.keys()).index(i) + 1))
                self.update_element['lbl'].append(temp_q_container)
                self.update_element['acc_fg'].append(temp_q_container)
                temp_q_container.pack(fill=tk.X, expand=False, padx=self.padX, pady=self.padY * 2)

                # Step 2: Add Contents
                # S2.1: Questions
                question_string = i.replace(QAInfo.QAS_MCCode, '').replace(QAInfo.QAS_TFCode, '')
                options = []
                if QAInfo.QAS_MC_OPTION_CODE in question_string:
                    for ii in question_string.split(QAInfo.QAS_MC_OPTION_CODE)[1::]:
                        question_string = question_string.replace(QAInfo.QAS_MC_OPTION_CODE, '')
                        found_1 = None;
                        found_2 = None

                        for iii in range(len(ii)):
                            if ii[iii] == "[" and found_1 is None and found_2 is None:
                                found_1 = iii
                            elif ii[iii] == "]" and found_2 is None and found_1 is not None:
                                found_2 = iii

                        if found_1 is not None and found_2 is not None:
                            options.append(ii[found_1:found_2].replace("[", '').replace("]", ""))

                            question_string = question_string.replace(
                                "[%s]" % ii[found_1:found_2].replace("[", '').replace("]", ""),
                                "\u2022 %s: " % ii[found_1:found_2].replace("[", '').replace("]", "")
                            )
                    question_string += "\n\nAccepted answers: %s" % ", ".join(j for j in options).strip().strip(
                        ",").strip()

                    if len(options) <= 0:
                        debug(
                            f"Question not asked because no options were found even though it was marked as a MC question; ")

                        temp_q_container.config(text=temp_q_container.cget("text") + ": Invalid Question")

                        val = False;
                        valCode = "010 - No options extracted"

                if not val:
                    self.question_data[i] = self.CORR_QUESTION

                    toPop.append([i, valCode])

                    plH = tk.Label(
                        temp_q_container,
                        text="Error: The form was unable to comprehend this question's data (Error Code: QAS_QF_Q:%s)" % valCode,
                        wraplength=int((self.root.winfo_screenwidth() - self.padX * 6))
                    )
                    plH.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

                    self.update_element['lbl'].append(plH)
                    self.update_element['acc_fg'].append(plH)
                    self.update_element['font'].append([plH, (self.fontFam, self.inputF_size)])

                    continue

                temp_q_lbl = tk.Label(temp_q_container)
                self.update_element['lbl'].append(temp_q_lbl)
                self.update_element['font'].append([temp_q_lbl, (self.fontFam, self.inputF_size)])
                temp_q_lbl.config(
                    text="Question %s:\n%s" % (
                    str(list(self.qas.keys()).index(i) + 1) + "/" + str(len(self.qas)), question_string.strip()),
                    wraplength=int((self.root.winfo_screenwidth() - self.padX * 6) / 2),
                    justify=tk.LEFT
                )
                temp_q_lbl.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY, side=tk.LEFT)

                # S2.2: Answers
                try:
                    if QAInfo.QAS_MCCode in i:
                        container = tk.LabelFrame(temp_q_container, bd='0')
                        self.question_data[i]['type'] = self.MC_QUESTION

                        for op in options:
                            temp_rb = tk.Radiobutton(container)
                            self.setup_radio_button(i, op, temp_rb)
                            temp_rb.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

                        container.pack(fill=tk.BOTH, expand=False, side=tk.RIGHT)
                        self.update_element['lbl'].append(container)

                    elif QAInfo.QAS_TFCode in i:
                        container = tk.LabelFrame(temp_q_container, bd='0')
                        self.question_data[i]['type'] = self.TF_QUESTION

                        for op in ['True', 'False']:
                            temp_rb = tk.Radiobutton(container)
                            self.setup_radio_button(i, op, temp_rb)
                            temp_rb.pack(fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY)

                        container.pack(fill=tk.BOTH, expand=False, side=tk.RIGHT)
                        self.update_element['lbl'].append(container)

                    else:
                        uid = (random.randint(0, 99999999999999999) + random.random()) * random.randint(0, 99)

                        counter = 0
                        while uid in self.norm_answer_fields_ref and counter <= 10000000:
                            counter += 1
                            uid = (random.randint(0, 99999999999999999) + random.random()) * random.randint(0, 99)

                        if counter > 10000000:
                            self.__errorScreen("Failed to assign UID to answer field", True, "UID_COUNTER>10000000")

                        self.question_data[i]['type'] = self.NORMAL_QUESTION

                        t_a_entry = tk.Text(temp_q_container)
                        t_a_entry.pack(fill=tk.X, expand=True, padx=self.padX, pady=self.padY)

                        self.norm_answer_fields_ref[uid] = t_a_entry
                        self.question_data[i]['UID'] = uid

                        self.update_element['lbl'].append(t_a_entry)
                        self.update_element['font'].append([t_a_entry, (self.fontFam, self.inputF_size)])
                        self.update_element['enteries'].append(t_a_entry)

                except Exception as e:
                    self.__errorScreen(e, True, "QAS:PRP_FORM:E__2028-CCAF", traceback.format_exc())

            self.submit_answers_button.config(
                text="Submit Answers",
                command=self.submit
            )

            self.submit_answers_button.pack(
                fill=tk.BOTH, expand=False, padx=self.padX, pady=self.padY, ipadx=self.padX / 2, ipady=self.padY / 2
            )

            for i in toPop:
                q = i[0]
                r = i[1]
                self.error_questions[q] = r

                self.question_data[q] = {'type': self.CORR_QUESTION}

        except Exception as E:
            debug(f"QAS:PRP_FORM:E__2032-CCQF", E, traceback.format_exc())
            self.__errorScreen(E, True, "QAS:PRP_FORM:E__2032-CCQF", traceback.format_exc())

    def setup_radio_button(self, question, option, tkRadiobutton):

        radio_button_refference_id = random.randint(100000000000, 999999999999) + random.random()  # ID (float)

        counter = 0
        while radio_button_refference_id in self.mc_rb_id_ref:  # A whole lotta possible numbers = a whole lotta capacity
            radio_button_refference_id = random.randint(0, 999999999999999999999999) + random.random()

            if counter > 10000000:  # 10mil tries granted
                self.__errorScreen("Cannot assign MC_UID tag to element (QAS_QF:MC_RadButton)", True,
                                   "QAS:RecDepthError-MC_UID-011")

            counter += 1

        if type(self.question_data[question].get('iVar_UID')) is not float:
            self.question_data[question]['iVar_UID'] = 0.00
            self.question_data[question]['iVar_uid_map'] = {}

            iVar = tk.IntVar()
            iVar.set(-1)  # Invalid (non-whole number); no option selected yet

            iVar_uid = (random.randint(0, 999999999999999999999999) + random.random()) * random.randint(1, 1000)

            counter_2 = 0

            while iVar_uid in self.mc_o_tf_configured_iVars and counter_2 <= 10000000:
                iVar_uid = (random.randint(0, 999999999999999999999999) + random.random()) * random.randint(1, 1000)
                counter_2 += 1

            if counter_2 > 10000000:
                raise RecursionError("could not generate iVar_uid for question")

            self.question_data[question]['iVar_UID'] = float(iVar_uid)
            self.mc_o_tf_configured_iVars[iVar_uid] = iVar

        else:
            iVar = self.mc_o_tf_configured_iVars[self.question_data[question]['iVar_UID']]
            iVar_uid = self.question_data[question]['iVar_UID']

        radio_button_refference_id = "QAS_QF_AF_MC_REF_" + str(radio_button_refference_id)

        self.mc_rb_id_ref[radio_button_refference_id] = tkRadiobutton

        if self.mc_rb_qs_ref.get(question) is None:
            print(question, '1', self.mc_rb_qs_ref.get(question))
            self.mc_rb_qs_ref[question] = [radio_button_refference_id]
        else:
            print(question, '2')
            self.mc_rb_qs_ref[question].append(radio_button_refference_id)

        try:
            self.question_data[question]['mc_id'].append(radio_button_refference_id)

        except:
            if not question in self.question_data:
                self.question_data[question] = {}

            if not 'mc_id' in self.question_data[question]:
                self.question_data[question]['mc_id'] = []

            self.question_data[question]['mc_id'].append(radio_button_refference_id)

        debug("setup_radio_button: q, option, id, mrqr, mrir", question, option, radio_button_refference_id,
              self.mc_rb_qs_ref, self.mc_rb_id_ref)

        tkRadiobutton.config(
            text=option,
            command=lambda: self.onMcClick(radio_button_refference_id, question, iVar_uid),
            indicatoron='0',
            relief=tk.RAISED,
            variable=iVar,
            value=len(self.question_data[question]['mc_id'])
        )

        self.question_data[question]['iVar_uid_map'][len(self.question_data[question]['mc_id'])] = option

        debug("SETUP_RADIO_BUTTON_FINAL_DEBUG: question, s.qd, rbrid, s.mcotfciV, s.mc_rb_id_ref, s.mc_rb_qs_ref",
              question, self.question_data, radio_button_refference_id, self.mc_o_tf_configured_iVars,
              self.mc_rb_id_ref, self.mc_rb_qs_ref)

        self.format_rButton(tkRadiobutton, False)

        return

    def onMcClick(self, id, question, iVar_uid):
        debug("onMcClick: id, q", id, question)

        try:
            iVar_val = self.mc_rb_id_ref[id].cget('value')
            self.mc_o_tf_configured_iVars[iVar_uid].set(iVar_val)
            debug("onMcClick: set iVar_uid (float, 1) to iVar_val (int, 2)", iVar_uid, iVar_val)

            # Clear all formatting
            for i in self.mc_rb_qs_ref[question]:
                self.format_rButton(self.mc_rb_id_ref[i], False)

            self.format_rButton(self.mc_rb_id_ref[id], True)

        except Exception as E:
            try:
                debug(str(E))
            except:
                pass

            self.__errorScreen(
                "Cannot format mc_question options with MC Option ID (ibi) '{}'\n\n    - Error: {}".format(id, str(
                    E.__class__) + ": " + str(E)), True, "QAS:2077:CFMC_ID_CORR", traceback.format_exc())

        return

    def format_rButton(self, _inst, _act, _err=False):
        if _err:
            _inst.config(
                bg="#990000",
                fg="#ffffff",
                selectcolor="#ffffff",
                activeforeground="#ffffff",
                activebackground="#990000"
            )

            _inst.deselect()

            return

        if _act:
            _inst.config(
                bg=self.theme.get('ac'),
                fg=self.theme.get('hg'),
                selectcolor=self.theme.get('ac'),
                activeforeground=self.theme.get('bg'),
                activebackground=self.theme.get('fg')
            )
            _inst.select()

        else:
            _inst.config(
                bg=self.theme.get('bg'),
                fg=self.theme.get('fg'),
                selectcolor=self.theme.get('bg'),
                activeforeground=self.theme.get('ac'),
                activebackground=self.theme.get('hg')
            )
            _inst.deselect()

    def submit(self):
        self.global_err_label.config(text="")

        try:

            err = False

            for i in self.qas:

                if i in self.error_questions:
                    continue  # Skip

                elif self.question_data[i]['type'] == self.NORMAL_QUESTION:
                    answer = self.norm_answer_fields_ref[self.question_data[i]['UID']].get("1.0", "end-1c").strip()

                    if not len(answer) > 0:
                        self.norm_answer_fields_ref[self.question_data[i]['UID']].config(
                            bg="#990000",
                            fg="#ffffff",
                            selectbackground="#ffffff",
                            selectforeground="#990000"
                        )

                        err = True

                    else:
                        self.norm_answer_fields_ref[self.question_data[i]['UID']].config(
                            bg=self.theme.get('bg'),
                            fg=self.theme.get('fg'),
                            selectbackground=self.theme.get('ac'),
                            selectforeground=self.theme.get('hg')
                        )

                elif self.question_data[i]['type'] == self.TF_QUESTION or self.question_data[i][
                    'type'] == self.MC_QUESTION:
                    # Non-iterative
                    rb_uid = self.question_data[i]['iVar_UID']
                    iVar = self.mc_o_tf_configured_iVars[rb_uid]
                    val = iVar.get()

                    if not val > -1:
                        # Error
                        err = True

                        for uid in self.question_data[i]['mc_id']:
                            tkRButton = self.mc_rb_id_ref[uid]
                            self.format_rButton(tkRButton, False, True)

                    else:
                        for uid in self.question_data[i]['mc_id']:
                            tkRButton = self.mc_rb_id_ref[uid]

                            if not tkRButton.cget('text') == self.question_data[i]['iVar_uid_map'][val]:
                                self.format_rButton(tkRButton, False, False)

                            else:
                                self.format_rButton(tkRButton, True, False)

                else:
                    self.__errorScreen(
                        "Failed to match question to any NMQ, MCQ, or TFQ, and was not marked as an errenous question.",
                        True, "QAS:EC-FMQ_[NMQ,MCQ,TFQ]")

            if err:
                esfx()

                self.global_err_label.config(
                    text="\u26a0 ERROR: You must answer all questions before submitting your answers."
                )

                return

            else:
                self.end_time = QATime.form("%H:%M:%S %b %d, %Y")
                self.mark()

        except Exception as E:
            self.__errorScreen(
                "An error occurred whilst processing the answers given",
                True,
                str(E.__class__) + " " + str(E),
                traceback.format_exc()
            )

    def __marking_screen(self):
        try:
            self.questions_frame_container.pack_forget()
            self.error_frame.pack_forget()
        except:
            pass

        self.title_lbl.config(
            text=self.title_lbl.cget('text') + " - Evaluating Responses"
        )

        info_lbl = tk.Label(self.root)

        info_lbl_base = "Evaluating your responses; this may take a while. You may let this process continue in the background and continue to do other tasks. Do not shutdown your computer or set it to sleep."

        info_lbl.config(
            text=info_lbl_base,
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg'),
            font=(self.fontFam, self.inputF_size),
            wraplength=self.loginUI_master.ws[0] - self.padX * 2,
            justify=tk.LEFT,
            anchor=tk.W
        )

        info_lbl.pack(fill=tk.BOTH, expand=True, padx=self.padX, pady=self.padY)

        self.root.title("Quzzing Form - Evaluating Responses")
        self.root.geometry("%sx%s+%s+%s" % (
        self.loginUI_master.ws[0], self.loginUI_master.ws[0], self.loginUI_master.sp[0], self.loginUI_master.sp[1]))
        self.root.overrideredirect(False)
        self.root.wm_attributes('-topmost', False)

        return [info_lbl, info_lbl_base]

    def mark(self):
        # at this point, everything should be good; yet it is still a good idea to try-except the entire question checking logic

        try:

            ILbl_raw = self.__marking_screen()
            ILbl = ILbl_raw[0]
            ILbl_base = ILbl_raw[1]

            ILbl.config(text=ILbl_base + "\n\nProgress: Getting Ready")

            self.root.update()

            errors = {}
            correct = {}
            incorrect = {}

            for question, answer in self.qas.items():

                ILbl.config(text=ILbl_base + "\nProgress: %s/%s\n\nQuestion:\n%s\n\nAnswer Given:\n" % (
                str(list(self.qas.keys()).index(question) + 1), str(len(self.qas)), question.strip()))

                answer_expected = answer.lower().strip()

                try:
                    question_data = self.question_data[question]
                except KeyError:
                    question_data = self.question_data[question.strip()]
                except:
                    self.__errorScreen(
                        "Could not fetch question data", True, "QAS:FORM_mark:2379-F2FQD", traceback.format_exc()
                    )

                if question_data['type'] == self.CORR_QUESTION or question in self.error_questions:
                    errors[question.strip()] = self.error_questions[question]
                    answer_r = "<<From Quizzing Form: This Question was an invalid question and will not be counted>>"

                elif question_data['type'] == self.TF_QUESTION or question_data['type'] == self.MC_QUESTION:
                    VUID = self.question_data[question]['iVar_UID']
                    V = self.mc_o_tf_configured_iVars[VUID].get()
                    answer_r = self.question_data[question]['iVar_uid_map'][V]

                elif question_data['type'] == self.NORMAL_QUESTION:
                    answer_r = self.norm_answer_fields_ref[self.question_data[question]['UID']].get("1.0",
                                                                                                    "end-1c").strip()

                else:
                    raise QAErrors.QACannotDetermineQuestionType

                ILbl.config(text=ILbl.cget('text') + answer_r.strip())
                self.root.update()

                # Best chance to get it right
                answer_r_for_check = "".join(re.findall("[^\ \t\n\b]", answer_r.lower()))
                answer_k_for_check = "".join(re.findall("[^\ \t\n\b]", answer_expected.lower()))

                if question_data['type'] == self.NORMAL_QUESTION:
                    if answer_r_for_check == answer_k_for_check:
                        correct[question.strip()] = answer_r.strip()

                    else:
                        incorrect[question.strip()] = [answer.strip(), answer_r.strip()]

                elif question_data['type'] == self.TF_QUESTION:
                    # ^ operand = XOR: If both or none: error, else, good

                    if ('t' in answer_k_for_check.lower()) ^ ('f' in answer_k_for_check.lower()):

                        if ('t' in answer_k_for_check.lower() and 't' in answer_r_for_check.lower()) and not (
                                'f' in answer_r_for_check.lower()):
                            correct[question.strip()] = answer_r.strip()

                        elif ('f' in answer_k_for_check.lower() and 'f' in answer_r_for_check.lower()) and not (
                                't' in answer_r_for_check.lower()):
                            correct[question.strip()] = answer_r.strip()

                        else:
                            incorrect[question.strip()] = [answer.strip(), answer_r.strip()]

                    else:
                        errors[
                            question.strip()] = "404: No appropriate answer provided by administrator (QType: True/False, expected answer: %s, received: %s" % (
                        answer.strip(), answer_r.strip())

                elif question_data['type'] == self.MC_QUESTION:
                    if answer_r_for_check.lower() == answer_k_for_check.lower():
                        correct[question.strip()] = answer_r.strip()

                    else:
                        incorrect[question.strip()] = [answer.strip(), answer_r.strip()]

            debug("QAS:MARKED: CORRECT (Q, A_given), INCORRECT (Q, A_expected, A_given), ERROR (Q, error)", correct,
                  incorrect, errors)

            ILbl.config(
                text=ILbl_base + "\n\nProgress: Compiling Scores File\n\nPlease select a location to save the scores file.")
            self.root.update()

            self.compile_sFile(correct, incorrect, errors)

            tkmsb.showinfo(apptitle, "Finished evaluating your responses")

            ILbl.config(
                text="Finished evaluating your responses; You may close this window now!\nTo ensure the privacy of the user, and to allow the admin to check all responses manually, the score cannot be viewed right now.\n\n\nThank you for using this application\n    - Geetansh G, Developer of QAS and Coding Made Fun")

            self.title_lbl.config(text="Quizzing Form - Done")
            self.root.title("Quizzing Form - Done")
            self.canClose = True

        except Exception as E:
            self.__errorScreen("Error whilst evaluating question answers", True, str(E.__class__) + str(E),
                               traceback.format_exc())

    def compile_sFile(self, correct: dict, incorrect: dict, errors: dict):
        # First, create a file in the appdata folder
        # JSON file with the following dicts:

        # 1) User Info
        # 2) Config
        # 3) Errors
        # 4) Incorrect
        # 5) Correct
        # 6) Time

        def create(filename, _score, instance):
            config = {
                'acqc': instance.loginUI_master.configuration['customQuizConfig'],
                'qpoa': instance.loginUI_master.configuration['partOrAll'],
                'qsdf': instance.loginUI_master.configuration['poa_divF'],
                'dma': instance.loginUI_master.configuration['a_deduc'],
                'pdpir': instance.loginUI_master.configuration['deduc_amnt']
            }

            first = instance.user_first
            last = instance.user_last
            id = instance.user_id

            __jInst = JSON()

            __jInst.setFlag(
                filename=filename,
                data_key="userID",
                data_val={
                    "first": first,
                    "last": last,
                    "id": id
                }
            )

            __jInst.setFlag(filename, "configuration", config)

            __jInst.setFlag(filename, "errors", errors)
            __jInst.setFlag(filename, "incorrect", incorrect)
            __jInst.setFlag(filename, "correct", correct)

            __jInst.setFlag(filename, "score", _score)

            __jInst.setFlag(filename, "time", {
                "start": self.start_time,
                "end": self.end_time
            })

            IO(filename, encrypt=True).encrypt()  # Encrypt the file

        fn = "%s - %s %s - %s, %s %s - %s-%s.%s" % (
            self.user_id,
            self.user_first,
            self.user_last,
            QATime.form("%Y"),
            QATime.form("%b"),
            QATime.form("%d"),
            QATime.form("%H"),
            QATime.form("%M"),
            QAInfo.export_score_dbFile
        )

        apFile = QAInfo.appdataLoc + "\\" + QAInfo.scoresFolderName + "\\" + fn

        score = len(correct) - len(incorrect) * (int(self.loginUI_master.configuration['deduc_amnt']) if bool(
            self.loginUI_master.configuration['a_deduc']) else 0)

        try:
            debug("apFile name ", apFile)
            create(apFile, score, self)

            while True:
                extern = tkfld.askdirectory()

                if type(extern) is not str:
                    esfx()
                    continue

                extern = extern.replace("/", "\\")

                if len(extern.strip()) <= 0:
                    esfx()
                    continue

                elif not os.path.exists(extern.strip()):
                    esfx()
                    continue

                exFile = extern + "\\" + fn
                break

            debug("exFile name ", exFile)
            create(exFile, score, self)

        except Exception as e:
            while os.path.exists(apFile): os.remove(apFile)
            raise e.__class__(str(e))

    def onFrameConfig(self, event=None):  # for scbar

        try:
            self.questions_canvas.configure(scrollregion=self.questions_canvas.bbox("all"))
        except:
            pass

        try:
            self.error_canvas.configure(scrollregion=self.error_canvas.bbox("all"))
        except:
            pass

    def __del__(self):
        self.thread.join(self, 0)


class esfx(
    threading.Thread):  # Threaded to let the sound effect run in the background whilst application function resumes
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        self.start()

    def run(self):
        try:
            playsound.playsound(".res/error_sound.mp3")
        except Exception as e:
            debug(f"Failed to play error sound: ", e.__class__, e, traceback.format_exc())

    def __del__(self):
        self.thread.join(self, 0)


class JSON:
    def __init__(self):
        self.jsonHandlerInst = QAJSONHandler.QAFlags()
        self.jsonHandler = self.jsonHandlerInst

        self.crashID = self.jsonHandlerInst.QT_crash_id
        self.timedEventID = self.jsonHandler.QT_timed_crash_id

        self.unrID = self.jsonHandlerInst.log_unr_id
        self.funcID = self.jsonHandlerInst.log_function_id
        self.timeID = self.jsonHandlerInst.log_time_id
        self.infoID = self.jsonHandlerInst.log_info_id

        self.noFuncID = self.jsonHandlerInst.no_func_id

    def logCrash(self, info: str, functionCall=None):
        id = self.crashID
        time = f"{QATime.now()}"

        self.setFlag(
            filename=QAInfo.global_nv_flags_fn,
            data_key=id,
            data_val={
                self.unrID: True,
                self.infoID: info,
                self.timeID: time,
                self.funcID: functionCall if functionCall is not None else self.noFuncID
            }
        )

    def removeFlag(self, filename: str, data_key: str):
        flag_io = QAJSONHandler.QAFlags()
        key = flag_io.REMOVE

        flag_io.io(
            key,
            filename=filename,
            key=data_key
        )

        return

    def setFlag(self, filename: str, data_key: str, data_val: any, **kwargs):
        Flags = {
            'append': [True, (True, bool)],
            'reload_nv_flags': [True, (True, bool)]
        }

        Flags = flags_handler(Flags, kwargs, __rePlain=True)

        flag_io = QAJSONHandler.QAFlags()
        key = flag_io.SET

        flag_io.io(key,
                   filename=filename,
                   data={
                       data_key: data_val
                   },
                   appendData=Flags['append'],
                   reloadJSON=Flags['reload_nv_flags'])

        return

    def getFlag(self, filename: str, data_key: str, **kwargs):
        Flags = {
            'return_boolean': [True, (True, bool)],
            'reload_nv_flags': [True, (True, bool)]
        }

        Flags = flags_handler(Flags, kwargs)

        temp: dict = {}
        for i in Flags: temp[i] = Flags[i][0]

        Flags = temp

        debug(f"Querying for flag {data_key} in file '{filename}'")

        flagsIO = QAJSONHandler.QAFlags()
        key = flagsIO.GET

        result = flagsIO.io(Key=key,
                            key=data_key,
                            filename=filename,
                            re_bool=Flags['return_boolean'],
                            reloadJSON=Flags['reload_nv_flags'])

        debug(f"Result of query: '{result}'")

        return result

    def log_crash_fix(self, urd: bool, tp: bool, apd: str, apftf: str, crinfo: str, crtime: str, crfunc: str):
        time = f"{QATime.now()}"
        id = self.timedEventID.strip() + " " + time

        self.setFlag(
            filename=QAInfo.global_nv_flags_fn,
            data_key=id,
            data_val={
                "time": time,
                "crash_detected": {
                    self.infoID: crinfo,
                    self.timeID: crtime,
                    self.funcID: crfunc
                },
                "ran_diagnostics": urd,
                "test_passed": tp,
                "diagnostics_function": apd,
                "correction_function": apftf
            }
        )

    def boot_check(self):
        global splObj
        # Step 1: Does the key exist?
        if self.getFlag(QAInfo.global_nv_flags_fn, self.crashID):

            # Step 2: Is the error un-resolved?
            check = self.getFlag(QAInfo.global_nv_flags_fn, self.crashID, return_boolean=False)

            if check.get(self.unrID):  # Un-resolved

                # Step 1: Vars
                _dData = QADiagnostics.Data()
                _test = _dData.diagnostics_function_mapping.get(
                    check.get(self.funcID)
                )
                _corr = _dData.correction_function_mapping.get(
                    check.get(self.funcID)
                )

                # Run the test
                _result = _test()

                if not _result:
                    # Run the diagnostics
                    _corr()

                # log_crash_fix(self, urd: bool, tp: bool, apd: str, apftf: str, crinfo: str, crtime: str, crfunc: str):
                self.log_crash_fix(
                    True,
                    _result,
                    f"{_test}",
                    f"{_corr}",
                    check.get(self.infoID),
                    check.get(self.timeID),
                    check.get(self.funcID)
                )

                self.removeFlag(
                    QAInfo.global_nv_flags_fn,
                    self.crashID
                )

                QASplash.hide(splObj)
                tkmsb.showinfo(apptitle,
                               f"The application had detected a boot-error flag and thus ran the appropriate diagnostics.")
                QASplash.show(splObj)

        # True = Test passed
        return True


# Adjust Splash
set_boot_progress(3)


# Functions go here

def debug(debugData: str, *args):
    debugData = debugData + " ".join(str(i) for i in args)

    # Script Name
    try:
        scname = __file__.replace(
            '/', '\\').split('\\')[-1].split('.')[0].strip()
    except:
        scname = sys.argv[0].replace(
            '/', '\\').split('\\')[-1].split('.')[0].strip()

    # Instance
    Log = QALogging.Log()

    # Generation
    if not QALogging.Variables().genDebugFile():
        Log.logFile_create(from_=scname)

    # Log
    Log.log(data=debugData, from_=scname)


def replace_string_index(string: str, index: list, new: str) -> str:
    if len(index) != 2:
        return string
    elif index[0] > index[1]:
        return string
    elif index[0] < 0 or index[1] > len(string):
        return string

    new = string[0:index[0]] + new + (string[index[1]::] if index[1] <= len(string) else "")

    return new


def loadConfiguration(configruationFilename: str) -> dict:
    if not os.path.exists(configruationFilename):
        code = JSON().getFlag('codes.json', QAInfo.codes_keys.get('configuration_file_error').get('conf_file_missing'))

        codeInfo = JSON().getFlag('codes.json', "info", return_boolean=False)
        codeInfo = codeInfo[code]

        __logError(
            code,
            runDiagnostics=True,
            diagnosticsInfo=code,
            diagnosticsFunctionName=QAJSONHandler.QAFlags().CONF_corruption_fnc,
            UI_Message=f"An error occured whilst loading the configuration;\n\nError Code: {code}\n\nError Info: {codeInfo}",
            exit=True,
            exitCode=f"QAErrors.ConfigurationError"
        )

        raise QAErrors.ConfigurationError(code)

    try:
        __IO = IO(configruationFilename)
        raw = __IO.autoLoad()
        _dict = json.loads(raw)

    except:
        code_key = QAInfo.codes_keys['configuration_file_error']['conf_file_corrupted']
        code = JSON().getFlag('codes.json', code_key, return_boolean=False)

        codeInfo = JSON().getFlag('codes.json', "info", return_boolean=False)
        codeInfo = codeInfo[code]

        __logError(
            code,
            runDiagnostics=True,
            diagnosticsInfo=code,
            diagnosticsFunctionName=QAJSONHandler.QAFlags().CONF_corruption_fnc,
            UI_Message=f"An error occured whilst loading the configuration;\n\nError Code: {code}\n\nError Info: {codeInfo}",
            exit=True,
            exitCode=f"QAErrors.ConfigurationError"
        )

        raise QAErrors.ConfigurationError(code)

    return _dict


def get_error_code(key) -> tuple:
    key = key.strip()

    out = []

    __raw = JSON().getFlag("codes.json", key, return_boolean=False)
    __info = JSON().getFlag("codes.json", "info", return_boolean=False)

    if key in __info:
        __info.get(key)
    else:
        __info = "No Information Found"

    return (__raw, __info)


def loadQuestions(path) -> dict:
    __raw = IO(path).autoLoad()

    __out = QAQuestionStandard.convRawToDict(__raw)
    return __out


def flags_handler(reference: dict, kwargs: dict, __raiseERR=True, __rePlain=False) -> dict:
    debug(f"Refference ::: {reference}")

    out: dict = reference

    for i in kwargs:
        if i in out:  # Valid name
            kdt = type(kwargs[i])
            valt = reference[i][-1]  # Type tuple

            if kdt in valt:
                if not kwargs[i] == reference[i][0]:
                    out[i] = [kwargs[i], reference[i][-1]]
                    debug(f"Changed flag '{i}' to '{out[i]}'")

            elif __raiseERR:
                debug(
                    f"Invalid type {kdt} for flag '{i}' expected: {valt}; raising error")
                raise TypeError(
                    f"Invalid type {kdt} for flag '{i}' expected: {valt}")

            else:
                debug(
                    f"Invalid type {kdt} for flag '{i}' expected: {valt}; __raiseERR != True; suppressing error")

        elif __raiseERR:
            debug(f"Invalid type flag name '{i}'; raising error")
            raise KeyError(f"Invalid type flag name '{i}'")

        else:
            debug(
                f"Invalid type flag name '{i}'; __raiseERR != True; suppressing error")

    if __rePlain:
        for i in out.keys():
            out[i] = out[i][0]

    debug(f"Returning edited kwargs {out}")
    return out


def __logError(errorCode: str, **kwargs):
    crash_msg: str = f"The application has encountered an error; internal diagnostics will be run during the next boot sequence of this application.\n\nDiagnostic Code: {errorCode}"

    flags = {

        'logError': [True, (bool,)],

        'exit': [False, (bool,)],
        'exitCode': [-1, (str, int)],

        'showUI': [True, (bool,)],
        'UI_Message': [crash_msg, (str,)],

        'runDiagnostics': [False, (bool,)],
        'diagnosticsInfo': [crash_msg, (str,)],
        'diagnosticsFunctionName': [QAJSONHandler.QAFlags().no_func_id, (str,)]

    };
    flags = flags_handler(flags, kwargs, __rePlain=True)

    if flags['logError']:
        debug(
            f"The application encountered an error; exit: {flags['exit']}; exitCode: {flags['exitCode']}, runDiagnostics: {flags['runDiagnostics']}, diagnostics_code: {flags['diagnosticsInfo']}, error code: {errorCode}")

    if flags['showUI']:
        tkmsb.showerror(apptitle, flags['UI_Message'])

    if flags['runDiagnostics']:  # TODO: fix this
        __inst = JSON()

        dinfo = ""
        dfunction = flags['diagnosticsFunctionName']

        __inst.logCrash(info=dinfo, functionCall=dfunction)

    if flags['exit']:
        application_exit(flags['exitCode'])


def loadData_extern(filepath, errorCode) -> list:
    try:
        connector = sqlite3.connect(filepath)
        cursor = connector.cursor()

        with connector:
            cursor.execute(
                "SELECT * FROM config"
            )
            conf_raw = cursor.fetchall()[0]

            cursor.execute(
                "SELECT * FROM qas"
            )
            qas_raw = cursor.fetchall()[0]

        connector.commit()
        connector.close()

        debug("conf_raw = ", conf_raw, "\nqas_raw = ", qas_raw)

        config = {
            'customQuizConfig': conf_raw[0],
            'partOrAll': conf_raw[1],
            'poa_divF': conf_raw[2],
            'a_deduc': conf_raw[3],
            'deduc_amnt': conf_raw[4]
        }

        try:
            qas_raw = qas_raw[0]
            questions = ld_q_fr(qas_raw, errorCode)

        except IndexError:
            questions = {}

        except:
            questions = errorCode

        return [config, questions]

    except Exception as e:
        debug(f"Error whilst reading DB: ", e)
        return errorCode


def loadData_intern(errorCode) -> list:
    try:

        def get_conf(flagID: str):
            return JSON().getFlag(
                os.path.join(QAInfo.appdataLoc, QAInfo.confFilename).replace('/', '\\').strip(),
                flagID,
                return_boolean=False
            )

        config = {
            'customQuizConfig': get_conf('acqc'),
            'partOrAll': get_conf('qpoa'),
            'poa_divF': get_conf('qsdf'),
            'a_deduc': get_conf('dma'),
            'deduc_amnt': get_conf('pdpir')
        }

        questions = ld_q_fr(
            IO(
                os.path.join(QAInfo.appdataLoc, QAInfo.qasFilename).replace('/', '\\').strip()
            ).autoLoad(),
            errorCode
        )

        return [config, questions]

    except Exception as E:
        debug("Error whilst loading data from internal files: ", E)
        return errorCode


def ld_q_fr(raw_questions: str, errorCode) -> dict:
    try:
        return QAQuestionStandard.convRawToDict(raw_questions.strip())

    except Exception as e:
        debug("Error whilst loading questions: ", e)
        return errorCode


def application_exit(code: str = "0") -> None:
    debug(f"Exiting with code '{code}'")
    sys.exit(code)


# ===============
# End of function declarations
# Below are the boot steps
# ===============

# Adjust Splash
set_boot_progress(4)
# Boot checks go here

JSON().boot_check()

# Adjust Splash
set_boot_progress(5)
# OVC

try:
    if not QA_OVC.check():
        QASplash.hide(splObj)
        tkmsb.showwarning(apptitle,
                          f"You are running an older version of the application; the database suggests that version '{QA_OVC.latest()}' is the latest (the current installed version is {QAInfo.versionData.get(QAInfo.VFKeys.get('v'))})")
        QASplash.show(splObj)

except:
    tkmsb.showwarning(apptitle, f"Non fatal: Failed to load version information (online)")

# Final Splash Settings
if not QAInfo.doNotUseSplash:
    show_splash_completion()  # Show completion
    QASplash.destroy(splObj)  # Close the splash screen

LoginUI()
