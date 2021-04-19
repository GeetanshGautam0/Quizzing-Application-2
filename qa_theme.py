# Do not import fileIOHandler for IO

# DO change the integrity check data in qa_diagnostics.py
# if new theme keys are added.

import tkinter.messagebox as messagebox
import tkinter as tk
import appdirs, json, traceback, sys, threading
import qa_logging as llog
import qa_globalFlags as QaFlags
import qa_time as qatime

if __name__ == "__main__": sys.exit(f"Cannot run module standalone") # Module should not be ran by itself

global default; global default_comment_header

# CAUTION: If the header is updated here, it must be updated in qa_diagnostics manually as well.
default_comment_header = """
# The "Credit" line will be kept as the first line; if not credit is present, the credit line will default to "Geetansh Gautam, Coding Made Fun"
# Do not put a colon after 'Credit' or else the theme is considered invalid

# Comments can be written with a '#' in the leading a line
# Comments and empty lines will be ignored

# This comment header will remain
# All other comments will be overwritten
"""

extenstion = 'qaFile'

colorIDs = ['bg', 'fg', 'ac', 'hg', 'border_color']
intIDs = ['fsize_para', 'btn_fsize', 'sttl_fsize', 'min_fsize', 'border']

default = { # If you change something here, define the new behaviour in conv_to_types
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
    'ac': '#008888', # Accent Color
    'hg': '#ffffff', # Highlight color (back of fields)
    'border_color': '#ffffff', # Border color for buttons

    # Misc
    'border': '0' # Border width
}

ui_set = False

# LL functions
def jsr_debug(__D):
    Log = llog.Log()
    Var = llog.Variables()
    sc_name = __file__.replace("/", "\\").split("\\")[-1].split(".")[0].strip()

    if not Var.genDebugFile(): Log.logFile_create(sc_name) # create the log file if it doesn't exist

    Log.log(__D, sc_name)

# Class Declarations

class PlainUI(threading.Thread):

    def __init__(self, title="QA_THEME_DEFAULTS_PlainUI"):
        self.thread = threading.Thread
        self.thread.__init__(self)

        self.vars = {
            'title': title
        }

        self.root = tk.Tk()
        self.ui_run()
        self.update()

        self.start()

        global ui_set
        ui_set = True

        # self.root.mainloop()

    def update(self):
        global ui_set
        self.root.title(self.vars['title'])

    def ui_run(self):
        pass

    def title(self, title: str):
        self.vars['title'] = title
        self.update()

    def withdraw(self):
        self.root.withdraw()

class CrashHandler(threading.Thread):
    def __init__(self):
        self.qaf = QaFlags.QAFlags()

        self.log_name = f"{appdataLoc()}\\{self.qaf.flags_fn}"
        self.log_function_id = self.qaf.log_function_id
        self.def_func = self.qaf.def_func
        self.log_time_id = self.qaf.log_time_id
        self.log_info_id = self.qaf.log_info_id
        self.log_unr_id = self.qaf.log_unr_id
        self.def_unr_val = self.qaf.log_unr_id
        self.id = self.qaf.theme_crash_id # Will be picked up by 'TU'
        self.theme_crash_timed_id = self.qaf.theme_crash_timed_id.strip()

        self.thread = threading.Thread
        self.thread.__init__(self)
        self.start()

    def log_error(self, time, info: any, func_map_name=None) -> None:
        if func_map_name is None: func_map_name = self.qaf.theme_crash_id
        lfn = self.log_name

        setFlag(id=self.id,
                data={
                    self.log_time_id: time,
                    self.log_info_id: info,
                    self.log_function_id: func_map_name,
                    self.log_unr_id: True
                },
                filename=lfn)

        return None

    def log_event(self, time, info: any, event_name: str = None) -> None:
        lfn = self.log_name
        if event_name is None: event_name = self.theme_crash_timed_id
        event_name += f"{time}"

        setFlag(
            id=event_name,
            data=info,
            filename=lfn
        )

        return None

# Pre-function definition logic

background = PlainUI()
background.title("Quizzing Application Loader - Theme Loader")
background.withdraw()

# Function Declarations

def err(code=""):
    jsr_debug(code)
    # messagebox.showerror("Master Theme Handler", code)


def appdataLoc():
    version_fn = "qa_versionInfo.json"
    with open(version_fn) as verFile:
        versionData = json.load(verFile)
    if type(versionData) is not dict: raise IOError("Unable to read the json file '{}'; aborting.".format(version_fn))

    adloc = appdirs.user_data_dir(appauthor=versionData['AuthorName'],
                                  appname=versionData['Product'],
                                  version=str(versionData['Version']),
                                  roaming=bool(versionData['Roaming']))

    return adloc  # appdata location

theme_filename_base = "theme.qaFile"
theme_filename = f"{appdataLoc()}\\{theme_filename_base}"
FTSRA_FOLDER = f"QAFTSRA"
print(theme_filename)

def reset():
    global theme_filename; global FTSRA_FOLDER; global theme_filename_base
    reset_read_from = f"{FTSRA_FOLDER}\\{theme_filename_base}"

    open(theme_filename, 'w').close() # Clear the file
    open(theme_filename, 'wb').write(open(reset_read_from, 'rb').read()) # Reset

