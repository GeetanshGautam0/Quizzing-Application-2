# Quizzing Application Theming Utility
# Beta 0.5 (No Adjustable UI Elements yet)

"""
CODE UNDER PRODUCTION
"""

# Boot time calculation
import qa_time

try: boot_start = qa_time.now() # Added try/except block to remove PEP8 warnings about variables before importing
except Exception: pass

# Generic python modules
import threading, os, sys, traceback, math, shutil, random
import tkinter as tk
import tkinter.messagebox as tkmsb
import tkinter.colorchooser as tkcolor
from tkinter import font as tkfont
from tkinter import filedialog as tkfd
from time import sleep
from tkinter import ttk

# Custom modules
import qa_appinfo as qaai
import qa_theme as Theme
import qa_logging as log
import qa_fileIOHandler as QaF
import qa_fontPicker as QaFPA
import qa_globalFlags as QaFlagHandler
import qa_diagnostics as QaDiagnostics

# Global variables
log_logref = log.Log()
log_varref = log.Variables()
apptitle = f"Theming Utility v{qaai.versionData[qaai.VFKeys['v']]}"
cont = False

global ui

def no_func(re=True) -> any:
    jsr_debug(f"Called placeholder function no_func")
    return re # Placeholder function

def check_theme_integ() -> bool:
    jsr_debug(f"Called function 'check_theme_integ'")
    integ = Theme.integ()
    jsr_debug(f"Theme Integ: {integ}")
    return integ

def reset_theme() -> None:
    jsr_debug(f"Resetting theme file...")

    global apptitle
    tkmsb.showinfo(apptitle, f"Resetting theme file; press OK to continue.")
    Theme.reset()
    jsr_debug(f"Reset theme file...")
    tkmsb.showinfo(apptitle, f"Successfully reset theme file.")

temp = QaFlagHandler.QAFlags()

check_function_mapping = {
    temp.def_func: no_func,
    'no_func': no_func,
    'check_theme_integ': check_theme_integ
}

check_fail_function_mapping = {
    'check_theme_integ': reset_theme,
    'no_func': lambda: no_func(True),
    temp.def_func: lambda: no_func(True)
}

class CrashHandler(threading.Thread):
    def __init__(self):
        centeral_flags_id = QaFlagHandler.QAFlags()

        self.id = centeral_flags_id.theme_crash_id
        self.unresolved_bool_id = centeral_flags_id.log_unr_id
        self.crash_information_id = centeral_flags_id.log_info_id
        self.crash_time_id = centeral_flags_id.log_time_id
        self.func_call_id = centeral_flags_id.log_function_id
        self.no_func_id = centeral_flags_id.def_func
        self.log_script_name = centeral_flags_id.theme_crash_timed_id

        self.thread = threading.Thread
        self.thread.__init__(self)
        self.start()

    def boot_check(self):
        global apptitle; global check_function_mapping; global check_fail_function_mapping

        try:

            if loadFlag(self.id, return_boolean=True): # If the flag exists
                check_b = loadFlag(self.id , return_boolean=False)
                jsr_debug(f"Received check_b={check_b}")

                if check_b[self.unresolved_bool_id]: # If the crash has not been dealt with
                    test = "Unknown"
                    jsr_debug(f"Dealing with crash from time='{check_b[self.crash_time_id]}'")
                    confirm_check = tkmsb.askyesno(apptitle,
                                                   f'An unresolved crash from "{check_b[self.crash_time_id]}" has been detected; would you like to run diagnostics now?\n\nCrash Information: {check_b[self.crash_information_id]}')

                    if not confirm_check:
                        jsr_debug(f"User wishes to not run diagnostics; marking crash as RESOLVED.")
                        n = check_b
                        n[self.unresolved_bool_id] = False
                        setFlag(self.id, n)
                        tkmsb.showinfo(apptitle, f"Marked crash as 'RESOLVED'")

                    else:
                        dmr = False # dmr = do not remove

                        diagnostics = QaDiagnostics.Diagnostics()

                        result = diagnostics.run_diagnostics(key=check_b[self.func_call_id])

                        if result:
                            tkmsb.showinfo(apptitle, f"Passed requested test; removing boot error flag; press 'OK' to continue.")
                            test = True
                            dmr = False # clear flag

                        else:
                            tkmsb.showerror(apptitle, f"Failed requested test; running appropriate correction script; press 'OK' to continue.")
                            test = False
                            corrections = QaDiagnostics.Corrections()
                            try: corrections.run_correction(key=check_b[self.func_call_id])
                            except Exception as e:
                                dmr = True # Do not clear
                                raise Exception.__class__(e)

                        if not dmr:
                            jsr_debug(f"removing boot error flag")
                            removeFlag(self.id)
                            tkmsb.showinfo(apptitle, f"Cleared error flag.")
                            jsr_debug(f"flag removed")

                        else:
                            jsr_debug(f"not removing boot error flag")

                    diag_data = QaDiagnostics.Data()

                    self.log_event(time=qa_time.now(), info={
                        'crash_detected': check_b,
                        'user_ran_diagnostics': confirm_check,
                        'test_passed': test,
                        'appropriate_diagnostics': diag_data.diagnostics_function_mapping[check_b[self.func_call_id]].__name__,
                        'appropriate_failed_test_function': diag_data.correction_function_mapping[check_b[self.func_call_id]].__name__
                    })

            global cont
            cont = True 

        except Exception as e:
            self.log_crash(time=qa_time.now(), info=f"{traceback.format_exc()}")
            tkmsb.showerror(apptitle, f"Unable to check/reset crash log; terminating application.")
            jsr_debug(f"Crash: {e}; {e.__class__.__name__}; {traceback.format_exc()}")
            sys.exit(f"{IOError}")

    def log_event(self, time, info):

        jsr_debug(f"Logging event; time = {time}, info = {info}")
        main_thread_name = self.log_script_name + f"{time}"

        setFlag(main_thread_name, info)

    def log_crash(self, time, info, func_call=None):
        if func_call is None: func_call = self.no_func_id

        jsr_debug(f"Logging the following crash: time = {time}, info = {info}")

        setFlag(self.id, {
            self.unresolved_bool_id: True,
            self.crash_information_id: info,
            self.crash_time_id: f"{time}",
            self.func_call_id: f'{func_call}'} # Function may only be a return type bool function
            )


def setFlag(flag_id: str, flag_data: any, **flags) -> None:
    """
    **QA_APPS_TU.setFlag**

    Custom function to save flags to external JSON file

    :param flag_id: Flag ID (dict key) [str]
    :param flag_data: Flag data (data to be stored/dict value) [any]
    :param flags: Flags (see 'Supported Flags' section for more information)
    :return: None

    ===============

    **Supported Flags**

    1) *append*:
        * Type: boolean
        * Default: True
        * Information: Append new data or change existing flag data and *NOT* clear the entire file before doing so and therefore not removing all other flags...

    2) *flags_filename*:
        * Type: str, bytes
        * Default: qa_appinfo.global_nv_flags_fn
        * Information: Name of file where flags are stored

    3) *reload_nv_flags*:
        * Type: boolean
        * Default: True (*Highly Recommended*)
        * Information: Reload qa_globalFlags' internal JSON data variable and reset it to the new information present in the flags file; highly recommended to set to *True* otherwise the application may not work suitably or may work slower than optimal.

    ==============

    """

    if not type(flag_id) is str: raise TypeError(f"Invalid type {type(flag_id)} passed for arguement 'flag_id'; expected type {str}.")

    Flags = {
        'append': [True, (True, bool)],
        'flags_filename': [qaai.global_nv_flags_fn, (qaai.global_nv_flags_fn, str, bytes)],
        'reload_nv_flags': [True, (True, bool)]
    }

    Flags = flags_modifier(Flags, flags)

    temp: dict = {}
    for i in Flags: temp[i] = Flags[i][0]

    Flags = temp

    flag_io = QaFlagHandler.QAFlags()
    key = flag_io.SET

    flag_io.io(key,
               filename=Flags['flags_filename'],
               data={
                   flag_id: flag_data
               },
               appendData=Flags['append'],
               reloadJSON=Flags['reload_nv_flags'])

    return None

