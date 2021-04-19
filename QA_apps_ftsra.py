import qa_time as QATime
import qa_logging as QaLog
import qa_appinfo as QAInfo
import qa_diagnostics as QADiagnostics
import qa_theme as QATheme
import qa_globalFlags as QAJSONHandler
import qa_fileIOHandler as QAFileIOHandler
import qa_quizConfig as QAConfigStandard

# Python default modules
import sys, os, threading, shutil, traceback, math
import tkinter as tk
from tkinter import messagebox as tkmsb
from tkinter import filedialog as tkfile
from tkinter import ttk


# Class Declarations

class UI(threading.Thread):
    def __init__(self, **flags):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.root = tk.Toplevel()
        self.root.withdraw()
        self.main_frame = tk.Frame(self.root)
        self.progress_frame = tk.Frame(self.root)

        self.theme = QATheme.Get().get('theme')

        self.titleLbl = tk.Label(self.root)
        self.main_container = tk.LabelFrame(self.main_frame)
        self.misc_container = tk.LabelFrame(self.main_frame)
        self.owr_all_btn = tk.Button(self.main_container)
        self.owr_config_btn = tk.Button(self.main_container)
        self.cpy_missing_btn = tk.Button(self.main_container)
        self.instructions_button = tk.Button(self.misc_container)
        self.check_button = tk.Button(self.misc_container)

        self.progress_ttl_lbl = tk.Label(self.progress_frame)
        self.progress_lb = tk.Listbox(self.progress_frame)
        self.progress_vsb = ttk.Scrollbar(self.progress_frame)
        self.progress_xsb = ttk.Scrollbar(self.progress_frame, orient=tk.HORIZONTAL)

        self.ws = (
            700 if 700 <= self.root.winfo_screenwidth() else self.root.winfo_screenwidth(),
            650 if 650 <= self.root.winfo_screenheight() else self.root.winfo_screenheight()
        )
        self.sp = (
            int(self.root.winfo_screenwidth() / 2 - self.ws[0] / 2),
            int(self.root.winfo_screenheight() / 2 - self.ws[1] / 2)
        )

        self.rootTitle = "QA Recovery Utilities"
        self.rootIcon = QAInfo.icons_ico['ftsra']

        self.listbox_counter = 0
        self.listbox_items = []

        self.up_elements = {
            'btns': [],
            'lbls': [],
            'frames': [],
            'ac_fg': [],
            'fonts': []
        }

        self.padX = 20
        self.padY = 10

        self.start()
        self.root.mainloop()

    def close_window(self):
        self.root.after(0, self.root.quit)

    def run(self):
        self.root.title(self.rootTitle)
        self.root.iconbitmap(self.rootIcon)
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)
        self.root.geometry("%sx%s+%s+%s" % (
            str(self.ws[0]),
            str(self.ws[1]),
            str(self.sp[0]),
            str(self.sp[1])
        ))

        self.up_elements['btns'].extend([
            self.cpy_missing_btn,
            self.owr_all_btn,
            self.owr_config_btn,
            self.check_button,
            self.instructions_button
        ])

        self.up_elements['lbls'].extend([
            self.titleLbl,
            self.main_container,
            self.misc_container,
            self.progress_ttl_lbl
        ])

        self.up_elements['frames'].extend([
            self.root,
            self.main_frame,
            self.progress_frame
        ])

        self.up_elements['ac_fg'].extend([
            self.titleLbl,
            self.misc_container,
            self.main_container,
            self.progress_ttl_lbl
        ])

        self.up_elements['fonts'].extend([
            [self.titleLbl, (self.theme.get('font'), 24)],
            [self.main_container, (self.theme.get('font'), self.theme.get('fsize_para'))],
            [self.misc_container, (self.theme.get('font'), self.theme.get('fsize_para'))],
            [self.cpy_missing_btn, (self.theme.get('font'), self.theme.get('btn_fsize'))],
            [self.owr_config_btn, (self.theme.get('font'), self.theme.get('btn_fsize'))],
            [self.owr_all_btn, (self.theme.get('font'), self.theme.get('btn_fsize'))],
            [self.instructions_button, (self.theme.get('font'), self.theme.get('btn_fsize'))],
            [self.check_button, (self.theme.get('font'), self.theme.get('btn_fsize'))],
            [self.progress_ttl_lbl, (self.theme.get('font'), self.theme.get('fsize_para'))]
        ])

        # Final
        self.layout()
        self.update_ui()
        self.root.deiconify()

    def update_ui(self, refresh_layout=False):

        if refresh_layout:
            self.clear_all_frames()
            self.layout()

        for element in self.up_elements['frames']:
            element.config(bg=self.theme.get('bg'))

        for element in self.up_elements['lbls']:
            element.config(
                bg=self.theme.get('bg'),
                fg=self.theme.get('fg')
            )

        for element in self.up_elements['btns']:
            element.config(
                bg=self.theme.get('bg'),
                fg=self.theme.get('fg'),
                activebackground=self.theme.get('ac'),
                activeforeground=self.theme.get('hg'),
                bd='0'
            )

        for element in self.up_elements['fonts']:
            element[0].config(
                font=element[1]
            )

        for element in self.up_elements['ac_fg']:
            element.config(fg=self.theme.get('ac'))

        self.progress_lb.config(
            bg=self.theme.get('bg'),
            fg=self.theme.get('fg'),
            font=(self.theme.get('font'), self.theme.get('fsize_para')),
            selectmode=tk.EXTENDED,
            selectbackground=self.theme.get('ac'),
            selectforeground=self.theme.get('hg')
        )

    def root_elements(self):
        elements = self.root.winfo_children()

        for i in elements:
            if i.winfo_children(): elements.extend(i.winfo_children())

        _all = [*elements]

        return _all, elements

    def clear_all_frames(self):
        for i in self.root_elements():
            try:
                i.pack_forget()
            except:
                pass

    def layout(self):
        self.titleLbl.config(text=self.rootTitle)
        self.titleLbl.pack(fill=tk.BOTH, padx=self.padX, pady=self.padY)

        self.main_container.config(text="Recovery Utilities")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=self.padX, pady=(self.padY, self.padY / 2))

        self.misc_container.config(text="Other Utilities")
        self.misc_container.pack(fill=tk.BOTH, expand=True, padx=self.padX, pady=(self.padY / 2, self.padY))

        self.owr_all_btn.config(
            text="Overwrite All Files",
            command=self.overwrite_all
        )

        self.owr_all_btn.pack(
            fill=tk.BOTH, expand=True, padx=(self.padX, self.padX / 2), pady=self.padY, side=tk.LEFT
        )

        self.owr_config_btn.config(
            text="Reset Configuration File",
            command=self.overwrite_config
        )

        self.owr_config_btn.pack(
            fill=tk.BOTH, expand=True, padx=self.padX / 2, pady=self.padY, side=tk.RIGHT
        )

        self.cpy_missing_btn.config(
            text="Patch Missing Files",
            command=self.cpy_missing
        )

        self.cpy_missing_btn.pack(
            fill=tk.BOTH, expand=True, padx=(self.padX / 2, self.padX), pady=self.padY, side=tk.RIGHT
        )

        self.instructions_button.config(
            text="Instructions",
            command=self.open_help_file
        )

        self.instructions_button.pack(
            fill=tk.BOTH, expand=True, padx=self.padX / 2, pady=self.padY, side=tk.RIGHT
        )

        self.check_button.config(
            text="Check Files",
            command=self.diagnostics
        )

        self.check_button.pack(
            fill=tk.BOTH, expand=True, padx=(self.padX / 2, self.padX), pady=self.padY, side=tk.RIGHT
        )

        self.progress_ttl_lbl.config(
            text="Activity",
            anchor=tk.W,
            justify=tk.LEFT
        )
        self.progress_ttl_lbl.pack(fill=tk.BOTH, padx=self.padX)

        self.progress_xsb.pack(fill=tk.X, side=tk.BOTTOM, padx=self.padX, pady=(0, self.padY))
        self.progress_lb.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(self.padX, 0))
        self.progress_vsb.pack(fill=tk.Y, side=tk.RIGHT, padx=(0, self.padX))

        self.progress_lb.config(yscrollcommand=self.progress_vsb.set, xscrollcommand=self.progress_xsb.set)
        self.progress_vsb.config(command=self.progress_lb.yview)
        self.progress_xsb.config(command=self.progress_lb.xview)

        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.progress_frame.pack(fill=tk.BOTH, expand=True)

    def clear_lb(self):
        self.listbox_counter = 0
        self.listbox_items = []

        self.progress_lb.delete(0, tk.END)

    def insert_into_lb(self, string, index: int = tk.END) -> int:
        string = str(string)
        self.listbox_counter += 1
        self.listbox_items.append(string)

        self.progress_lb.insert(index, string)
        self.progress_lb.yview(tk.END)
        self.root.update()

        return self.listbox_counter - 1

    def lb_show_ok(self, index: int):
        if index < 0 or index > len(self.listbox_items) - 1: return

        self.progress_lb.itemconfig(
            index,
            background="#ffffff", foreground="#00802b",
            selectbackground="#00802b",
            selectforeground="#ffffff"
        )

    def lb_show_error(self, index: int):
        if index < 0 or index > len(self.listbox_items) - 1: return

        self.progress_lb.itemconfig(
            index,
            background="#ffffff", foreground="#800000",
            selectbackground="#800000",
            selectforeground="#ffffff"
        )

    def overwrite_all(self):
        self.clear_lb()

        conf = tkmsb.askyesno(self.rootTitle, "Are you sure you want to delete all files (excluding scores and logs?)")
        if not conf:
            self.lb_show_error(self.insert_into_lb("User refused to overwrite all files; aborting"))
            return

        self.lb_show_ok(self.insert_into_lb("Re-writing basic application files..."))

        # Backup
        try:
            conf = tkmsb.askyesno(self.rootTitle,
                                  "Would you like to export the current application data prior to re-writing all application files?")
            if not conf:
                self.insert_into_lb("User does not want to create backup file")
                raise Exception

            if not os.path.exists(os.path.join(QAInfo.appdataLoc, ".ra_backups")):
                os.makedirs(os.path.join(QAInfo.appdataLoc, ".ra_backups"))

            filename = "{}\\{}\\{} {}.qaEnc".format(
                QAInfo.appdataLoc,
                ".ra_backups",
                "qaGFileBackup",
                QATime.form("%H-%M-%S %b %d, %Y")
            )

            self.insert_into_lb("Creating backup file\n{}".format(filename.split("\\")[-1]))
            self.insert_into_lb("Read data from files")

            try:
                config_raw = QAFileIOHandler.read(
                    QAFileIOHandler.create_fileIO_object(
                        os.path.join(QAInfo.appdataLoc, QAInfo.confFilename)
                    )
                )

            except:
                config_raw = "QAS :: FileNotFound"

            try:
                qas_raw = QAFileIOHandler.read(
                    QAFileIOHandler.create_fileIO_object(
                        os.path.join(QAInfo.appdataLoc, QAInfo.qasFilename)
                    )
                )
            except:
                qas_raw = "QAS :: FileNotFound"

            try:
                theme_raw = QAFileIOHandler.read(
                    QAFileIOHandler.create_fileIO_object(
                        os.path.join(QAInfo.appdataLoc, QAInfo.themeFilename)
                    )
                )

            except:
                theme_raw = "QAS :: FileNotFound"

            self.insert_into_lb("Creating backup file")

            QAJSONHandler.QAFlags().io(
                QAJSONHandler.QAFlags().SET,
                filename=filename,
                appendData=False,
                data={
                    'c': config_raw,
                    'q': qas_raw,
                    't': theme_raw
                }
            )

            # Encrypt the file
            self.insert_into_lb("Encrypting backup file")
            file_inst = QAFileIOHandler.InstanceGenerator(filename, QAInfo.qaEnck)
            QAFileIOHandler.encrypt(file_inst)

            self.insert_into_lb("")
            self.lb_show_ok(
                self.insert_into_lb("Created backup file successfully")
            )

        except Exception as E:

            debug(f"Error whilst creating backup file (ftsra:ovw_all) [E] [tb]", E, " ", traceback.format_exc())

            self.insert_into_lb("")
            self.lb_show_error(
                self.insert_into_lb("Failed to create backup")
            )

        self.insert_into_lb("")

        # Copy + Delete

        errors = {}
        success = []
        skipped = []

        location = QAInfo.appdataLoc
        for i in os.listdir(location):
            file = os.path.join(location, i).replace('/', '\\')

            try:
                if os.path.isfile(file) and file.split('\\')[-1] in QAInfo.QaFTSRAFiles:

                    if os.path.isfile(QAInfo.ftsFolder + "\\" + file.split('\\')[-1]):

                        os.remove(file)
                        success.append(file)
                        self.insert_into_lb(f"Removed file {i} successfully")

                    else:
                        self.insert_into_lb("")
                        ind = self.insert_into_lb(
                            f"Error: Cannot reset file {i} because its default version is not available (QA-NDF)")
                        self.lb_show_error(ind)
                        self.insert_into_lb("")

                        raise FileNotFoundError(
                            "A file that was to be copied into the application data folder was not found; filename: {}".format(
                                file.split('\\')[-1]
                            )
                        )

                else:
                    skipped.append([file, os.path.isfile(file)])
                    self.insert_into_lb(f"Skipped {i}")

            except Exception as E:

                errors[file] = [E, traceback.format_exc()]

        self.insert_into_lb("")

        loc2 = QAInfo.ftsFolder
        for i in os.listdir(loc2):
            file = os.path.join(loc2, i).replace('/', '\\')

            try:
                if os.path.isfile(file):
                    with open(file, 'rb') as src, open(location + "\\" + i, 'wb') as dst:
                        dst.write(src.read())
                        dst.close();
                        src.close()

                    ind = self.insert_into_lb(f"Successfully reset {i}")
                    self.lb_show_ok(ind)

            except Exception as E:
                ind = self.insert_into_lb(f"Failed to copy file {i} (damage could have been inflicted)")
                self.lb_show_error(ind)
                debug(f"Failed to copy file {i}; {E} {traceback.format_exc()}")

        if not os.path.exists(os.path.join(QAInfo.appdataLoc, QAInfo.scoresFolderName)):
            self.insert_into_lb("Scores folder not found; creating folder")

            try:
                os.makedirs(os.path.join(QAInfo.appdataLoc, QAInfo.scoresFolderName))

                self.lb_show_ok(self.insert_into_lb("Created Scores folder"))

            except Exception as E:
                debug(f"Failed to create scores folder; [e] [tb]", E, " ", traceback.format_exc())

        debug("overwrite_all: {errors}, {success}, {skipped}", errors, " ", success, " ", skipped)
        tkmsb.showinfo(
            self.rootTitle,
            f"Successfully reset {len(errors)} files, and skipped {len(skipped)} (+{len(errors)} errors)"
        )

    def overwrite_config(self):
        self.clear_lb()
        self.lb_show_ok(
            self.insert_into_lb("Reset Configuration File? (User-Input required)")
        )

        conf = tkmsb.askyesno(self.rootTitle, "Are you sure you want to reset the configuration file?")

        if not conf:
            self.lb_show_error(
                self.insert_into_lb("User aborted the utility.")
            )
            return

        # Backup
        try:
            bConf = tkmsb.askyesno(self.rootTitle, "Do you want to generate a backup file before resetting the file?")

            if not bConf:
                self.lb_show_error(
                    self.insert_into_lb("User aborted the creation of the backup file.")
                )

                raise Exception("Null-01")

            filename = "{}\\{}\\{} {}.qaEnc".format(
                QAInfo.appdataLoc,
                ".ra_backups",
                "qaCFileBackup",
                QATime.form("%H-%M-%S %b %d, %Y")
            )

            self.insert_into_lb("Creating backup file\n{}".format(filename.split("\\")[-1]))
            self.insert_into_lb("Read data from old configuration")

            config_raw = QAFileIOHandler.read(
                QAFileIOHandler.create_fileIO_object(
                    os.path.join(QAInfo.appdataLoc, QAInfo.confFilename)
                )
            )

            self.insert_into_lb("Creating backup file")

            QAJSONHandler.QAFlags().io(
                QAJSONHandler.QAFlags().SET,
                filename=filename,
                appendData=False,
                data={'c': config_raw}
            )

            # Encrypt the file
            self.insert_into_lb("Encrypting backup file")
            file_inst = QAFileIOHandler.InstanceGenerator(filename, QAInfo.qaEnck)
            QAFileIOHandler.encrypt(file_inst)

            self.insert_into_lb("")
            self.lb_show_ok(
                self.insert_into_lb("Created backup file successfully")
            )

        except Exception as E:
            debug(f"Failed to create backup [e] [tb] ", E, ' ', traceback.format_exc())

        self.insert_into_lb("")

        self.insert_into_lb("Resetting configuration file")

        with open(
                os.path.join(QAInfo.appdataLoc, QAInfo.confFilename), 'wb'
        ) as dstFile, open(
            os.path.join(QAInfo.ftsFolder, QAInfo.confFilename), 'rb'
        ) as srcFile:
            dstFile.write(srcFile.read())
            srcFile.close()
            dstFile.close()

        self.lb_show_ok(
            self.insert_into_lb("Reset configuration file successfully!")
        )

        tkmsb.showinfo(self.rootTitle, "Reset configuration file successfully!")

    def cpy_missing(self):

        added = [];
        total = []

        self.clear_lb()
        self.insert_into_lb("Patching missing files")
        self.insert_into_lb("")

        for i in os.listdir(QAInfo.ftsFolder):
            try:

                if os.path.isfile(
                        os.path.join(QAInfo.ftsFolder, i)
                ) and not os.path.exists(os.path.join(QAInfo.appdataLoc, i)):
                    total.append(i)

                    with open(os.path.join(QAInfo.ftsFolder, i), 'rb') as src, open(os.path.join(QAInfo.appdataLoc, i),
                                                                                    'wb') as dst:
                        dst.write(src.read())
                        dst.close()
                        src.close()

                    self.lb_show_ok(
                        self.insert_into_lb(f"Patched file {i}")
                    )

                    added.append(i)

                else:
                    if os.path.exists(os.path.join(QAInfo.appdataLoc, i)):
                        self.insert_into_lb(f"File {i} did not need to be patched (it already exists)")

                    else:
                        self.insert_into_lb(f"Skipped {i}")

            except Exception as E:
                self.lb_show_error(
                    self.insert_into_lb(f"Failed to patch file {i}")
                )

                debug(f"Failed to patch file ", i, " [e] [tb] ", E, " ", traceback)

        if not os.path.exists(
                os.path.join(QAInfo.appdataLoc, QAInfo.scoresFolderName)
        ):
            self.insert_into_lb("Patching Scores folder")
            os.makedirs(os.path.join(QAInfo.appdataLoc, QAInfo.scoresFolderName))
            self.lb_show_ok(self.insert_into_lb("Patched Scores folder"))

        self.lb_show_ok(self.insert_into_lb("Patched {}/{} missing files".format(len(added), len(total))))
        tkmsb.showinfo(self.rootTitle, "Patched {}/{} missing files".format(len(added), len(total)))

    def open_help_file(self):
        openFile(QAInfo.help_files['ftsra'])

    def diagnostics(self):
        self.clear_lb()
        self.lb_show_ok(self.insert_into_lb("Running diagnostic checks"))
        self.insert_into_lb("")

        logs = [];
        fails = 0
        log_ext = ".qaLog";
        log_folder = ".ra_logs"

        # Basic checks
        self.insert_into_lb("Running basic checks")
        self.insert_into_lb("")

        # .fts
        for i in QAInfo.QaFTSRAFiles:
            if not os.path.exists(os.path.join(QAInfo.ftsFolder, i)):
                fails += 1
                logs.append("L_FTS_D_FE: {i} - FAILED")
                self.lb_show_error(self.insert_into_lb(f"L_FTS_D_FE: {i} - FAILED"))

            else:
                logs.append("L_FTS_D_FE: {i} - PASSED")
                self.lb_show_ok(self.insert_into_lb(f"L_FTS_D_FE: {i} - PASSED"))

        self.insert_into_lb("")

        # AppData
        for i in QAInfo.QaFTSRAFiles:
            if not os.path.exists(os.path.join(QAInfo.appdataLoc, i)):
                logs.append("L_ApD_D_FE: {i} - FAILED")
                fails += 1
                self.lb_show_error(self.insert_into_lb(f"L_ApD_D_FE: {i} - FAILED"))

            else:
                logs.append("L_ApD_D_FE: {i} - PASSED")
                self.lb_show_ok(self.insert_into_lb(f"L_ApD_D_FE: {i} - PASSED"))

        # In-D checks
        self.insert_into_lb("")
        self.insert_into_lb("Running in-depth checks")
        self.insert_into_lb("")

        # Configuration File
        self.insert_into_lb(f"Checking configuration file")

        if os.path.exists(
                os.path.join(QAInfo.ftsFolder, QAInfo.confFilename)
        ):
            confErr = False

            _json = QAJSONHandler.load_json(os.path.join(QAInfo.ftsFolder, QAInfo.confFilename))

            counter = 0
            for i in QAConfigStandard.default_configuration:
                counter += 1

                if not i in _json or type(_json.get(i)) is not type(QAConfigStandard.default_configuration.get(i)):
                    logs.append(f"L_FTS_InD-C::CONFIG - FAILED (Key {i} not found or found corrupted data for key)")
                    self.lb_show_error(
                        self.insert_into_lb(
                            f"L_FTS_InD-C::CONFIG - FAILED (Key {i} not found or found corrupted data for key)")
                    )
                    fails += 1
                    confErr = True

                else:
                    logs.append(
                        f"L_FTS_InD-C::CONFIG - Key test {counter}/{len(QAConfigStandard.default_configuration)} PASSED")
                    self.lb_show_ok(
                        self.insert_into_lb(
                            f"L_FTS_InD-C::CONFIG - Key test {counter}/{len(QAConfigStandard.default_configuration)} PASSED")
                    )

            self.insert_into_lb("")

            if not confErr:
                logs.append(f"L_FTS_InD-C::CONFIG - PASSED")
                self.lb_show_ok(
                    self.insert_into_lb(f"L_FTS_InD-C::CONFIG - Summary: PASSED")
                )

            else:
                logs.append(f"L_FTS_InD-C::CONFIG - FAILED")
                self.lb_show_error(
                    self.insert_into_lb(f"L_FTS_InD-C::CONFIG - Summary: FAILED")
                )

            self.insert_into_lb("")

        else:
            fails += 1
            logs.append("L_FTS_InD-C::CONFIG - FAILED (File not found)")
            self.lb_show_error(
                self.insert_into_lb("L_FTS_InD-C::CONFIG - FAILED (File not found)")
            )

        if os.path.exists(
                os.path.join(QAInfo.appdataLoc, QAInfo.confFilename)
        ):
            confErr = False

            _json = QAJSONHandler.load_json(os.path.join(QAInfo.appdataLoc, QAInfo.confFilename))

            counter = 0
            for i in QAConfigStandard.default_configuration:
                counter += 1

                if not i in _json or type(_json.get(i)) is not type(QAConfigStandard.default_configuration.get(i)):
                    logs.append(f"L_ApD_InD-C::CONFIG - FAILED (Key {i} not found or found corrupted data for key)")
                    self.lb_show_error(
                        self.insert_into_lb(
                            f"L_ApD_InD-C::CONFIG - FAILED (Key {i} not found or found corrupted data for key)")
                    )
                    fails += 1
                    confErr = True

                else:
                    logs.append(f"L_ApD_InD-C::CONFIG - Key test {counter}/{len(QAConfigStandard.default_configuration)} PASSED")
                    self.lb_show_ok(
                        self.insert_into_lb(
                            f"L_ApD_InD-C::CONFIG - Key test {counter}/{len(QAConfigStandard.default_configuration)} PASSED")
                    )

            self.insert_into_lb("")

            if not confErr:
                logs.append(f"L_ApD_InD-C::CONFIG - PASSED")
                self.lb_show_ok(
                    self.insert_into_lb(f"L_ApD_InD-C::CONFIG - Summary: PASSED")
                )

            else:
                logs.append(f"L_ApD_InD-C::CONFIG - FAILED")
                self.lb_show_error(
                    self.insert_into_lb(f"L_ApD_InD-C::CONFIG - Summary: FAILED")
                )

            self.insert_into_lb("")

        else:
            fails += 1
            logs.append("L_ApD_InD-C::CONFIG - FAILED (File not found)")
            self.lb_show_error(
                self.insert_into_lb("L_ApD_InD-C::CONFIG - FAILED (File not found)")
            )

        # Checking Theme File
        self.insert_into_lb("Checking Theme File")

        def load_theme_file(filename) -> dict:
            data_raw = QAFileIOHandler.read(
                QAFileIOHandler.create_fileIO_object(filename)
            )

            output = {}

            for line in data_raw.split("\n"):
                line = line.strip()

                if len(line.strip()) > 0:

                    if line[0] != "#":

                        k = line.split(' ')[0].strip()
                        v = line.replace(k, '', 1).strip()

                        if k in QATheme.default:
                            v = type(QATheme.default[k])(v)  # Set the right type

                        output[k] = v

            return output

        if os.path.exists(
                os.path.join(QAInfo.ftsFolder, QAInfo.themeFilename)
        ):

            themeErr = False
            theme_ex = QATheme.default
            theme_fts = load_theme_file(os.path.join(QAInfo.ftsFolder, QAInfo.themeFilename))

            counter = 0
            for i in theme_ex:
                counter += 1

                if not i in theme_fts or type(theme_ex.get(i)) is not type(theme_fts.get(i)):
                    logs.append(f"L_FTS_InD-C::THEME - FAILED (Key {i} not found or found corrupted data for key)")
                    self.lb_show_error(
                        self.insert_into_lb(
                            f"L_FTS_InD-C::THEME - FAILED (Key {i} not found or found corrupted data for key)")
                    )
                    fails += 1
                    themeErr = True

                else:
                    logs.append(f"L_FTS_InD-C::THEME - Key Check {counter}/{len(theme_ex)} - PASSED")
                    self.lb_show_ok(
                        self.insert_into_lb(
                            f"L_FTS_InD-C::THEME - Key Check {counter}/{len(theme_ex)} - PASSED")
                    )

            if not themeErr:
                logs.append(f"L_FTS_InD-C::THEME - PASSED")
                self.lb_show_ok(
                    self.insert_into_lb(f"L_FTS_InD-C::THEME - Summary: PASSED")
                )

            else:
                logs.append(f"L_FTS_InD-C::THEME - FAILED")
                self.lb_show_error(
                    self.insert_into_lb(f"L_FTS_InD-C::THEME - Summary: FAILED")
                )

        else:
            fails += 1
            logs.append("L_FTS_InD-C::THEME - FAILED (File not found)")
            self.lb_show_error(
                self.insert_into_lb("L_FTS_InD-C::THEME - FAILED (File not found)")
            )

        self.insert_into_lb("")

        if os.path.exists(
                os.path.join(QAInfo.appdataLoc, QAInfo.themeFilename)
        ):
            themeErr = False
            theme_ex = QATheme.default
            theme_fts = load_theme_file(os.path.join(QAInfo.appdataLoc, QAInfo.themeFilename))

            counter = 0
            for i in theme_ex:
                counter += 1

                if not i in theme_fts or type(theme_ex.get(i)) is not type(theme_fts.get(i)):
                    logs.append(f"L_ApD_InD-C::THEME - FAILED (Key {i} not found or found corrupted data for key)")
                    self.lb_show_error(
                        self.insert_into_lb(
                            f"L_ApD_InD-C::THEME - FAILED (Key {i} not found or found corrupted data for key)")
                    )
                    fails += 1
                    themeErr = True

                else:
                    logs.append(f"L_ApD_InD-C::THEME - Key Check {counter}/{len(theme_ex)} - PASSED")
                    self.lb_show_ok(
                        self.insert_into_lb(
                            f"L_ApD_InD-C::THEME - Key Check {counter}/{len(theme_ex)} - PASSED")
                    )

            if not themeErr:
                logs.append(f"L_ApD_InD-C::THEME - PASSED")
                self.lb_show_ok(
                    self.insert_into_lb(f"L_ApD_InD-C::THEME - Summary: PASSED")
                )

            else:
                logs.append(f"L_ApD_InD-C::THEME - FAILED")
                self.lb_show_error(
                    self.insert_into_lb(f"L_ApD_InD-C::THEME - Summary: FAILED")
                )

        else:
            fails += 1
            logs.append("L_ApD_InD-C::THEME - THEME (File not found)")
            self.lb_show_error(
                self.insert_into_lb("L_ApD_InD-C::THEME - FAILED (File not found)")
            )

        # -------------
        # Final Summary
        # -------------

        try:
            os.makedirs(
                os.path.join(QAInfo.appdataLoc, log_folder)
            )

        except: pass

        filename = "{}\\{} {}.{}".format(
            os.path.join(QAInfo.appdataLoc, log_folder),
            "RA_CHECK_LOG",
            QATime.form("%H-%M-%S %b %d, %Y"),
            log_ext
        )

        with open(filename, 'w') as logFile:
            logFile.writelines(logs)
            logFile.close()

        self.insert_into_lb("")
        self.insert_into_lb("FINAL SUMMARY:")
        ind = self.insert_into_lb(f"Finished Tests; {fails}/{len(logs)} failures recorded.")
        self.insert_into_lb("The results of this test were logged.")

        if fails != 0:
            self.lb_show_error(ind)

        else:
            self.lb_show_ok(ind)

    def __del__(self):
        self.thread.join(self, 0)


