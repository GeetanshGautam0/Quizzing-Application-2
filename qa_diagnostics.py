import threading, os, sys, shutil
from tkinter import messagebox as tkmsb
import qa_appinfo as QaAI
import qa_logging as log
import qa_globalFlags as QaGF
import qa_theme as Theme
import qa_quizConfig as Configuration

log_ref = log.Log()
log_var_ref = log.Variables()

apptitle = "QA Diagnostics"

theme_GLOBAL_default_comment_header = """
# The "Credit" line will be kept as the first line; if not credit is present, the credit line will default to "Geetansh Gautam, Coding Made Fun"
# Do not put a colon after 'Credit' or else the theme is considered invalid

# Comments can be written with a '#' in the leading a line
# Comments and empty lines will be ignored

# This comment header will remain
# All other comments will be overwritten
"""

class Diagnostics(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        self.start()

        self.data_ref = Data()

    def run_diagnostics(self, key=None) -> bool:
        debug_log(f"run_diagnostics: key = {key}")

        if type(key) is not str: raise TypeError(
            f"Invalid data type for variable 'key'; expected {str}, received {type(key)}")

        if key not in self.data_ref.diagnostics_function_mapping.keys(): raise KeyError(
            f"Inavlid key '{key}' expected one of the following: {self.data_ref.diagnostics_function_mapping.keys()}"
        )

        diag_function = self.data_ref.diagnostics_function_mapping[key]
        debug_log(f"Calling the following function: {diag_function}")

        result = diag_function()

        debug_log(f"Test passed? {result}")

        return result

class Corrections(threading.Thread):
    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        self.start()

        self.data_ref = Data()

    def run_correction(self, key=None) -> None:
        debug_log(f"run_correction: key = {key}")
        if type(key) is not str: raise TypeError(
            f"Invalid data type for variable 'key'; expected {str}, received {type(key)}")

        if key not in self.data_ref.correction_function_mapping.keys(): raise KeyError(
            f"Inavlid key '{key}' expected one of the following: {self.data_ref.correction_function_mapping.keys()}"
        )

        function = self.data_ref.correction_function_mapping[key]
        debug_log(f"Calling the following function: {function}")

        function()

        return None

class Data:
    def __init__(self):
        qaf = QaGF.QAFlags()

        self.FTSRA_appdata_checks = "run_ftsra_file_checks++appdata_loc_only"

        self.correction_function_mapping = {
            qaf.no_func_id: lambda: no_func(None),
            qaf.theme_crash_id: corrections_rst_theme,
            qaf.FTSRA_fileCheck: ftsra_folder_corrections,
            qaf.CONF_corruption_fnc: configuration_file_corrections,
            self.FTSRA_appdata_checks: ftsra_folder_corrections # ftsra_folder_corrections does the thing required; recycle
        }

        self.diagnostics_function_mapping = {
            qaf.no_func_id: lambda: no_func(True), # Pass
            qaf.theme_crash_id: diagnostics_theme,
            qaf.FTSRA_fileCheck: ftsra_folder_diagnostics,
            qaf.CONF_corruption_fnc: configuration_file_diagnostics,
            self.FTSRA_appdata_checks: ftsra_appdata_diagnostics
        }

        self.theme_integ_key = qaf.theme_crash_id
        self.no_func_key = qaf.no_func_id

        self.Default_theme = Theme.default

        # Turn the dict ^ to a string
        # Credit First; as usual

        theme_str = f"Credit {self.Default_theme['Credit']}\n"

        # Add comment header
        theme_str += Theme.default_comment_header.join("\n")

        for i in self.Default_theme:
            if not i == "Credit":
                theme_str += "\n{} {}".format(
                    i, self.Default_theme[i]
                )

        debug_log(f"Loaded the following default theme string: {theme_str}")

        self.FTSRA_defaults = {  # File/Folder Name: Tuple(isDir?, data (files))
            QaAI.scoresFolderName: (True, None),
            QaAI.confFilename: (False, Configuration.default_configuration_str),
            QaAI.readOnlyFilename: (False, "<Unrecoverable Data>"),
            QaAI.qasFilename: (False, ""),
            QaAI.themeFilename: (False, theme_str)
        }

        self.FTSRA_special = { # Files in here will have their data reset
            QaAI.confFilename: Configuration.default_configuration_str,
            QaAI.themeFilename: theme_str
        }

        self.FTSRA_appdata_check_lst = { # Diagnostics function : correction function
            configuration_file_diagnostics: configuration_file_corrections,
            diagnostics_theme: corrections_rst_theme
        }

def ftsra_appdata_diagnostics() -> bool:
    data = Data()
    spc = data.FTSRA_appdata_check_lst
    failed = []

    for i in data.FTSRA_defaults:
        ipath = f"{QaAI.appdataLoc}\\{i}"

        if not os.path.exists(ipath):
            failed.append(ipath)

    for i in spc:
        if not i():
            failed.append(i)
            spc[i]()

    if len(failed) > 0:
        debug(f"Failed the following tests: {failed}")
        return False

    return True

def ftsra_folder_corrections() -> None: # TODO: Do this
    debug_log(f"Correcting FTSRA folder missing files.")
    data = Data()
    specials = data.FTSRA_special

    for i in data.FTSRA_defaults:
        curr_isdir = data.FTSRA_defaults[i][0]
        curr_fileData = data.FTSRA_defaults[i][1]

        # Path
        fpath = f"{QaAI.appdataLoc}\\{i}" # fpath = Final Path
        fname = fpath.split("\\")[-1].strip()
        debug_log(f"Working on {'folder' if curr_isdir else 'file'} '{fpath}'")

        # DIR
        if curr_isdir:

            # Pre-existence
            if os.path.exists(fpath): # If it already exists
                while os.path.exists(fpath): os.rmdir(fpath) # Delete directory
                debug_log(f"Deleted directory {fpath}")

            # New
            os.mkdir(fpath)

        # File
        else:
            if os.path.exists(fpath):
                debug("{} already exists{}".format(fpath, ' and is in special check list; running internal check on data' if fname in specials else ''))

                if fname in specials:
                    debug(f"Writing '{specials[fname]}' to '{fpath}'")
                    open(fpath, 'w').write(specials[fname])

                else:
                    debug(f"File {fpath} not in specials; not running checks.")

            else:
                debug(f"Creating {fpath} with data '{curr_fileData}'")
                while not os.path.exists(fpath): open(fpath, 'w').write(curr_fileData)

    return

def configuration_file_corrections() -> None:
    debug(f"Running conf file corrections script")
    fn = f"{QaAI.appdataLoc}\\{QaAI.confFilename}"
    dfd = Configuration.default_configuration_str

    open(fn, 'w').write(dfd)

def configuration_file_diagnostics() -> bool:
    debug(f"Running conf file diagnostics script")
    data = Data()
    fn = f"{QaAI.appdataLoc}\\{QaAI.confFilename}"; f_raw = QaGF.QAFlags if os.path.exists(fn) else None
    if f_raw is None:
        debug(f"File {fn} doesn't exist; returning False")
        return False

    f_raw = f_raw() # Run class after os check to speed things up in case the file does not exist
    f_raw = f_raw.io(f_raw.GET, re_bool=False, filename=fn, reloadJSON=True, key=None)

    f_keys = f_raw.keys()

    debug(f"Running configuration file diagnostics having loaded the following keys: {f_keys}.")

    for i in Configuration.default_configuration:
        if i not in f_keys:
            debug(f"Required key '{i}' not found in {fn}")
            return False

    return True

def ftsra_folder_diagnostics() -> bool:
    output = True

    debug_log(f"Running FTSRA diagnostics")

    data = Data()

    for i in data.FTSRA_defaults:
        if not os.path.exists(f"{QaAI.ftsFolder}\\{i}"):
            output = False
            debug(f"File {QaAI.ftsFolder}\\{i} does not exist; test failed.")
            break

    if not output:
        tkmsb.showwarning(f"QA Diagnostics", "The application has detected an incomplete install; some files will be reset, however, the installation cannot be patched. Contact Coding Made Fun for further assistance and provide them with the error code.\n\nThe following functions will no longer be available:\n  1) 'Reset All Files'\n  2) 'Copy Missing Files'\n  3) And perhaps 'Reset Configuration File' as well.\n\nError '{}'".format(
            get_code(
                QaAI.codes_keys['incomplete_install']['FTSRA']
            )))

    return output

def debug_log(data: str) -> None:
    global log_ref; global log_var_ref

    try:
        sc_name = __file__.replace("/", "\\").split("\\")[-1].strip().split('.')[0].strip()
    except Exception as e:
        sc_name = sys.argv[0].replace("/", "\\").split("\\")[-1].strip().split('.')[0].strip()

    if not log_var_ref.genDebugFile():
        log_ref.logFile_create(from_=sc_name)

    log_ref.log(data=data, from_=sc_name)

    return None

def debug(a: str) -> None: debug_log(a)

def flags_handler(ref: dict, flags: dict, re_plain: bool = False, __raise_err: bool = True) -> dict:
    debug_log(f"running flags_handler; ref = {ref}, flags = {flags}, re_plain = {re_plain}")

    output = ref

    # ref = {'key': ['set', ('default', <data types>)]

    for i in flags:
        if i in ref:
            if type(flags[i]) in ref[i][1][1::]: # 1 = def tuple, 1:: = data types
                output[i] = [flags[i], ref[i][1]] # reconstruct

            elif __raise_err:
                debug_log(f"Type {type(flags[i])} is invalid for flag '{i}' expected type(s) {ref[i][1][1::]}; raising error")
                raise AttributeError(f"Type {type(i)} is invalid for flag '{i}' expected type(s) {ref[i][1][1::]}")

            else:
                debug_log(f"Type {type(i)} is invalid for flag '{i}' expected type(s) {ref[i][1][1::]} but __raise_err is set to False therefore suppressing error.")

        elif __raise_err:
            debug_log(f"Flag '{i}' is invalid; raising error")
            raise AttributeError(f"Flag '{i}' is invalid")
            
        else:
            debug_log(f"Flag '{i}' is invalid but __raise_err is set to False therefore suppressing error.")

    if re_plain:
        debug_log(f"Clearing excessive data from output dict")
        temp = {}
        for key, val in output.items(): temp[key] = val[0]
        output = temp

    debug_log(f"Returning {output}")

    return output

def load_theme_data(filename: str = '') -> dict:
    debug_log(f"Loading theme from file {filename}")
    # load theme file data
    raw = open(filename, 'r').readlines()
    output = {}
    for i in raw:
        i = i.strip()
        if not i == "":
            if not i[0] == "#":
                key = i.split(' ')[0]
                val = i.replace(key, '', 1).strip()
                output[key] = val

    debug_log(f"Loaded and returning the following theme data: {output}")
    return output

def diagnostics_theme(**flags) -> bool:
    """
    **QA_DIAGNOSTICS.diagnostics_theme**

    :param flags: Flags [dict]
    :return: boolean (valid theme or not)

    ===========

    **Supported Flags**

    1) *filename*:
        * Type: str, bytes
        * Other supported types: *None* (NoneType)
        * Default: <appinfo.appdataloc> + <theme filename> (default file)
        * Information: Filename to load data from; if set to *None*, the dictionary from flag *theme_data* will be used in the validity check

    2) *theme_data*:
        * Type: dict
        * Other supported types: --
        * Default : {} (function will be biased to return *False*)
        * Information: Data to use in validity check (only applied if flag *filename* is set to *None*)

    ===========

    """

    # Flags

    theme_file = f"{QaAI.appdataLoc}\\{QaAI.themeFilename}"

    Flags = {
        'filename': [theme_file, (theme_file, str, bytes, type(None))],
        'theme_data': [{}, ({}, dict)]
    }

    Flags = flags_handler(ref=Flags, flags=flags, re_plain=True)

    debug_log(f"Set flags dict to {Flags}")

    # vars
    theme_file = Flags['filename']

    ints = [
        'fsize_para',
        'sttl_base_fsize',
        'min_fsize',
        'border',
        'btn_fsize'
    ]

    strs = {  # dict key: Tuple(strip? , strip_items, # chars [any for #chars = any amount of characters])
        'bg': (True, ['#', ' ', '\n'], 6),
        'fg': (True, ['#', ' ', '\n'], 6),
        'ac': (True, ['#', ' ', '\n'], 6),
        'hg': (True, ['#', ' ', '\n'], 6)
    }

    other = [
        'font'
    ]

    all = []
    all.extend(ints)
    all.extend(other)
    all.extend(strs.keys())

    theme_data = load_theme_data(Flags['filename']) if Flags['filename'] is not None else Flags['theme_data']

    debug_log(f"Loaded theme {theme_data}")

    # Checks
    # Run tests in order from basic -> advanced

    for i in all: # Check to see if all required (basic presence test)
        if i not in theme_data:
            debug_log(f"Key {i} failed basic presence test; returning False")
            return False # If any test fails

    # Integer checks
    for i in ints:
        try: int(theme_data[i])
        except:
            debug_log(f"Key {i} failed integer test; returning False")
            return False

    # String checks
    for i in strs:
        # dict key: Tuple(strip? , strip_items, # chars)

        _d = theme_data[i]

        if strs[i][0]: # If needed to strip
            debug_log(f"Stripping data before string test")
            for ii in strs[i.strip()][1]:
                while _d.strip()[-1] == ii or _d.strip()[0] == ii:
                    debug_log(f"Stripping '{ii}'")
                    _d = theme_data[i].strip(ii)
        else:
            _d = theme_data[i]

        debug_log(f"Running string test on the following data: {_d}")

        # dict key: Tuple(strip? , strip_items, # chars [any for #chars = any amount of characters])
        if strs[i][-1] is any: continue
        elif not len(_d) == strs[i][-1]:
            debug_log(f"Key {i} failed string test; returning False; expected length {strs[i][-1]}, got {len(_d)}")
            return False

    return True

def conv_to_theme(data: dict) -> str:
    global theme_GLOBAL_default_comment_header
    output = ""

    # Order: Credit >> Comments >> Data

    # Credit
    output += f"Credit {data['Credit']}\n"

    # Comments
    output += theme_GLOBAL_default_comment_header

    output += "\n"

    # Data
    for i in data:
        if "credit" not in i.strip().lower():
            output += f"{i.strip()} {data[i]}\n"
            debug_log(f"Added data {i} {data[i]}")

    debug_log(f"Returning the following data: {output}")
    return output


def corrections_rst_theme(**flags) -> None:
    """
    **QA_DIAGNOSTICS.corrections_rst_theme**

    :param flags: Flags [dict]
    :return: None

    ========

    **Supported Flags**

    1) *writeToFilename*
        * Type: str, bytes
        * Other supported types: --
        * Default: Default theme file
        * Information: Filename to which the new theme will be written to (new theme is the default theme by default)

    2) *readFromFilename*
        * Type: str, bytes
        * Other supported types: *None* (NoneType)
        * Default: QAFTSRA theme file (<appinfo.ftsFolder> + <appinfo.theme_filename>)
        * Information: File to load theme from; if set to *None*, the script will use the dictionary given in *readFrom_data*

    3) *readFrom_data*
        * Type: dict
        * Other supported types: N/A
        * Default: {}
        * Information: Data to read from; if not valid, the data from the default *readFromFile* will be used.

    ========

    """


    global apptitle
    tkmsb.showinfo(apptitle, f"Resetting theme file; this operation will overwrite the existing theme.\n\nPress OK to continue.")
    debug_log(f"Resetting theme file")

    # Default files
    wt_def = f"{QaAI.appdataLoc}\\{QaAI.themeFilename}"
    rf_def = f"{QaAI.ftsFolder}\\{QaAI.themeFilename}"

    # Flags
    Flags = {
        'writeToFilename': [wt_def, (wt_def, str, bytes)],
        'readFromFilename': [rf_def, (rf_def, str, bytes, type(None))],
        'readFrom_data': [{}, ({}, dict)]
    }

    Flags = flags_handler(ref=Flags, flags=flags, re_plain=True)

    debug_log(f"Reset flags to {Flags}")

    # See which system to use (slightly optimized?)
    drf = Flags['readFromFilename']; drd = Flags['readFrom_data']; dwf = Flags['writeToFilename']
    dlrf = load_theme_data(drf) if drf is not None else {}; dlrf_g = load_theme_data(rf_def) if not drf == rf_def else dlrf
    drf_v = diagnostics_theme(filename=None, theme_data=dlrf)
    drd_v = diagnostics_theme(filename=None, theme_data=drd) if Flags['readFromFilename'] is None else False

    dr = dlrf_g if drf == rf_def else (drd if drf is None and drd_v else (dlrf if drf_v else dlrf_g))

    debug_log(f"Using theme data: {dr}")

    dr = conv_to_theme(data=dr)

    # Write the new data
    open(Flags['writeToFilename'], 'wt').write(dr)

def no_func(re=None): return re

def get_code(ID: str) -> any:
    filename = QaAI.cdfn
    if not os.path.exists(filename): return "Unknown Code"
    Flags = QaGF.QAFlags()
    return Flags.io(Flags.GET, key=ID, reloadJSON=True, filename=filename, re_bool=False)