def loadFlag(flag_id: str, **flags):
    """
    **QA_APPS_TU.loadFlag**

    Custom function to retrieve flag data from external JSON file

    :param flag_id: Flag ID (Dict Key) [str]
    :param flags: Flags [str]
    :return: Union (bool, any)

    ==========

    **Supported Flags**

    1) *return_boolean*
        * Type: bool
        * Default: True
        * Information:
            * If set to *True*, the function will return a boolean;
                * True = Flag is present in given file
                * False = Flag is not present in given file

            * If set to *False*, the function will return the value of the flag;
                * If the flag exists, the function returns the value; type *any*
                * If the flag does not exist, the function returns type *NoneType*

    2) *filename*
        * Type: bytes, str
        * Default: qa_appinfo.global_nv_flags_fn
        * File to look for the flags in

    3) *reload_nv_flags*
        * Type: bool
        * Default: True (Highly Recomended; although slower)
        * Information: If set to *True*, the flags handler will reload its internal variables with the latest information present in the requested file.

    ==========

    """

    if not type(flag_id) is str: raise TypeError(f"Invalid type {type(flag_id)} passed for arguement 'flag_id'; expected type {str}.")

    Flags = {
        'return_boolean': [True, (True, bool)],
        'filename': [qaai.global_nv_flags_fn, (qaai.global_nv_flags_fn, str, bytes)],
        'reload_nv_flags': [True, (True, bool)]
    }

    Flags = flags_modifier(Flags, flags)

    temp: dict = {}
    for i in Flags: temp[i] = Flags[i][0]

    Flags = temp

    jsr_debug(f"Set flags to {Flags}")
    jsr_debug(f"Querying for flag {flag_id} in file {Flags['filename']}")

    flagsIO = QaFlagHandler.QAFlags()
    key = flagsIO.GET

    result = flagsIO.io(Key=key,
                        key=flag_id,
                        filename=Flags['filename'],
                        re_bool=Flags['return_boolean'],
                        reloadJSON=Flags['reload_nv_flags'])

    jsr_debug(f"Result of query: '{result}'")

    return result

def removeFlag(flag_id: str, **flags) -> None:
    """
    **QA_APPS_TU.removeFlag**

    Custom function to remove flags (entries) from external JSON file

    :param flag_id: Flag ID (Dict Key) [str]
    :param flags: Flags [dict]
    :return: None

    =========

    **Supported Flags**

    1) *filename*:
        * Type: str, bytes
        * Default: qa_appinfo.global_nv_flags_fn
        * Information: File from which to remove the given entry

    =========

    """

    if not type(flag_id) is str: raise TypeError(
        f"Invalid type {type(flag_id)} passed for argument 'flag_id'; expected type {str}.")

    Flags = {
        'filename': [qaai.global_nv_flags_fn, (qaai.global_nv_flags_fn, str, bytes)]
    }

    Flags = flags_modifier(Flags, flags)

    jsr_debug(f"Removing flag {flag_id} from file {Flags['filename']}")

    flagsIO = QaFlagHandler.QAFlags()
    key = flagsIO.REMOVE

    flagsIO.io(Key=key,
               filename=Flags['filename'][0],
               key=flag_id)

    return None

def jsr_debug(_deb_data: str) -> None:
    """
    **QA_APPS_TU.JSR_DEBUG**

    :param _deb_data: debug data (str)
    :return: None

    Custom function to manipulate custom module qa_logging to log data.
    """

    # Global vars:
    global log_logref;
    global log_varref

    if not type(_deb_data) is str: raise IOError

    try:
        sc = __file__.replace("/", "\\").replace(os.getcwd().strip(), "").strip("\\").strip()
    except:
        sc = sys.argv[0].replace(os.getcwd().strip(), "").strip("\\").strip()

    if not log_varref.genDebugFile(): log_logref.logFile_create(sc)
    log_logref.log(_deb_data, sc)


def boot_time(s, e, **flags):
    """
    **QA_APPS_TU.BOOT_TIME**

    :param s: start (datetime.time)
    :param e: end (datetime.time)
    :param flags: flags (dict)
    :return: datetime.time

    Calculates and logs boot time

    Supported Flags:
        * log: bool = True/False - Log boot time to logs file?
    """

    # flags
    # ..., log: bool = False/True - True will let the function log the boot time.
    Flags = {
        'log' : [True, (True, bool)]
    }

    bt = qa_time.calcDelta(s, e)
    if Flags['log'][0]: jsr_debug(f'boot time: start - {s}, end - {e}, time - {bt}')
    return bt

def closeapp(ui, _code: str="0"):
    ui.rm() # Close UI
    sys.exit(_code)

def error_handler(_e: str = 'No diagnostic information given', _ecode: str = 'Unknown exit code', _exit: bool = False,
                  _showui: bool = True, ui_ref= None, **flags):
    """
    **QA_APPS_TU.ERROR_HANDLER**

    :param _e: Error code / Diagnostic info (str)
    :param _ecode: Exit code (str)
    :param _exit: Exit? (bool)
    :param _showui: Show the UI? (bool)
    :param flags: flags (dict)
    :return: None

    Handles errors, logs to log file, exits (if requested), etc.

    Supported flags:
        * useCustomText (bool): to use all custom text or an altered pre-existing base.
        * customText (str): custom text to use if 'useCustomText' is set to True; default is 'An unknown error occured'
        * doNotLog (bool): do not log error
    """
    try:
        # Flags
        Flags = {
            'useCustomText': [False, (False, bool)],
            'customText': ['An unknown error occurred', ('An unknown error occurred', str)],
            'doNotLog': [False, (False, bool)],
        }

        Flags = flags_modifier(Flags, flags)

        jsr_debug(f"Running error_handler with arguments: {_e, _ecode, _exit, _showui, flags}")

        global apptitle

        # Variables
        e_use = _e
        base_no_e = 'An error occurred whilst running the application scripts; the error, however, was not significant enough to require a termination of the app.\n\nDiagnostic information:\n{}'.format(
            e_use)
        base_e = 'An error occurred whilst running the application scripts; this error is severe and therefore requies the application to be terminated. If data was being saved it will be restored automatically.\n\nDiagnostic information:\n{}'.format(
            e_use)
        base = base_e if _exit else base_no_e

        if not Flags['doNotLog'][0]: jsr_debug(
            f"Error raised: _e: {_e}, _ecode: {_ecode} _exit: {_exit}, _showui: {_showui}, Flags: {Flags}")

        # UI
        if _showui:
            if Flags['useCustomText'][0]:
                tkmsb.showerror(apptitle, Flags['customText'][0])  # Custom message
            else:
                tkmsb.showerror(apptitle, base)  # Edited generic message

        if _exit: closeapp(_ecode)  # Exit if requested

    except Exception as e:
        jsr_debug(f"Unable to show error; more information: {e.__class__.__name__}: {e}: {traceback.format_exc()}")
        ui_ref.root.quit()

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
                    "Type {} unsupported for flag {}; supported types: {}".format(type(flags[i]), i, Flags[i][1][1::]))

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