def integ(_reload: bool = False, src=None, check_theme_file: bool = True) -> bool:
    global theme_filename
    if check_theme_file: src = theme_filename

    g = Get()

    ints = [
        'fsize_para',
        'sttl_base_fsize',
        'min_fsize',
        'border',
        'btn_fsize'
    ]

    strs = { # tuple (key, strip? , strip_items, # chars
        'bg': (True, ['#', ' ', '\n'], 6),
        'fg': (True, ['#', ' ', '\n'], 6),
        'ac': (True, ['#', ' ', '\n'], 6),
        'hg': (True, ['#', ' ', '\n'], 6),
        'border_color': (True, ['#', ' ', '\n'], 6)
    }

    other = [
        'font'
    ]

    # Step 1: reload theme
    if _reload:
        Get.refresh_theme()

    if src is None:
        theme_check = g.theme_dict

    else:
        try: theme_check = load_theme(file=src, ignore_flags=True)
        except: return False

    for i in strs:
        if not i in theme_check: return False

    for i in ints:
        if not i in theme_check: return False

    for i in other:
        if not i in theme_check: return False

    for i in theme_check:

        if i.strip() in ints:
            try:
                int(theme_check[i])
            except: return False # Invalid entry

        if i.strip() in strs:
            if strs[i.strip()][0]: # strip bool
                for ii in strs[i.strip()][1]: _d = theme_check[i].strip(ii)
            else:
                _d = theme_check[i]

            if strs[i.strip()] is any: pass
            elif not len(_d) == strs[i.strip()][-1]: return False # Last item = length

    return True

def check_theme_integ(loaded: dict, ref: dict):
    if ref is None:
        ref = default
    jsr_debug(f"Loaded dictionary keys: {loaded.keys()}; reference dictionary keys: {ref.keys()}")

    for i in ref.keys():
        if i not in loaded.keys():
            jsr_debug(f"Key '{i}' not found in loaded dictionary.")
            return False
        else:
            jsr_debug(f"Key '{i}' found in loaded dictionary.")
    return True

def conv_to_types(theme: dict) -> dict:
    global default
    if not check_theme_integ(theme, default): return default

    jsr_debug(f"Converting theme {theme}")

    types = {
        'font': str,

        'fsize_para': int,
        'sttl_base_fsize': int,
        'min_fsize': int,

        'bg': str,
        'fg': str,
        'ac': str,
        'hg': str,

        'border': int
    }

    output = theme
    err = False

    for i in types:
        try:
            output[i] = types[i](theme[i])
        except Exception as e:
            jsr_debug(f"Error whilst converting theme: {e}; key = '{i}'; setting to default value ({default[i]})")
            err = True
            output[i] = default[i]

    if err:
        jsr_debug("Theme file was corrupted; some anomalies in the theme may be visible.")
        # messagebox.showerror("Theme Convertor", f'Theme file was corrupted; some anomalies in the theme may be visible.')

    jsr_debug(f"Returning the following, converted theme dictionary: {output}")
    return output

def load_theme(file=None, ignore_flags: bool = False):  # File theme.qaFile will not be encrypted
    global theme_filename; global default
    OUT = default; Pass = False

    if file is None:
        file = theme_filename

    jsr_debug(f"Loading theme from file {file}")

    try:
        # Variables
        raw: str = open(file, 'r').read().strip()  # Raw (str)
        raw_l: list = raw.split("\n")  # Raw (list)
        sep = " "  # Seperator
        loaded = {}
        jsr_debug(f"Loaded {raw}")

        # Handle
        for i in raw_l:
            if len(i.strip()) > 0:
                if not i.strip()[0] == "#":
                    # If it is not a comment
                    key = i.split(sep)[0].strip()
                    val = i.replace(key, "", 1).strip()
                    loaded[key] = val
                    jsr_debug(f"Added {key}: {val}")

        valid = check_theme_integ(loaded, default)  # make sure all keys from default exist in the loaded dict

        print(f"Loaded theme is valid: {valid}")

        # return loaded if valid else default
        if valid:
            OUT = loaded
        else:
            Pass = True
            raise IOError('pass to error handler')

    except Exception as e:
        ch = CrashHandler()
        ch.log_error(time=f'{qatime.now()}', info=f"{traceback.format_exc()}")

        if not Pass:
            err(f"A low-level error occurred whilst loading the theme; using default theme temporarily. Please use the Theming Utility to reset the file.\n\nMore information: {e}")
            jsr_debug(f"An error occurred whilst loading the theme (see end for more info); returning default theme ({default}); more information: {traceback.format_exc()}")
        else:
            err(f"Failed to load theme from file '{file}'; using default theme.")
            jsr_debug(f"Failed to load theme from file '{file}'.")
        OUT = default

        if ignore_flags: raise Exception

    OUT = conv_to_types(OUT)

    jsr_debug(f"Returning the following theme dictionary: '{OUT}'")
    return OUT