class CrashHandler(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.jsonHandler_instance = QAJSONHandler.QAFlags()

        self.start()

    def log_crash(self, time, info: str, function: str):
        debug(f"Logging crash from time {time}")

        # Variables
        global apptitle
        time = f"{time}"  # "Convert" to string
        ID = self.jsonHandler_instance.ftsra_crash_id

        # Log
        json_setFlag(ID, {
            self.jsonHandler_instance.log_time_id: time,
            self.jsonHandler_instance.log_function_id: function,
            self.jsonHandler_instance.log_info_id: info,
            self.jsonHandler_instance.log_unr_id: True
        })

    def log_event(self, ID: str, info: any):
        if ID is None: ID = self.jsonHandler_instance.no_func_id

        debug(f"Logging event with ID {ID} ")
        json_setFlag(ID, info)

    def boot_check(self) -> bool:
        result = True  # True = passed, False = failed, ran scripts
        global apptitle

        if json_getFlag(self.jsonHandler_instance.ftsra_crash_id):  # If the thing exists
            debug(f"An error log exists in the global_nv_flags file")

            check2 = json_getFlag(self.jsonHandler_instance.ftsra_crash_id, mode=any)

            if check2[self.jsonHandler_instance.log_unr_id]:  # If unresolved
                tkmsb.showerror(apptitle,
                                f"Found unresolved boot error flags; running diagnostics.\n\nPress OK to continue.")

                debug(f"The error was marked as unresolved; running diagnostics.")
                result = False

                logged_info = {
                    'function': check2[self.jsonHandler_instance.log_function_id],
                    'time': check2[self.jsonHandler_instance.log_time_id],
                    'info': check2[self.jsonHandler_instance.log_info_id]
                }

                debug(f"Time of error: {logged_info['time']}; info: {logged_info['info']}")
                debug(f"Running diagnostics script with key {logged_info['function']}")

                # Run Diagnostics
                diagnostics = QADiagnostics.Diagnostics()
                diagnostics_results = diagnostics.run_diagnostics(key=logged_info['function'])

                if not diagnostics_results:
                    debug(f"Diagnostics failed; running correction scripts")
                    tkmsb.showerror(apptitle,
                                    f"Failed requested tests; running correction scripts.\n\nPress OK to continue.")

                    # Corrections
                    corrections = QADiagnostics.Corrections()
                    corrections.run_correction(logged_info['function'])

                else:
                    debug(f"Diagnostics passed; still returning False")
                    tkmsb.showinfo(apptitle, f"Passed requested tests")

                # Log event in the same file
                ID = self.jsonHandler_instance.FTSRA_timed_log.strip() + f"{QATime.now()}"
                debug(f"Logging boot error/corrections with key {ID}")

                debug(f"Marking error as 'RESOLVED'")
                toSave = check2
                toSave[self.jsonHandler_instance.log_unr_id] = False
                json_setFlag(self.jsonHandler_instance.ftsra_crash_id, toSave)
                tkmsb.showinfo(apptitle, f"Cleared boot-error flag.")

                self.log_event(ID, {
                    'crash_time': logged_info['time'],
                    'crash_info': logged_info['info'],
                    'crash_function_key': logged_info['function'],
                    'crash_diagnostics_passed': diagnostics_results
                })

            else:
                debug(
                    f"Error was marked as resolved before correction or diagnostics scripts were ran; starting app normally.")

        return result

    def __del__(self):
        self.thread.join(self, 0)


class ErrorHandler(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.ch_instance = CrashHandler()

        self.start()

    def error_handler(self, err_info: str = "No diagnostic information", **flags) -> None:
        """
        **QA_APPS_FTSRA.ErrorHandler.error_handler**

        :param err_info: Error Information (str)
        :param flags: Flags (dict; see Supported Flags for more information)
        :return: None

        ===================

        **Supported Flags**

        1) *exit*
            * Type: bool
            * Default: False
            * Other supported inputs: --
            * Information: Should the function terminate the application when done with the error handling?

        2) *exit_code*
            * Type: str, int
            * Other supported inputs: --
            * Default: 1 (int)
            * Information: The exit code to exit with (only applies if *exit* is set to *True*)

        3) *log_error*
            * Type: bool
            * Other Supported Inputs: --
            * Default: True
            * Information: Should the application log the error message to the debug file?

        4) *show_ui*
            * Type: bool
            * Other Supported Inputs: --
            * Default: True
            * Information: Should the error be shown on a tkinter.messagebox.showerror dialogue?

        5) *customUIMsg*
            * Type: str
            * Other Supported Inputs: *None* (NoneType)
            * Default: None
            * Information:
                * If set to *type str*, the application will display the given string in the error dialogue (applicable only for *show_ui* = *True*)
                * If set to *None*, the application will display a concatenated string of the base string + err_info in the error dialogue (applicable only for *show_ui* = *True*)

        6) *log_crash*
            * Type: bool
            * Other Supported Inputs: --
            * Default: False
            * Information: Automatically call *QA_apps_ftsra.CrashHandler.log_crash()* with the given information?

        7) *crash_function*
            * Type: str
            * Other Supported Inputs: --
            * Default: qa_diagnostics.Data.no_func_key
            * Information: Function key for the appropriate diagnostic + correction function; note that the key must be a valid variable in *qa_diagnostics*

        8) *crash_info*
            * Type: str
            * Other Supported Inputs: --
            * Default: "No Diagnostic Information"
            * Information: CrashHandler.crash_info; only required if *log_crash* is set to *True*


        ===================

        """

        # Globals
        global apptitle

        # Defaults
        no_func_id = QADiagnostics.Data()
        no_func_id = no_func_id.no_func_key

        def_cinfo = "No diagnostic information"

        Flags = {
            #
            'exit': [False, (False, bool)],
            'exit_code': [1, (1, str, int)],
            'log_error': [True, (True, bool)],
            'show_ui': [True, (True, bool)],
            'customUIMsg': [None, (None, type(None), str)],

            # Crash Handler
            'log_crash': [False, (False, bool)],
            'crash_function': [no_func_id, (no_func_id, str)],
            'crash_info': [def_cinfo, (def_cinfo, str)]
        }

        Flags = flags_handler(Flags, flags, __rePlain=True)

        # Step 1: Figure out the string (if needed)
        err_string = err_info
        base_str = "An error occurred whilst running an application script"
        severity_str = {
            'low': '.\n\nMore Diagnostic Information:\n',
            'high': ' and the application needs to be terminated due to the severity of the error.\n\nMore Diagnostic Information:\n'
        }

        if Flags['show_ui'] or Flags['log_error']:  # If needed; else don't waste time
            if Flags['customUIMsg'] is None:  # Use base.join(err_info)
                err_string = base_str.join([
                    severity_str['low'] if not Flags['exit'] else severity_str['high'],
                    err_info
                ])

            else:
                err_string = Flags['customUIMsg']  # Use custom str

        debug(f"Loaded the following error string: {err_string}")

        # Step 2: Show UI (if needed)
        temp = tkmsb.showerror(apptitle, err_string) if Flags['show_ui'] else None

        # Step 3: Log (If needed)
        debug(f"The following error occurred: {err_string}")  # time is shown in debug logs automatically.

        # Stp 4: CrashHandler (If needed)
        if Flags['log_crash']:
            self.ch_instance.log_crash(
                time=QATime.now(),
                info=Flags['crash_info'],
                function=Flags['crash_function']
            )

        # Step 5: Exit (if needed)
        temp = Exit(Flags['exit_code']) if Flags['exit'] else None

        debug(f"Finished error handling")

    def __del__(self):
        self.thread.join(self, 0)


# Functions
def Exit(_code: any = 0):
    sys.exit(_code)


def check_fl_input(FL, PE=True) -> bool:
    if type(FL) is not str:
        return False
    elif len(FL.strip()) <= 0:
        return False
    elif PE:
        if not os.path.exists(FL): return False

    return True


def debug(debug_data, *args) -> None:
    debug_data += "".join(str(i) for i in args)

    Log = QaLog.Log();
    LogVar = QaLog.Variables()
    sc_name = sys.argv[0].replace("/", "\\").split("\\")[-1].strip().split('.')[0].strip()  # Script name

    if not LogVar.genDebugFile(): Log.logFile_create(sc_name)
    Log.log(data=debug_data, from_=sc_name)

    return


def json_setFlag(flagID: str, data: any, **flags) -> None:
    """
    **QA_APPS_FTSRA.json_setFlag**

    :param flagID: Flag ID (dict key; str)
    :param data: Flag Data (dict data; any)
    :param flags: Flags (See Supported Flags)
    :return: None

    =================

    **Supported Flags**

    1) *filename*
        * Type: str
        * Other Supported Inputs: --
        * Default: qa_appinfo.appdataLoc + qa_globalFlags.flags_fn
        * Information: Location of the JSON file in question.

    2) *append*
        * Type: bool
        * Other Supported Inputs: --
        * Default: True [HIGHLY RECOMMENDED]
        * Information: Append new data to JSON file instead of a complete overwrite.

    3) *reloadJSON*
        * Type: bool
        * Other Supported Inputs: --
        * Default: True [HIGHLY RECOMMENDED]
        * Information: Reload JSON dictionary to memory before setting data, and after.

    =================

    """

    # Vars
    JSONHandlerInstance = QAJSONHandler.QAFlags()
    ref = JSONHandlerInstance.SET

    # Defaults
    fn = f"{QAInfo.appdataLoc}\\{JSONHandlerInstance.flags_fn}"

    # Flags
    Flags = {
        'filename': [fn, (fn, str)],
        'append': [True, (True, bool)],
        'reloadJSON': [True, (True, bool)]
    }

    Flags = flags_handler(Flags, flags, __rePlain=True)

    # Logic
    debug(f"Setting JSON flag in file {Flags['filename']} for {flagID} to {data}")

    JSONHandlerInstance.io(
        Key=ref,
        data={
            flagID: data
        },
        appendData=Flags['append'],
        reloadJSON=Flags['reloadJSON'],
        filename=Flags['filename']
    )


def json_getFlag(flagID: str, **flags) -> any:
    """
    **QA_APPS_FTSRA.json_getFlag**

    :param flagID: Flag ID (Dict Key; str)
    :param flags: Flags (See Supported Flags)
    :return: any

    ===========

    **Return Info**

    * The function will return whatever you've selected; this can be a boolean or any;
    * If set to *bool* mode, the *bool* output represents whether if there is any valid data for the requested key in the given file.
    * If set to *any* mode, the output is the data for the given flag ID; if the ID is invalid, the output will be *None*

    ==========

    **Supported Flags**

    1) *filename*
        * Type: str
        * Other Supported Inputs: --
        * Default: qa_appinfo.appdataLoc + qa_globalFlags.flags_fn
        * Information: Path to the JSON file

    2) *mode*
        * Type: type; supported: *any*, *bool*
        * Other Supported Inputs: --
        * Default: *bool*
        * Information: Read *Return Info*; note that if set to anything but *any* or *bool*, the variable will be reset to *bool mode*

    3) *reloadJSON*
        * Type: bool
        * Other Supported Inputs: --
        * Default: True (Highly Recommended)
        * Information: Update JSON to memory before querying flag ID.

    ==========

    """

    # Defaults
    JSONHandlerInstance = QAJSONHandler.QAFlags()
    def_fn = f"{QAInfo.appdataLoc}\\{JSONHandlerInstance.flags_fn}"

    # Flags
    Flags = {
        'filename': [def_fn, (def_fn, str)],  # JSON File
        'mode': [bool, (bool, type)],  # any = return the data; bool = return existence boolean
        'reloadJSON': [True, (True, bool)]  # reload JSON before getting flag data
    };
    Flags = flags_handler(Flags, flags, __rePlain=True)

    # Vars
    Key = JSONHandlerInstance.GET

    debug(f"Querying ID {flagID} in {Flags['filename']}")
    try:
        output = JSONHandlerInstance.io(Key=Key,
                                        key=flagID,
                                        reloadJSON=Flags['reloadJSON'],
                                        filename=Flags['filename'],
                                        re_bool=False if Flags['mode'] is any else True)
    except Exception as e:
        debug(
            f"An error was raised whilst querying for the flag; more information: {e.__class__.__name__}; {e}; {traceback.format_exc()}")
        output = None if Flags['mode'] is any else False

    debug(f"Query result for ID {flagID} in {Flags['filename']}: {output}")

    return output


def json_removeFlag(flagID: str, **flags) -> None:
    # Defaults
    JSONHandlerInstance = QAJSONHandler.QAFlags()
    def_fn = f"{QAInfo.appdataLoc}\\{JSONHandlerInstance.flags_fn}"

    # Flags
    Flags = {
        'filename': [def_fn, (def_fn, str)],
        'reloadJSON': [True, (True, bool)]
    };
    Flags = flags_handler(Flags, flags, __rePlain=True)

    # Vars
    Key = JSONHandlerInstance.REMOVE

    # Pop
    debug(f"Removing data for ID {flagID} in file {Flags['filename']}")

    JSONHandlerInstance.io(Key=Key,
                           key=flagID,
                           reloadJSON=Flags['reloadJSON'],
                           filename=Flags['filename'])


def openFile(path): os.startfile(os.path.realpath(path))


def flags_handler(ref: dict, flags: dict, __raiseErr: bool = True, __rePlain: bool = False) -> dict:
    """
    **BASIC INFORMATION ONLY**

    :param ref: Reference dictionary
    :param flags: Flags given
    :param __raiseErr: Raise error (def True)
    :param __rePlain: Return plain data (only index 0 from Expected Syntax) (def False)
    :return: Adjusted dictionary

    Expected syntax:
    {
        'flag name' : List[<set>, Tuple(<default value>, *<types>)]
    }
    """
    output = ref

    for i in flags:

        if i in ref:  # If flag is valid

            if type(flags[i] in ref[i][1][1::]):  # If type is valid
                output[i] = [flags[i], ref[i][1]]  # Reset
                debug(f"Set flag '{i}' to {output[i]}")

            elif __raiseErr:  # Raise Error
                debug(
                    f"Invalid type for flag '{i}' (expected {ref[i][1][1::]}, got {type(flags[i])}); raising error for __raiseErr is set to True")
                raise TypeError(f"Invalid type for flag '{i}' (expected {ref[i][1][1::]}, got {type(flags[i])})")

            else:  # Pass
                debug(
                    f"Invalid type for flag '{i}' (expected {ref[i][1][1::]}, got {type(flags[i])}); suppressing error for __raiseErr is set to False")
                pass

        elif __raiseErr:  # Raise Error
            debug(
                f"Invalid flag '{i}'; raising error for __raiseErr is set to True")
            raise TypeError(f"Invalid flag '{i}'")

        else:  # Pass
            debug(
                f"Invalid flag '{i}'; suppressing error for __raiseErr is set to False")
            pass

    if __rePlain:
        debug(f"Clearing excessive information from output dictionary.")
        for i in output: output[i] = output[i][0]

    debug(f"Outputting the following flags dictionary: {output}")
    return output


def confirm() -> bool:
    return tkmsb.askyesno(apptitle, f"Do you want to continue with the requested routine?")


def setBootError(time, info, function=None) -> None:
    QAJSONHandlerData = QAJSONHandler.QAFlags()
    if function is None: function = QAJSONHandlerData.FTSRA_fileCheck

    CH = CrashHandler()
    CH.log_crash(
        time=time,
        info=info,
        function=function
    )


# Boot check
ch = CrashHandler()
if not ch.boot_check():
    # Logic
    # Should exit if failed
    tkmsb.showwarning(apptitle, f"The application will close now; please restart the application manually.")
    debug(f"The application will close now; please restart the application manually.")
    Exit('boot_check_fail;;ran_scritps')

# Boot check passed
ui = UI()  # Call the UI