def jsr_conv(_d, **flags):
    """
    **QA_APPS_TU.JSR_CONV**

    :param _d: raw data
    :param flags: flags (dict)
    :return: tuple/list (bool valid, data type, data)

    Custom function to convert data types (advanced functionality)
    If a data type is unsupported the function will return [None, None, None]; otherwise it will return [True/False, datatype, data]

    Supported flags (Optional):
        * dtypes (tuple): a tuple / list containing the valid data types; example: (str, bytes, list, tuple)
        * convertTo (type): the type to convert the data to (default is str)
        * multi_sep (str): the separator for converting a str or bytes object to a list
        * doNotStrip (bool): do not strip the data (trailing spaces, leading speaces, and newline characters) (defaults = bool)

    Supported data types (input):
        * list
        * tuple
        * str
        * bytes

    Supported data types (output):
        * list
        * str
        * bytes
    """

    # Basic Logging:
    for i in flags: jsr_debug(f"Flag {i}: {flags[i]} (type {type(flags[i])})")

    # Variables
    type_multi = [list, tuple]
    type_single = [str, bytes, int]  # All supported data types

    # Flags
    # Flags dictionary - contains all flags
    Flags = {  # Flag name : [set_to, (default, *supported_data_types)]
        'dtypes': [(str, bytes, list, tuple, int), ((str, bytes, list, tuple, int), tuple, list)],
        'convertTo': [str, (str, type)],
        'multi_sep': ["\n", ("\n", str)],
        'doNotStrip': [False, (False, bool)]
    }

    # Flags dictionary - modify
    Flags = flags_modifier(Flags, flags)

    # Step 1: Get data type
    dtype = type(_d)
    jsr_debug(f"Data type: {dtype}")

    # Step 2: if the data type is the same, return
    if dtype == Flags['convertTo'][0]:
        jsr_debug(f"The data type is the same; returning immediately")
        return [True, dtype, _d]

    # Step 3: If the dtype is not valid or supported
    if not dtype in Flags['dtypes'][0] or (not dtype in type_multi and not dtype in type_single):
        jsr_debug(f"Unable to convert '{_d}' (type {dtype}); returning [False, None, None]")
        return [False, None, None]

    # Step 4: Convert to right category (single / multi)
    # Step 4.1: Find
    if Flags['convertTo'][0] in type_multi:
        to = 'multi'
    elif Flags['convertTo'][0] in type_single:
        to = 'single'
    else:
        jsr_debug("Unable to convert {_d} (type {dtype}) due to an internal error; returning [None, None, None]")
        return [None, None, None]  # Return triple none if unsupported data type

    jsr_debug(f"to (category): {to}")

    # Step 4.2: Convert (or skip)
    if (dtype in type_multi and to == "multi") or (dtype in type_single and to == "single"):
        jsr_debug("Correct category")
        if to == 'single':

            jsr_debug("single => single")

            if dtype is int:
                jsr_debug(f'converting from {int} to {Flags["convertTo"][0]}')

                if Flags['convertTo'][0] is str:
                    jsr_debug(f"int => str conversion; returning {str(_d)}")
                    return [True, str, str(_d)]

                if Flags['convertTo'][0] is bytes:
                    jsr_debug(f"int => bytes conversion; returning {str(_d).encode('utf-8')}")
                    return [True, bytes, str(_d).encode('utf-8')]

            elif dtype is bytes:  # OG data type

                if Flags['convertTo'][0] is str:  # bytes => str
                    jsr_debug(f"bytes => str conversion")
                    if not Flags['doNotStrip'][0]: out = str(_d.decode('utf-8')).strip()
                    else: out = str(_d.decode('utf-8'))
                    return [True, Flags['convertTo'][0], out] if type(out) is Flags['convertTo'][0] else [None, None,
                                                                                                          None]

                else:
                    jsr_debug(f"Cannot convert from type bytes; returning [None, None, None]")
                    return [None, None, None]

            elif dtype is str:  # OG data type

                if Flags['convertTo'][0] is bytes:  # str => bytes
                    jsr_debug(f"str => bytes conversion")
                    if not Flags['doNotStrip'][0]: out = bytes(_d.strip().encode('utf-8'))
                    else: out = bytes(_d.encode('utf-8'))
                    return [True, Flags['convertTo'][0], out] if type(out) is Flags['convertTo'][0] else [None, None,
                                                                                                          None]
                if Flags['convertTo'] is int:
                    jsr_debug(f"str => int converstion")
                    out = ''; allowed = [str(i) for i in range(10)]
                    for i in _d.strip(): out += i if i in allowed else ''
                    return[True, Flags['convertTo'][0], out] if type (out) is Flags['convertTo'] else [None, None, None]

                else:
                    jsr_debug(f"Cannot convert from type str; returning [None, None, None]")
                    return [None, None, None]

            else:
                error_handler(_e="Cannot convert from type {} to {}; data = {}; allowed data types = {}".format(dtype,
                                                                                                                Flags[
                                                                                                                    'convertTo'][
                                                                                                                    0],
                                                                                                                _d,
                                                                                                                Flags[
                                                                                                                    'dtypes'][
                                                                                                                    0]),
                              _ecode="IOError", _exit=True)

        elif to == 'multi':

            jsr_debug(f"Converting type multi => multi")

            if dtype is tuple:  # OG DType

                if Flags['convertTo'][0] is list:  # tuple => list
                    jsr_debug(f"tuple => list")
                    out = list(i for i in _d)
                    jsr_debug(f'output = {out}')
                    return [True, Flags['convertTo'][0], out] if type(out) is Flags['convertTo'][0] else [False, None,
                                                                                                          None]

                else:
                    error_handler(
                        _e="Cannot convert from type {} to {}; data = {}; allowed data types = {}".format(dtype, Flags[
                            'convertTo'][0], _d, Flags['dtypes'][0]), _ecode="IOError", _exit=True)

            if dtype is list:

                if Flags['convertTo'][0] is tuple:  # list => tuple
                    jsr_debug(f"list => tuple")
                    out = tuple(i for i in _d)
                    jsr_debug(f"output = {out}")
                    return [True, Flags['convertTo'][0], out] if type(out) is Flags['convertTo'][0] else [False, None,
                                                                                                          None]

        else:
            error_handler(_ecode="IOError", _exit=True)

    else:  # If conversion is needed

        if to == 'single':  # If to be converted to a single type data type
            jsr_debug(f"Converting from type multi => single")

            output = ""
            if Flags['convertTo'][0] is bytes: output = bytes(output.encode('utf-8'))

            for i in _d:
                if Flags['convertTo'][0] is bytes:
                    if type(i) is str:
                        output += bytes(i.encode('utf-8'))  # Convert str to bytes

                    elif type(i) is bytes:
                        output += i  # If it is already bytes

                    else:
                        raise IOError("Unable to decode type {} for data {}".format(type(i), i))

                elif Flags['convertTo'][0] is str:
                    if type(i) is str:
                        output += i  # if it already a str

                    elif type(i) is bytes:
                        output += str(i.decode('utf-8')).strip()  # If it is type bytes

                    else:
                        raise IOError("Unable to decode type {} for data {}".format(type(i), i))

            jsr_debug(f"Returning [True, {Flags['convertTo'][0]}, {output}]")
            return [True, Flags['convertTo'][0], output]

        elif to == 'multi':  # If to be converted to a multiple type data type; returns a list
            jsr_debug(f"Converting from single => multi")

            # Variables
            output = []
            t = ""

            # Variable setup
            if type(_d) is bytes:
                t = str(_d.decode('utf-8')).strip()
            elif type(_d) is str:
                t = _d.strip()
            else:
                raise IOError("Unable to decode type {} for data {}".format(type(_d), _d))

            # Conversion
            output_str = t.split(Flags['multi_sep'][0])
            jsr_debug(f"Converted data to str, then to list, and now converting back to original data.")

            output = [];
            contTo = type(_d)
            og_dt = type(_d)
            if og_dt not in Flags['dtypes'][0] or (og_dt not in type_single and og_dt not in type_multi):
                output = output_str

            else:  # If can convert

                BR_ERR = False;
                temp = []

                try:
                    for i in output_str:
                        jsr_debug(f"i {output_str.index(i)}/{len(output_str)}")
                        if type(i) is Flags['convertTo'][0]:
                            temp.append(i)
                            jsr_debug(f"Same DT; appended '{i}'")

                        else:
                            jsr_debug(f"Changing data types")

                            if type(i) is str:
                                jsr_debug(f"Converting from str to ...")

                                if contTo is bytes:  # str => bytes
                                    jsr_debug(f"Converting to {bytes}")
                                    temp.append(i.strip().encode('utf-8'))

                                else:  # Unsupported data types
                                    jsr_debug("Cannot convert; raising error flag.")
                                    BR_ERR = True
                                    break

                            elif type(i) is bytes:
                                jsr_debug(f"Converting from bytes to ...")

                                if contTo is str:  # bytes => str
                                    jsr_debug(f"Converting to str")
                                    temp.append(i.decode('utf-8').strip())

                                else:  # Unsupported data types
                                    jsr_debug("Cannot convert; raising error flag.")
                                    BR_ERR = True
                                    break

                            else:  # Unsupported data types
                                jsr_debug("Cannot convert; raising error flag.")
                                BR_ERR = True
                                break

                except Exception as e:
                    jsr_debug(f"An error occurred whilst converting data; more info: {e}: {traceback.format_exc()}")
                    BR_ERR = True

                if BR_ERR:
                    jsr_debug(f"Error flag raised; returning str")
                    output = output_str

                else:
                    jsr_debug(f"Error flag not raised; returning converted list")
                    output = temp

            jsr_debug(f"Returning [True, {type(output)}, {output}]")
            return [True, type(output), output]

        else:
            jsr_debug(f'Returning [None, None, None]')
            return [None, None, None]

    return [False, None, None]  # Edge case

def get_IOMode(data, **flags):
    """
    **QA_APPS_TU.GET_IOMODE**

    :param data: data stream (any)
    :param flags: flags (dict)
    :return: data io info [mode (read write dict [read = 'r', write = 'w']), multi required (bool)] (list/tuple)

    Custom function that returns the appropriate IO mode ('wb', 'rb', 'r', etc)

    Supported data types:
        * str
        * bytes
        * list
        * tuple

    """

    # Function variables
    Flags = {}  # Default flags
    edge = [{'w': 'w', 'r': 'r'}, False]  # Edge case return statement
    Flags = flags_modifier(Flags, flags)  # Set flags
    supp = [bytes, str, list, tuple]  # Supported data types

    # Step 1: Basic check(s)
    dt = type(data)
    if not dt in supp: raise TypeError("Type {} not supported for variable 'data'".format(type(dt)))

    # Step 2: switch case (equivalent)
    if dt is bytes:
        return [{'w': 'wb', 'r': 'rb'}, False]
    elif dt is str:
        return [{'w': 'w', 'r': 'r'}, False]
    elif dt is list or dt is tuple:
        return [{'w': 'w', 'r': 'r'}, True]

    return edge  # Edge case