def setFlag(id: str, data: any, **flags) -> None:
    ch = CrashHandler()
    Flags = {
        'filename': [ch.log_name, (ch.log_name, str, bytes)],
        'reload_json': [True, (True, bool)], # Highly recommended to NOT change
        'appendData': [True, (True, bool)] # Highly recommended to NOT change
    }

    Flags = flags_modifier(Flags, flags); temp = {}
    for i in Flags: temp[i] = Flags[i][0]
    Flags = temp # Reset flags var to only contain the requested data

    flagsHandler = QaFlags.QAFlags(); key = flagsHandler.SET

    flagsHandler.io(key,
                    filename=Flags['filename'],
                    data={
                        id: data
                    },
                    appendData=Flags['appendData'],
                    reloadJSON=Flags['reload_json'])

    return None

def getFlag(id: str, **flags) -> any:
    ch = CrashHandler()
    Flags = {
        'filename': [ch.log_name, (ch.log_name, str, bytes)],
        'return_boolean': [True, (True, bool)],
        'reload_JSON': [True, (True, bool)] # Highly recommended
    }

    flagsHandler = QaFlags.QAFlags(); key = flagsHandler.GET

    Flags = flags_modifier(Flags, flags); temp = {}
    for i in Flags: temp[i] = Flags[i][0]
    Flags = temp  # Reset flags var to only contain the requested data

    result = flagsHandler.io(key,
                             re_bool=Flags['return_boolean'],
                             key=id,
                             filename=Flags['filename'],
                             reloadJSON=Flags['reload_JSON']
                             )

    return result

def pop_flag(id: str, **flags) -> None:
    ch = CrashHandler()

    Flags = {
        'filename': [ch.log_name, (ch.log_name, str, bytes)],
        'reload_JSON': [True, (True, bool)] # Highly recommended
    }

    Flags = flags_modifier(Flags, flags); temp = {}
    for i in Flags: temp[i] = Flags[i][0]
    Flags = temp  # Reset flags var to only contain the requested data

    flagsHandler = QaFlags.QAFlags(); key = flagsHandler.REMOVE

    flagsHandler.io(key,
                    filename=Flags['filename'],
                    reloadJSON=Flags['reload_JSON'],
                    key=id)

    return None

def flags_modifier(_ref: dict, _flags: dict, __raiseError: bool = True):
    """
    **QA_APPS_TU.FLAGS_MODIFIER**

    :param _ref: reference dictionary of flags (dict); Format: flag name: info; info: list = [current value, defaults]; defaults: tuple = (default value, <accepted data type(s)>)
    :param _flags: flags provided (**kwargs or similar)
    :param __raiseError: raise an error if the flag is not valid (default True)
    :return: altered _ref (dict)

    Custom function to take care of arguments similar to **kwargs
    """

    # Name conversion
    Flags = _ref
    flags = _flags

    # Logging
    jsr_debug('Running function flags_modifier')
    jsr_debug(f"jsr_conv: Flags before flag check: {Flags}; flags given: {flags}")

    for i in flags:
        jsr_debug(f"Checking flag {i}")
        if i in Flags:  # If it is a valid flag
            # Log
            jsr_debug(f"Flag name is valid")
            jsr_debug(f'datatype of flag: {type(flags[i])}; allowed data types: {Flags[i][1:]}')

            if type(flags[i]) in Flags[i][1][1::]:  # If it is valid
                jsr_debug(f"Flag data type is valid; resetting from {Flags[i][0]} to {flags[i]}")
                Flags[i][0] = flags[i]

            elif __raiseError:
                raise IOError(
                    "Type {} unsupported for flag {}; supported types: {}".format(type(flags[i]), i,
                                                                                  Flags[i][1][1::]))

            else:
                jsr_debug(
                    f"Flag datatype {type(flags[i])} invalid; keeping original data ({Flags[i][0]})")  # If the Dt is not valid

        elif __raiseError:
            raise IOError("Flag name {} invalid".format(i))

        else:
            jsr_debug(f"Flag name invalid")  # If the name is not valid

    # Trailing logging
    jsr_debug(f"jsr_conv: Flags after flag check: {Flags}")

    return Flags

class Get():
    def __init__(self):
        # Variable definitions
        self.theme_dict: dict = load_theme()
        print(f"Loaded theme {self.theme_dict}")

        # Variable lookup
        self.refresh_vars()

    def refresh_vars(self):
        jsr_debug(f"Refreshing variables...")
        self.var_lookup = {
            'themedict': self.theme_dict,
            'theme_dict': self.theme_dict,
            'theme': self.theme_dict
        }
        jsr_debug(f"Refreshed all variables in var dict.")

    def refresh_theme(self, __loadFrom__=None):
        self.theme_dict: dict = load_theme(__loadFrom__)
        jsr_debug(f"Reset theme dict to {self.theme_dict}")
        self.refresh_vars()
        return None

    def get(self, key: str):
        key = key.lower()
        re = self.var_lookup[key] if key in self.var_lookup else None
        jsr_debug(f"Returning for key {key}: {re}")
        return re

# Application Logic

# [This is a module; no application logic]