def secure_save(_f: str, _d, **flags):
    """
    **QA_APPS_TU.SECURE SAVE**

    :param _f: filename to save to (str)
    :param _d: data to save (str / bytes)
    :return: None

    **Supported Flags:**
        1) encrypt: to encrypt file? (bool; default = False)
        2) datatype: data type to convert to (type; default = bytes)
        3) append: append the new data (bool; default = False)
        4) appendSep: seperator for appending; str only; automatically converted to the right dt (str; default = "")

    Creates backup, attempts to save properly, if fails, restores to backup and processes data if required.
    """

    # Flags
    Flags = {
        'encrypt': [False, (False, bool)],
        'datatype': [bytes, (bytes, type)],
        'append': [False, (False, bool)],
        'appendSep': ['', ('', str)]
    }

    Flags = flags_modifier(Flags, flags)

    # Data types
    _d_dts_supp = [str, bytes, list, tuple]
    _d_dts = [str, bytes]
    _d_final = Flags['datatype'][0]

    # Basic checks
    if not os.path.exists(_f): raise IOError("File {} does not exist.".format(_f))
    if not type(_d) in _d_dts_supp: raise TypeError(f'Type {type(_d)} unsupported by function.')

    # Extra data variables
    data = None # No converted data (yet)
    BAK = None  # No backup

    # Create backup
    try:
        BAK = open(_f, 'rb').read()  # Read in bytes to allow maximum compatibility with minimal error inducing factors.
    except Exception as e:  # Unsafe to continue with the saving process.
        try:
            raise IOError(
                f"Cannot create auto-gen backup for file {_f}; it is deemed unsafe to proceed therefore the process will be terminated.")
        except Exception as e:
            error_handler(_e=traceback.format_exc(), _ecode=e.__class__.__name__, _exit=True)

    # Save to file; if something goes wrong, restore to backup and exit
    try:  # Try to save the new data

        # Set the data var

        if Flags['append'][0]:
            # Step 1: convert data to bytes

            try:
                E = None
                data = jsr_conv(_d, convertTo=bytes)

                # Checks
                if not data[0] or data[-1] is None: raise IOError(
                    f"Pass to error handler -- convertor failed to convert the data type for data from file {_f}")

                # Reset data var to the actual data
                data = data[-1]
                jsr_debug(f"Set data variable to {data}")

                # Append-only code: read the data from the file (in bytes; decrypt if required)
                org = load_file(_f, outputDT=bytes)

                # Append
                data = (org + jsr_conv(Flags['appendSep'][0], convertTo=bytes, doNotStrip=True)[-1] + data) if len(jsr_conv(org, convertTo=bytes)[-1]) > 0 else data

            except Exception as e:
                E = f'An error occurred whilst running a conversion script; more information:\n\n{e}\n{traceback.format_exc()}'

            else:
                try:
                    if data is None:
                        jsr_debug(f"Unable to convert data for file {_f}")
                        E = 'Unable to convert the data to the correct type...'
                except Exception as e:
                    error_handler(_e=traceback.format_exc(), _exit=True, _ecode=e.__class__.__name__)

            if not E is None: error_handler(useCustomText=True, customText=E)

        else:
            # Not appending
            # Altered data var + checks
            E = None
            try:
                data = jsr_conv(_d, dtypes=_d_dts, convertTo=_d_final) # [valid, type, data]

                # Checks
                if not data[0] or data[-1] is None: raise IOError(f"Pass to error handler -- convertor failed to convert the data type for data from file {_f}")

                # Reset data var to the actual data
                data = data[-1]

            except Exception as e:
                E = f'An error occurred whilst running a conversion script; more information:\n\n{e}\n{traceback.format_exc()}'
            else:
                try:
                    if data is None:
                        jsr_debug(f"Unable to convert data for file {_f}")
                        E = 'Unable to convert the data to the correct type...'
                except Exception as e:
                    error_handler(_e=traceback.format_exc(), _exit=True, _ecode=e.__class__.__name__)

            if not E is None: error_handler(useCustomText=True, customText=E)

        # Data var set; appending/not appending operation are the same from now on...

        # Step 1: Clear the file
        open(_f, 'w').close()
        jsr_debug(f"Cleared File {_f}")

        # Step 2: Write the new data
        md = get_IOMode(data)
        if md[-1]:
            open(_f, md[0]['w']).writelines(data)
        else:
            open(_f, md[0]['w']).write(data)

        jsr_debug(
            f'Written {data} to {_f}. Mode info: {md}; 0:{md[0]}; 0_w:{md[0]["w"]}; 0_r:{md[0]["r"]}; 1:{md[-1]}')

        # Step 3: Encrypt (If requested) (appending and not appending)
        if Flags['encrypt'][0]:
            jsr_debug(f"Encrypted file {_f}")
            QaF.encrypt(_f)

        return # Return; do not run any extra code; save time

    except Exception as e1:  # Restore to backup
        try:  # Try to restore to backup
            jsr_debug(f"Failed to save new data; attempting to restore backup to file {_f}")

            # Backup
            open(_f, 'wb').write(BAK)

            # If successful
            jsr_debug("Successfully restored data to backup ({}) in file {}".format(BAK, _f))
            jsr_debug(f"Raising error {e1} - {traceback.format_exc()}")
            try:
                raise e1.__class__(f'{e1}; {traceback.format_exc()}')
            except Exception as e1_2:
                error_handler(traceback.format_exc(), _ecode=e1_2.__class__.__name__, _exit=True)

        except Exception as e2:  # Restoration failed
            jsr_debug(f"Failed to restore to backup for file {_f}")
            error_handler(_ecode=e2.__class__.__name__, _exit=True, useCustomText=True,
                          customText=f"Failed to restore to auto-gen backup for file {_f}; the file may no longer be accessible by Quizzing Application.\n\nDiagnostic Information: {traceback.format_exc()}")

def bw_hex_choose(hex_code: str) -> str:
    hex_code = hex_code.replace('#', '').strip().lower()
    jsr_debug(f"Querying whether if #000000 should be used or whether if #ffffff be used given #{hex_code}")

    Int = 0 # <0 = black; >0 = white
    allowed = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    conv: dict = {'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}; threshold = math.floor(conv['f']/2)
    conv_back = {}
    for k, v in conv.items(): conv_back[v] = k

    for i in hex_code:
        if i not in allowed: raise TypeError(f"Hex code #{hex_code} invalid; character {i} is not one of {allowed}")
        try:
            tmp = int(i)
        except Exception as e:
            tmp = conv[i]

        if tmp >= threshold: Int += 1
        else: Int -= 1

    if Int <= 0: # It's dark, return white
        jsr_debug(f"Returning #ffffff")
        return "#ffffff"
    else: # It's light, return black
        jsr_debug(f"Returning #000000")
        return "#000000"

def invert_hex(hex_code: str) -> str: # Warning; inefficient method of doing this; couldn't find a better way
    jsr_debug(f"Inverting #{hex_code}")
    hex_code = hex_code.replace("#", '').strip().lower()
    if not len(hex_code) == 6: raise AttributeError(f"Hex code #{hex_code} is invalid; expected 6 character str")

    allowed: list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    conv: dict = {'a': 10, 'b': 11, 'c': 12, 'd': 13, 'e': 14, 'f': 15}; max=conv['f']
    conv_back = {}
    for k, v in conv.items(): conv_back[v] = k
    final: str = ''

    for i in hex_code:
        if i not in allowed: raise TypeError(f"Hex code #{hex_code} invalid; character {i} is not one of {allowed}")
        try:
            tmp = max-int(i)
        except Exception as e:
            tmp = max-conv[i]

        final += f"{tmp}" if tmp < 10 else conv_back[tmp]

    jsr_debug(f"Inverted hex #{hex_code} to #{final}")

    return final

def load_file(_f, **flags):
    """
    **QA_APPS_TU.LOAD_FILE**

    :param _f: filename (str)
    :param flags: flags (dict)
    :return: file data

    Loads data from a given file.
    Default data type: str

    1) **Supported Flags:**
        * outputDT (type): the data type of output
        * dict_keyVal_sep (str): separator of a key and a value
            - <key> <sep> <val> => {key: val}
            - Example: "ac #000000" => {'ac': '#000000'}
            - Default separator is a space (' ')
            - The separator is automatically converted to the right data type
        * skDec (bool): skip decryption (optional; decrypted or skipped automatically)
        * list_separator (str): list separator
            - <item> <sep> <item>
            - Example: '<item1> <sep> <item2>' => [item1, item2]
            - Default separator is <backslash n>
            - The separator is automatically converted to the right data type

    2) **Supported Output Data Types:**
        * str
        * bytes
        * list
        * dict
    """

    # Variables
    Flags = {
        'outputDT': [str, (str, type)],
        'dict_keyVal_sep': [" ", (" ", str)],
        'skDec': [False, (False, bool)],
        'list_separator': ["\n", ("\n", str)]
    }
    supp = [str, bytes, list, dict]  # Supported data types (output)

    # Modify flags
    Flags = flags_modifier(Flags, flags)

    # Step 0: Basic checks
    if not os.path.exists(_f): raise IOError("File {} does not exist.".format(_f))
    if not Flags['outputDT'][0] in supp: raise IOError(
        "Type {} not supported by function load_file".format(Flags['outputDT'][0]))

    # Step 1: read raw (may need to decrypt)
    raw = None
    try:
        if Flags['skDec']: raise QaF.CRError("Do not decrypt file; passing")
        raw = QaF.decrypt(_f, _owr=False)  # Custom python module qa_fileIOHandler
        jsr_debug(f"Read RAW data from {_f} using qa_fileIOHandler.decrypt()")

    except Exception:
        raw = open(_f, 'rb').read()
        jsr_debug(f"Read RAW data from {_f} using open(_f, 'rb').read()")

    else:
        jsr_debug(f"Successfully read data from file {_f}")

    # Step 2: Convert to the right data type
    if raw is None: raise IOError("Cannot load file {}".format(_f))

    dt = type(raw);
    dt_request = Flags['outputDT'][0]  # Data types

    # Configure flags that need to be adjusted (data types)
    Conf = ['dict_keyVal_sep', 'list_separator']
    for i in Conf:
        __temp1 = Flags[i][0]
        __to = jsr_conv(__temp1, convertTo=dt_request if dt_request is str or dt_request is bytes else str)
        Flags[i][0] = __to  # Change to
        jsr_debug("Changed Flags[{}] from {} to {}".format(__temp1, i, __to))

    if dt is dt_request:
        jsr_debug("dt == dt_request; returning raw ({})".format(raw))
        return raw  # Immediate return statement

    def Str(_d):
        jsr_debug("Running load_file.Str() for data ({})".format(_d))

        if type(_d) is bytes:
            return str(_d.decode('utf-8')).strip()
        elif type(_d) is str:
            return _d.strip()
        else:
            raise IOError("Type {} no supported by load_file.Str()".format(type(_d)))

    def Bytes(_d):
        jsr_debug("Running load_file.Bytes() for data ({})".format(_d))

        if type(_d) is str:
            return _d.strip().encode('utf-8')
        elif type(_d) is bytes:
            return _d
        else:
            raise IOError("Type {} no supported by load_file.Bytes()".format(type(_d)))

    def List(_d, _flags):
        DT = type(_d)
        if DT is str:  # str => list
            return _d.strip().split(_flags['list_separator'][0])

        elif DT is bytes:  # bytes => list
            return Str(_d).split(_flags['list_separator'][0])

        else:
            raise TypeError("Unsupported conversion type {} to {}".format(dt, list))

    # Conversion
    data = ""  # Output Variable

    if dt is bytes and dt_request is str:  # bytes => str
        data = Str(raw)

    elif dt is str and dt_request is bytes:  # str => bytes
        data = Bytes(raw)

    elif dt_request is list:  # Union(str, bytes) => list
        if dt is str:  # str => list
            data = raw.strip().split(Flags['list_separator'][0])

        elif dt is bytes:  # bytes => list
            data = Str(raw).split(Flags['list_separator'][0])

        else:
            raise TypeError("Unsupported conversion type {} to {}".format(dt, list))

    elif dt_request is dict:  # Union(str, bytes) => dict
        out = {}
        if dt is str:  # str => dict
            for i in List(raw, Flags):
                if len(i.strip()) > 0:  # If there is any data in the given entry

                    key = i.split(Flags['dict_keyVal_sep'])[0].strip()  # Get the key
                    val = i.replace(key, "").strip()  # Replace the key from text to get value

                    out[key] = val  # Set the value

            data = out  # Set the data variable

        elif dt is bytes:  # bytes => dict
            for i in List(Str(raw), Flags):
                if len(i.strip()) > 0:  # If there is any data in the given entry

                    key = i.split(Flags['dict_keyVal_sep'])[0].strip()  # Get the key
                    val = i.replace(key, "").strip()  # Replace the key from text to get value

                    out[key] = val  # Set the value

            data = out  # Set the data variable

        else:
            raise TypeError("Unsupported conversion type {} to {}".format(dt, dict))

    return data  # Return the output

def int_ask(theme: dict, curr: str, ttl: str = "Enter an Integer"):

    print(f'abcd {curr}')

    TK = tk.Tk()
    root = tk.Frame(TK)
    root.pack(fill=tk.BOTH, expand=True)
    TK.config(bg=theme['bg'])
    root.config(bg=theme['bg'])
    TK.title("Picker")
    TK.protocol("WM_DELETE_WINDOW", TK.destroy)

    entry = tk.Entry(root,
                     justify=tk.LEFT,
                     fg=theme['fg'],
                     bg=theme['bg'],
                     selectforeground=theme['hg'],
                     selectbackground=theme['ac']
                     )

    lbl = tk.Label(root,
                   text=ttl,
                   bg=theme['bg'],
                   fg=theme['fg'])

    submit = tk.Button(root,
                       text="Submit",
                       bd=theme['border'],
                       fg=theme['fg'],
                       bg=theme['bg'],
                       activeforeground=theme['hg'],
                       activebackground=theme['ac'],
                       command=lambda: root.after(0, TK.destroy)
                       )

    lbl.pack(fill=tk.BOTH, expand=True)
    entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    submit.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    entry.delete(0, tk.END)
    entry.insert(0, f"{curr}")

    root.lift()

    root.update()

    ws = [root.winfo_width(), root.winfo_height()]
    ws = [
        ws[0] * 2 if ws[0] * 2 <= root.winfo_screenwidth() else ws[0],
        # ws[1] * 2 if ws[1] * 2 <= root.winfo_screenheight() else ws[1]
        ws[1] # Don't change height
    ] # Reuse ws to prevent the "winfo" function running too many times.

    TK.geometry(f"{ws[0]}x{ws[1]}")

    root.mainloop()

    def filter(string: str) -> int:
        allowed = []
        out: str = ''
        for i in range(10): allowed.append(str(i))
        for i in string: out += i if i in allowed else ''
        return int(out)

    raw = entry.get()

    TK.withdraw()

    return filter(raw)

# UI Definition

class UI(threading.Thread):

    def __init__(self, title="Quizzing Application Theming Utility", master=None):
        # Initialization
        self.t = threading.Thread
        self.t.__init__(self)

        # Run crash check
        ch = CrashHandler()
        ch.boot_check()

        # Variable initialization
        self.title = jsr_conv(title, convertTo=str)[-1] if jsr_conv(title, convertTo=str)[
            0] else "Quizzing Application Theming Utility"

        # Main window
        self.root = tk.Tk(); self.root.withdraw()

        # Set window transform information
        self.txy = {'x': 0, 'y': 1}  # Coordinate template
        self.ss = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())  # Screen size
        self.ds = (700, 750)  # Default size
        self.ds_ratio = (
            700/1920, # Width
            750/1080 # Height
        )
        self.ws = [
            self.ds[self.txy['x']] if self.ds[self.txy['x']] < self.ss[self.txy['x']] else int(self.ss[self.txy['x']]*self.ds_ratio[0]),
            self.ds[self.txy['y']] if self.ds[self.txy['y']] < self.ss[self.txy['y']] else int(self.ss[self.txy['y']]*self.ds_ratio[1])
        ]  # Window size (adjustable)
        self.sp = (int(self.ss[self.txy['x']] / 2 - self.ws[self.txy['x']] / 2),
                   int(self.ss[self.txy['y']] / 2 - self.ws[self.txy['y']] / 2))  # Position on screen

        # Padding x and y
        self.padX = 20; self.padY = 20

        # Label frame ratios (after deducting padding)
        self.lbl_fr_r = {
            'change': 0.75, # Change group gets 75%
        }; self.lbl_fr_r['preview'] = 1-self.lbl_fr_r['change'] # Calculate the preview group's width %%

        # UI Variables
        self.titleLbl = tk.Label(self.root, text="Theming Utility") # Main Header Text
        self.change_btnGrp = tk.LabelFrame(self.root, text="Change Theme") # Altering Group Label Frame
        self.save_refresh_btn = tk.Button(self.root, text="Refresh") # Submit and Refresh Button
        self.io_btn_grp = tk.LabelFrame(self.root, text="IO")
        self.io_import = tk.Button(self.io_btn_grp, text="Import Theme")
        self.io_export = tk.Button(self.io_btn_grp, text="Export Theme")
        self.restore_btn = tk.Button(self.root, text="Restore to Default")

        # UI - Theme setting variables
        # self.theme_set_canv_frame = tk.Canvas(self.change_btnGrp)
        # self.theme_set_canv = tk.Frame(self.theme_set_canv_frame)
        # self.theme_set_canv_scbar = ttk.Scrollbar(self.theme_set_canv_frame)

        self.theme_set_canvas_new = tk.Canvas(self.change_btnGrp, borderwidth=0)
        self.theme_set_frame_new = tk.Frame(self.theme_set_canvas_new)
        self.theme_set_vsb = tk.Scrollbar(self.change_btnGrp, orient=tk.VERTICAL)

        # LB Frames - the containers need to have their own instances
        self.bg_lbf = tk.LabelFrame(self.theme_set_frame_new)
        self.fg_lbf = tk.LabelFrame(self.theme_set_frame_new)
        self.ac_lbf = tk.LabelFrame(self.theme_set_frame_new)
        self.hg_lbf = tk.LabelFrame(self.theme_set_frame_new)
        self.font_lbf = tk.LabelFrame(self.theme_set_frame_new)
        self.fsize_para_lbf = tk.LabelFrame(self.theme_set_frame_new)
        self.min_fsize_lbf = tk.LabelFrame(self.theme_set_frame_new)
        self.btn_fsize_lbf = tk.LabelFrame(self.theme_set_frame_new)
        self.border_lbf = tk.LabelFrame(self.theme_set_frame_new)

        # Buttons need to have their own instance
        self.bg_change_btn = tk.Button(self.bg_lbf)
        self.fg_change_btn = tk.Button(self.fg_lbf)
        self.ac_change_btn = tk.Button(self.ac_lbf)
        self.hg_change_btn = tk.Button(self.hg_lbf)
        self.font_change_btn = tk.Button(self.font_lbf)
        self.fsize_para_change_btn = tk.Button(self.fsize_para_lbf)
        self.min_fsize_change_btn = tk.Button(self.min_fsize_lbf)
        self.btn_fsize_change_btn = tk.Button(self.btn_fsize_lbf)
        self.border_change_btn = tk.Button(self.border_lbf)

       	self.font_face_preview = tk.Label(self.font_lbf)

        self.theme_set_loop_vars = {  # Title: [Info, command, Theme dict ID]
            'Background Color': ['Background color of all application windows', lambda: self.change('bg'), 'bg'],
            'Foreground Color': ['The color of all text throughout all applications', lambda: self.change('fg'), 'fg'],
            'Accent Color': ['The accent color can be seen as the background of a pressed button',lambda: self.change('ac'), 'ac'],
            'Highlight Color': ['The highlight color can be seen as the foreground of a pressed button',lambda: self.change('hg'), 'hg'],
            'Font Face': ['The font face used throughout all applications',lambda: self.change('font'), 'font'],
            'Font Size (P)': ['The font size used in paragraphs and regular text throughout all applications',
                              lambda: self.change('fsize_para'),'fsize_para'],
            'Font Size (Min)': ['The smallest font size possible in any application (paragraphs excluded)',
                                lambda: self.change('min_fsize'),'min_fsize'],
            'Font Size (Btn)': ['The font size used for (most) buttons throughout the application', lambda: self.change('btn_fsize'),'btn_fsize'],
            'Button Border Size': ['The size of the line surrounding buttons', lambda: self.change('border'),'border']
        }

        # Mapper
        self.tsblkm: tuple = ( # Instance of the keys above ^, btn ref, lbf ref
            ('Background Color', self.bg_change_btn, self.bg_lbf),
            ('Foreground Color', self.fg_change_btn, self.fg_lbf),
            ('Accent Color', self.ac_change_btn, self.ac_lbf),
            ('Highlight Color', self.hg_change_btn, self.hg_lbf),
            ('Font Face', self.font_change_btn, self.font_lbf),
            ('Font Size (P)', self.fsize_para_change_btn, self.fsize_para_lbf),
            ('Font Size (Min)', self.min_fsize_change_btn, self.min_fsize_lbf),
            ('Font Size (Btn)', self.btn_fsize_change_btn, self.btn_fsize_lbf),
            ('Button Border Size', self.border_change_btn, self.border_lbf)
        )


        self.btns_change_set_commands = []

        self.adj_btns: list = []

        # Theme (loaded)
        th = Theme.Get()
        self.theme = th.get("themedict")

        # Update variables
        self.theme_lbl = []
        self.theme_btn = []
        self.previews = {}

        # Last things in self.__init__
        self.start()

        # Calculate the boot time
        global boot_start
        boot_e = qa_time.now() # Boot end time (UI initialized yet not drawn...
        boot_time(boot_start, boot_e) # Calculate the boot time

        # Show the UI
        self.root.mainloop()  # Run the UI

    def _on_mousewheel(self, event):
        """
        Straight out of stackoverflow
        Article: https://stackoverflow.com/questions/17355902/tkinter-binding-mousewheel-to-scrollbar
        Change: added "int" around the first arg
        """
        self.theme_set_canvas_new.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def rm(self): self.root.after(0, self.root.destroy)

    def get_theme(self): return self.theme

    def update_ui(self):
        jsr_debug(f"UI.update_ui: Updating the theme with the following theme: {self.theme}.")
        jsr_debug(f"Labels (or similar) to update_ui: {self.theme_lbl}; button-like: {self.theme_btn} and previews {self.previews}")

        # Update root
        self.root.config(background=self.theme['bg'])

        # Change GRP
        self.theme_set_canvas_new.config(background=self.theme['bg'])
        self.theme_set_frame_new.config(background=self.theme['bg'])
        
        self.root.iconbitmap(
            qaai.icons_ico.get('tu')
        )

        jsr_debug(f"UI.update_ui: Updated root theme")

        # Theme the labels
        for i in self.theme_lbl:
            try:
                jsr_debug(f"UI.update_ui: Setting theme for label {i}: {i.cget('text')}")
                i.config(bg=self.theme['bg'], fg=self.theme['fg'])
            except Exception as e:
                error_handler(useCustomText=True,
                              customText=f"Unable to set theme as there was an error in the theme file; please restore the theme file by pressing the button in the bottom right-hand corner;\n\nMore diagnostic information: {e.__class__.__name__}: {e}: {traceback.format_exc()}", ui_ref=self)

        # Theme the buttons
        for i in self.theme_btn:
            try:
                jsr_debug(f"UI.update_ui: Setting theme for button {i}: {i.cget('text')}")
                i.config(bg=self.theme['bg'],
                         fg=self.theme['fg'],
                         activebackground=self.theme['ac'],
                         activeforeground=self.theme['hg'],
                         highlightbackground=self.theme['border_color'],
                         highlightcolor=self.theme['border_color'],
                         highlightthickness=self.theme['border'],
                         bd=self.theme['border'])

            except Exception as e:
                # error_handler(useCustomText=True,
                #               customText=f"Unable to set theme as there was an error in the theme file; please restore the theme file by pressing the button in the bottom right-hand corner;\n\nMore diagnostic information: {e.__class__.__name__}: {e}: {traceback.format_exc()}", ui_ref=self)
                try: self.dsb_btns()
                except: pass

                jsr_debug(f"Crash report: cannot set element theme for {i}; more information: {e}; {traceback.format_exc()}")

                ch = CrashHandler()
                data = QaDiagnostics.Data()
                ch.log_crash(time=qa_time.now(), info=f"{traceback.format_exc()}", func_call=data.theme_integ_key)

                sleep(0.5)
                self.root.quit()
                self.t.join(self)

        self.restore_btn.config( # Invert Color to ensure that it can be seen
            bg=self.theme['bg'],
            # fg=f"#{invert_hex(self.theme['bg'])}"
            fg=bw_hex_choose(self.theme['bg'])
        )

        self.font_face_preview.config(text=f"{self.theme['bg']}")

        # Title LBL Font Face
        self.titleLbl.config(font=(
        	self.theme['font'],
        	int(self.titleLbl.cget('font').split(' ')[-1])
        ))

        # Previews
        for i in self.previews:
            d = self.previews[i]
            tmp_preview = i.config(
                                    text=self.theme[d],
                                    bd=0,
                                    highlightbackground=f'#{invert_hex(self.theme[d])}',
                                    background=self.theme[d],
                                    activebackground=self.theme[d],
                                    foreground=bw_hex_choose(self.theme[d]),
                                    activeforeground=bw_hex_choose(self.theme[d])
            )
            jsr_debug(f"Set theme for preview {i} with dict key {d}")

    def dsb_btns(self):
        for i in self.theme_btn:
            i.config(state=tk.DISABLED)

    def enb_btns(self):
        for i in self.theme_btn:
            i.config(state=tk.NORMAL)

    def run(self):
        # Event Handlers (temporary)
        def eventHandler(event):
            jsr_debug(f"Resized to {event.width}x{event.height}")

        # root_handler.root.bind('<Configure>', eventHandler) # Remove when not debugging events to prevent delay

        # Root variables
        gem = f"{self.ws[self.txy['x']]}x{self.ws[self.txy['y']]}+{self.sp[self.txy['x']]}+{self.sp[self.txy['y']]}"
        ttl = self.title; ico = qaai.icons_ico['tu']

        # Root setup
        self.root.title(ttl)  # Set title
        self.root.geometry(gem)  # Set transformation
        self.root.iconbitmap(ico) # Set icon
        self.root.protocol("WM_DELETE_WINDOW", lambda: closeapp(self))

        jsr_debug(f"Using title {ttl}")  # Debug (title)
        jsr_debug(f"Using geometry {gem}")  # Debug (size)
        jsr_debug(f"Setting icon to '{ico}'") # Debug (icon)
        # Element Placement + configuration

        # Label frame c and p width calculation
        w = int(self.ws[
                    0] - 3 * self.padX)  # window size - 3* padx (<pad before c frame> + <pad between c and p frames> + <pad after p frame>)
        c_w = int(w * self.lbl_fr_r['change']); p_w = int(w * self.lbl_fr_r['preview'])

        jsr_debug(f"""c_w + p_w values: 
        cw = {c_w}, 
        pw = {p_w}, 
        total = {c_w + p_w}, 
        expected {w} 
        (cw:pw expected = {self.lbl_fr_r['change']}:{self.lbl_fr_r['preview']}; 
        cw:pw actual = {c_w/(c_w+p_w)}:{1-(c_w/(c_w+p_w))})""")

        # Title Label
        self.titleLbl.pack(fill=tk.BOTH, expand=True)
        tfs = math.floor(self.ws[self.txy['x']]/len(self.titleLbl.cget('text'))) # Calculate the font size
        jsr_debug(f"Using font face {self.theme['font']} and size {tfs} for title")
        self.titleLbl.config(font=(self.theme['font'], tfs)) # Set font attributes
        self.theme_lbl.append(self.titleLbl)
        self.theme_lbl.append(self.change_btnGrp)

        # Change Theme - Label Frame
        # Canvas
        self.change_btnGrp.pack(fill=tk.BOTH, expand=1, padx=(self.padX, int(self.padX/2)), pady=self.padY, side=tk.LEFT)

        # Change Container + Frame + SCBar
        # self.theme_set_canvas_new = tk.Canvas
        # self.theme_set_frame_new = tk.Frame
        # self.theme_set_vsb = tk.Scrollbar

        self.theme_set_vsb.configure(command=self.theme_set_canvas_new.yview)
        self.theme_set_canvas_new.configure(
            yscrollcommand=self.theme_set_vsb.set,
            width=int(c_w-0.1*c_w)
        )

        self.theme_set_vsb.pack(fill=tk.Y, side=tk.RIGHT, expand=False)
        self.theme_set_canvas_new.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.theme_set_canvas_new.create_window(
            (0,0),
            window=self.theme_set_frame_new,
            anchor="nw",
            tags="self.theme_set_frame_new"
        )

        self.theme_set_frame_new.config(width=self.theme_set_canvas_new.cget('width'))

        jsr_debug(f"""
self.theme_set_frame_new.width = {self.theme_set_frame_new.cget('width')}
self.theme_set_canvas_new.width = {self.theme_set_canvas_new.cget('width')}
""")

        # IO
        self.io_btn_grp.pack(fill=tk.BOTH, expand=1, padx=self.padX, pady=(self.padY, int(self.padY / 2)))
        self.theme_lbl.append(self.io_btn_grp)

        self.io_import.pack(fill=tk.BOTH, expand=1, padx=int(self.padX/2), pady=(10, 5))
        self.io_export.pack(fill=tk.BOTH, expand=1, padx=int(self.padX/2), pady=(10, 5))

        self.theme_btn.append(self.io_import)
        self.theme_btn.append(self.io_export)

        self.io_import.config(command=self.io_import_func)
        self.io_export.config(command=self.io_export_func)

        # Submit + refresh Button
        self.save_refresh_btn.pack(fill=tk.BOTH, expand=1, padx=self.padX, pady=int(self.padY / 2))
        self.theme_btn.append(self.save_refresh_btn)

        # self.save_refresh_btn.config(command=self.save)
        self.save_refresh_btn.config(command=self.reload) # Button only used to refresh now.

        # Restore Button
        self.restore_btn.pack(fill=tk.BOTH, expand=1, padx=self.padX, pady=(int(self.padY / 2), self.padY))
        self.theme_btn.append(self.restore_btn)

        self.restore_btn.config(command=self.restore)

        # Set the widths
        self.change_btnGrp.config(width=c_w)
        self.save_refresh_btn.config(width=p_w)

        # Canvas Objects
        curr_ind: int = 0
        max_ind: int = len(self.theme_set_loop_vars)-1
        info_vars = self.theme_set_loop_vars

        def configute_chng_grp(info, key, root_handler, btn_inst, lbf_inst):

            py: tuple = (int(root_handler.padY / 2), int(root_handler.padY / 2)) if 0 < curr_ind < max_ind else ((root_handler.padY, int(root_handler.padY / 2)) if curr_ind == 0 else (int(root_handler.padY / 2), root_handler.padY))

            lbf_inst.config(text=key, width=int(
                #self.theme_set_frame_new.cget('width') - root_handler.padX
                root_handler.theme_set_frame_new.cget('width')
            ))
            lbf_inst.pack(fill=tk.BOTH, expand=True, padx=root_handler.padX, pady=py)

            jsr_debug(f"Set width for {lbf_inst} ({lbf_inst.cget('text')}) to (expected: {root_handler.theme_set_frame_new.cget('width')}, actual: {lbf_inst.cget('width')})")

            temp_lbl = tk.Label(lbf_inst, text=info.get(key)[0], anchor=tk.W)
            temp_lbl.pack(fill=tk.BOTH, expand=True)

            btn_inst.config(text=f'Set {key}', command=info.get(key)[-2])
            btn_inst.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

            jsr_debug(f"Set command for button {btn_inst} to {info.get(key)[-2]}")

            if info.get(key)[-1] in Theme.colorIDs:
                tmp_preview = tk.Button(lbf_inst,
                                        text=root_handler.theme[info[key][-1]].strip('{').strip('}')
                                        )
                tmp_preview.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT)
                root_handler.previews[tmp_preview] = info[key][-1]

            else:
                if key == 'font':
                    root_handler.font_face_preview.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=(0, int(root_handler.padX / 2)))

                else:
                    temp_lbl_2 = tk.Label(lbf_inst,
                                          text='Set to: {}'.format(root_handler.theme.get(info[key][-1]))
                                          )
                    temp_lbl_2.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=(0, int(root_handler.padX / 2)))
                    root_handler.theme_lbl.append(temp_lbl_2)

            root_handler.theme_lbl.append(lbf_inst)
            root_handler.theme_lbl.append(temp_lbl)
            root_handler.theme_btn.append(btn_inst)

        # Change BTN Grps
        for i in self.tsblkm:
            configute_chng_grp(info_vars,  # Information Dictionary
                               i[0],  # Key (info_vars key)
                               self,  # Root Instance
                               i[1],  # Button Instance
                               i[-1]  # LBF Instance
                               )

        # Set the widths
        self.change_btnGrp.config(width=c_w)
        self.save_refresh_btn.config(width=p_w)

        # Event Handler Binds
        self.theme_set_frame_new.update() # Update the Frame object
        self.theme_set_frame_new.bind("<Configure>", self.onFrameConfig)
        self.theme_set_canvas_new.bind_all("<MouseWheel>", self._on_mousewheel)

        # Final code in UI.run
        jsr_debug("UI.run: set root_handler.theme_lbl to {} and root_handler.theme.btn to {}.".format(self.theme_lbl, self.theme_btn))

        # Update the theme of the elements
        self.root.deiconify()
        self.update_ui()

    def reload(self):
        Theme.Get().refresh_theme()
        self.theme = Theme.Get().get('theme')
        self.update_ui()

    def onFrameConfig(self, event): # for scbar
        self.theme_set_canvas_new.configure(
            scrollregion=self.theme_set_canvas_new.bbox("all")
        )

    # Button Functions

    def change(self, theme_key: str): # Master handler of all changes
        jsr_debug(f"Running change command for key {theme_key}")
        new = None

        if theme_key in Theme.colorIDs:
            new = tkcolor.askcolor(color=self.theme.get(theme_key))[-1]
            jsr_debug(f"New color for id {theme_key}: {new}")

        elif theme_key == 'font':
            new = QaFPA.FontDialog()['font']
            jsr_debug(f"New font: {new}")

        elif theme_key in Theme.intIDs:
            id = theme_key
            for i in self.theme_set_loop_vars:
                if self.theme_set_loop_vars[i][-1] == theme_key:
                    id = i
                    break

            new = int_ask(self.theme, self.theme[theme_key], f"Set {id}")
            jsr_debug(f"New int for theme id {id}: {new}")

        if new is None: return
        if new == self.theme[theme_key]: return
        else: # Save time
            self.theme[theme_key] = new
            self.save()

    def io_import_func(self):
        jsr_debug(f"Attempting to import theme")

        # Step 1: get the file
        filename = tkfd.askopenfilename(filetypes=[("Quizzing Application Theme File", Theme.extenstion)])
        jsr_debug(f"Selected file: {filename}")

        if filename.strip() == "":
            error_handler(useCustomText=True, customText='No file selected; aborting.')
            jsr_debug("Cancelled importing operation")
            return # If no file is selected

        # Step 2: Load data
        theme = {}

        try:
            # Variables
            raw: str = open(filename, 'r').read().strip()  # Raw (str)
            raw_l: list = raw.split("\n")  # Raw (list)
            sep = " "  # Separator
            loaded = {}

            # Handle
            for i in raw_l:
                if len(i.strip()) > 0:
                    if not i.strip()[0] == "#":
                        # If it is not a comment
                        key = i.split(sep)[0].strip()
                        val = i.replace(key, "", 1).strip()
                        loaded[key] = val

            valid = Theme.check_theme_integ(loaded, Theme.default)  # make sure all keys from default exist in the loaded dict

            if not valid: raise IOError('Failed to validate file "{}"'.format(filename))
            else: theme = loaded

        except Exception as e:
            error_handler(useCustomText=True,
                          customText=f"Cannot load theme data from file '{filename}'; aborting import process.\n\nDiagnostic information: {traceback.format_exc()}")

            return None

        jsr_debug(f"Theme file valid")

        # Step 2.5 (ish): Confirm
        global apptitle
        if not tkmsb.askyesno(apptitle, f"Are you sure you want to overwrite your theme data; this cation cannot be undone."):
            jsr_debug(f"User aborted theme import")
            return

        jsr_debug(f"User confirmed theme import; continuing")

        # Step 3: Set data (copy)
        if not os.path.exists(Theme.theme_filename): # If the theme file does not exist...
            jsr_debug(f"Theme file does not exist; copying...")
            shutil.copyfile(filename, Theme.theme_filename) # Create and copy data

        else:
            jsr_debug(f"Theme file exists; overwriting data...")
            open(Theme.theme_filename, 'wb').write(open(filename, 'rb').read()) # Overwrite data as it is valid

        # Update
        th = Theme.Get()
        th.refresh_theme()
        self.theme = th.get('theme')
        self.update_ui()

        jsr_debug(f"Refreshed UI theme")
        tkmsb.showinfo(apptitle, "Successfully imported and refreshed theme.")

    def io_export_func(self):
        jsr_debug(f"Exporting theme")
        global apptitle

        export_filename_suggestion = f"{random.randint(000000, 9999999)}.{Theme.extenstion}"
        jsr_debug(f"Suggested filename: {export_filename_suggestion}")

        allowed_file_types = [
            ('Quizzing Application Theme File', f'*.{Theme.extenstion}')
        ]

        filename = tkfd.asksaveasfilename(filetypes=allowed_file_types, defaultextension=allowed_file_types, initialfile=export_filename_suggestion)

        # If aborted / canceled
        if filename is None or filename.strip() == "":
            error_handler(useCustomText=True, customText="Canceled export operation.")
            jsr_debug("Cancelled exporting operation")

        jsr_debug(f"Exporting theme data to '{filename}'")

        # Copy the file
        try: # Try
            shutil.copyfile(Theme.theme_filename, filename)

        except Exception as e: # Failed
            jsr_debug(f"Cannot export file; more info: {e.__class__.__name__}: {e}: {traceback.format_exc()}")
            error_handler(_e=traceback.format_exc())

        else: # Success
            jsr_debug(f"Exported theme file to '{filename}'")
            tkmsb.showinfo(apptitle, f'Successfully exported theme to file "{filename}"')

    def restore(self):
        jsr_debug(f"UI.restore (reset theme to default)")
        # Load OG Theme to in memory variable
        # Step 1: load the new data in qa_theme's memory
        og_theme = "{}\\{}\\{}".format(os.getcwd().replace('/','\\'), qaai.ftsFolder, qaai.themeFilename)
        jsr_debug(f"Reading theme from file: '{og_theme}'")
        # Theme.load_theme(file=og_theme)
        # Step 2: refresh qa_theme's internal dictionary
        g = Theme.Get()
        g.refresh_theme(__loadFrom__=og_theme)
        # Step 3: load new theme to this app's theme variable
        self.theme: dict = g.get('theme')
        jsr_debug(f"Restore routine: reset theme to {self.theme}")

        # Then call the save function that will overwrite and update_ui the UI
        # Step 4: Call self.save
        self.save() # Reads from self.theme, overwrites and refreshes UI

    def save(self):
        jsr_debug(f"Saving theme")

        self.save_theme() # Save the theme
        self.update_ui() # Update the theme

    def save_theme(self):
        """
        :return: None

        Please save new theme to theme dictionary before calling this function.
        The appropriate dictionary is UI.theme (retrieved by UI.get_theme())
        """

        # Load Variables
        theme = self.get_theme()
        theme_file = Theme.theme_filename

        jsr_debug(f"Saving the following theme: {theme}")

        # Step 1: Checks
        if not Theme.check_theme_integ(theme, Theme.default):  # Check if the theme is valid
            error_handler(useCustomText=True, customText=f"Failed to save theme to file {theme_file}")

        if not os.path.exists(theme_file):
            error_handler(useCustomText=True,
                          customText=f"Failed to save theme to file {theme_file} as the theme file does not exist.")

        # Step 2: Construct the data
        # Credit >> Comments >> Data

        out = "" # Output

        # Credit
        out = f"Credit {jsr_conv(self.theme['Credit'], convertTo=str)[-1]}"
        jsr_debug(f"Set output data to '{out}'")

        # Comments
        out += f"\n{jsr_conv(Theme.default_comment_header, convertTo=str)[-1]}"
        jsr_debug(f"Set output data to '{out}'")

        # Data
        for i in self.theme:
            if not i.lower() == "credit":
                jsr_debug(f"Adding data for key {i}")
                out += f"\n{jsr_conv(i, convertTo=str)[-1]} {jsr_conv(self.theme[i], convertTo=str)[-1]}"
                jsr_debug(f"Set output data to '{out}'")

        # Step 3: Save data
        secure_save(theme_file, out)

if not os.path.exists(Theme.theme_filename): # If theme file does not exist.
    jsr_debug(f"No theme file found; aborting.")
    error_handler(_exit=True,
                  _ecode = "No Theme File Found",
                  useCustomText=True,
                  customText=f"Unable to launch application as the theme file does not exist; please run the FTSRA utility.\n\nExpected location: {Theme.theme_filename}.")
#
# tkmsb.showinfo(
#             apptitle,
#             f"Note that only the title is affected by changes in font in this utility."
#         )

ui = UI(apptitle)
