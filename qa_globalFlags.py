import sys, json, os
import qa_logging as log
import json

Log = log.Log()
log_var = log.Variables()

def debug(__debugData: str):
    global Log; global log_var

    # Script Name

    try:
        sc_name = __file__.replace("/", "\\").split("\\")[-1].split(".")[0].strip()
    except:
        sc_name = sys.argv[0].replace("/", "\\").split("\\")[-1].split(".")[0].strip()

    if not log_var.genDebugFile(): Log.logFile_create(sc_name)

    Log.log(__debugData, sc_name)

# if __name__ == "__main__":
#     sys.exit(0) # Cannot run application by itself

def flag_handler(ref, flags, __raiseError: bool = True):
    # Name conversion
    Flags = ref

    debug(f"flag_handler: ref = {ref}, flags = {flags}, __raiseError = {__raiseError}")

    for i in flags:
        debug(f"i = {i}; flags[i] = {flags[i]}")

        if i in Flags:  # If it is a valid flag
            debug(f"Flag name {i} is valid")

            if type(flags[i]) in Flags[i][1][1::]:  # If it is valid
                debug(f"Flag data valid; resetting from {Flags[i][0]} to {flags[i]}")
                Flags[i][0] = flags[i]

            elif __raiseError:
                debug(f"Flag type invalid; raising error")
                raise IOError(
                    "Type {} unsupported for flag {}; supported types: {}".format(type(flags[i]), i, Flags[i][1][1::]))

        elif __raiseError:
            raise IOError("Flag name {} invalid".format(i))

    return Flags

def load_json(file):
    debug(f"Reading json from file {file}")

    if not os.path.exists(file):
        debug(f"File does not exist; returning empty dictionary.")
        return {}

    with open(file) as JSFile: output = json.load(JSFile)

    debug(f"Returning {output}")
    return output

def save_json(file, data):
    debug(f"Saving json data (see end) to file {file}; data: {data}")

    if not os.path.exists(file):
        debug(f"Generating file because it does not exist.")
        open(file, 'x').close()

    if not type(data) is dict:
        debug(f"Data type {type(data)} is not {dict}")
        raise TypeError(f'Type {type(data)} not supported; expected {dict}.')

    _d = json.dumps(data, indent=4)
    debug(f"Saving the following to file {file}: {_d}")

    open(file, 'w').write(_d)
    debug(f"Written JSON data to file {_d}")

class QAFlags:

    def __init__(self, **flags):
        # Externally and internally accessible variables
        self.SET = 's'
        self.GET = 'g'
        self.REMOVE = 'r'
        self.keys = [self.SET, self.GET, self.REMOVE]  # Supported Keys

        self.flags_fn = f"QA_FLAGS.json"

        self.log_function_id = "crash_function"
        self.log_time_id = "crash_time"
        self.log_info_id = "crash_info"
        self.log_unr_id = "crash_unresolved"; self.def_unr_val = True

        self.theme_crash_timed_id = "QA_APPS_TU_EVENT_LOG from "

        self.theme_crash_id = 'GLOBAL_THEME_ERROR'

        self.no_func_id = 'GLOBAL_NO_FUNCTION'
        self.def_func = self.no_func_id

        self.ftsra_crash_id = "GLOBAL_FTSRA_ERROR"
        self.FTSRA_fileCheck = 'FTSRA_FTSFOLDER_FILECHECK'
        self.FTSRA_timed_log = "QA_APPS_FTSRA_EVENT_LOG from "

        self.CONF_corrupted_err = "GLOBAL_CORRUPTED_CONFIGURATION"
        self.CONF_corruption_fnc = "CONFIGURATION_DATA_INTEGRITY_CHECK"
        
        self.ADMTs_crash_id = "GLOBAL_ADMIN_TOOLS_ERROR"
        self.ADMTs_timed_crash_id = "GLOBAL_ADMIN_TOOLS_EVENT_LOG from "

        self.QT_crash_id = "GLOBAL_QUIZZING_FORM_ERROR"
        self.QT_timed_crash_id = "GLOBAL_QUIZZING_FORM_EVENT_LOG from "

        self.FLAGS_FILE: str = self.flags_fn

        self.json_info = load_json(self.FLAGS_FILE) # Default
        self.loaded_json = self.FLAGS_FILE

    def load_to_mem(self, filename):
        self.json_info = load_json(filename)
        self.loaded_json = filename
        debug(f"Loaded new JSON data (See end) to internal var from file {filename}; data: {self.json_info}")

    def save_set_json(self, current: dict, append: bool, Data: dict):
        debug(f"Ressetting internal variable (self.json_info) to new information before saving...")

        if append:
            debug(f"Appending...")

            self.json_info = current
            debug(f"Set self.json_info to {current}")

            for i in Data:
                if not i.strip() == '':
                    self.json_info[i] = Data[i]
                    debug(f"Added [{i}] = {Data[i]}")

        else:
            debug(f"Not appending new json data (owr all flags)")
            self.json_info = Data
            debug(f"Set JSON data")

        debug(f"Set variable to the following data: {self.json_info}")

    def io(self, Key, **flags):

        """
        **QAFlags.io**

        :param Key: Key (ex: __init__.SET, __init__.GET, etc.)
        :param flags: Flags
        :return: Requested return (bool / json data)

        **Supported Flags:**

        1) *re_bool*
            * Data Type: Boolean
            * Default: True
            * Information: Return a boolean (does the key exist in the given json file?)

        2) *data*
            * Data Type: dict
            * Example: {'key': 'value', 'key1', 'value1'...} Can be as many keys as you  want from 1 to any thing
            * Default: {'': ''}
            * Information: Data to save (key and value; only applies to key=__init__.SET)

        3) *key*
            * Data Type: str, None
            * Default: None
            * Information: Key that is in question (only applies to key=__init__.GET or key=__init__.REMOVE)
            * Note: *None* returns the entire JSON file's data

        4) *filename*
            * Data Type: str
            * Default: __init__.FLAGS_FILE
            * Information: json filename

        5) *reloadJSON*
            * Data type: bool
            * Default: True
            * Information: reload self.json_information variable (load from *filename*)

        6) *appendData*
            * Data Type: bool
            * Default: True
            * Information: Append new flag/owr old flag; do not overwrite the complete file

        """

        Flags = { # Supported Flags
            're_bool': [True, (True, bool)],
            'data': [{'': ''}, ({'': ''}, dict)],
            'key': [None, (None, str, type(None), None)],
            'filename': [self.FLAGS_FILE, (self.FLAGS_FILE, str)],
            'reloadJSON': [True, (True, bool)],
            'appendData': [True, (True, bool)]
        }

        debug(f"Flags before resetting: {Flags}")
        Flags = flag_handler(Flags, flags)
        debug(f"Flags before filtering: {Flags}")

        temp = {}
        for k, v in Flags.items():
            temp[k] = v[0]
        Flags = temp
        debug(f"Set flags to {Flags}")

        def Get(Key: str, re_bool: bool, current: dict):
            debug(f"Calling method 'Get'; args: Key={Key}, re_bool={re_bool}, current={current}")

            if Key is None: return current

            if re_bool:
                return Key in current
            else:
                return current[Key] if Key in current else None

        def Remove(Filename: str, Dict: dict, Pop: str):
            debug(f"Calling method for __init__.REMOVE with Filename = {Filename}; Dict = {Dict}; Pop = {Pop}")

            if not type(Dict) is dict: raise TypeError

            Dict.pop(Pop) if Pop in Dict else Dict
            debug(f"Set _d (__init__.REMOVE) to {Dict}")

            if not type(Dict) is dict: raise TypeError

            save_json(Filename, Dict)

        def Save(Filename: str, Data: dict, append: bool, current: dict):
            debug(f"Calling method 'Save'")

            _d = {}
            if append:
                _d = current
                for i in Data:
                    if not i.strip() == '': _d[i] = Data[i]

            else:
                _d = Data

            debug(f"Method 'Save': Data to save: {_d}")

            save_json(Filename, _d)

        if not Key in self.keys:
            debug(f"Invalid Key; returning None")
            return None

        if Flags['reloadJSON']: self.load_to_mem(Flags['filename']) # Reload if needed

        if Key == self.GET: # __init__.GET
            return Get(Flags['key'], Flags['re_bool'], self.json_info)

        elif Key == self.SET: # __init__.SET
            self.save_set_json(self.json_info, Flags['appendData'], Flags['data'])
            Save(Flags['filename'], self.json_info, False, self.json_info)
            if Flags['reloadJSON']: self.load_to_mem(Flags['filename'])

        elif Key == self.REMOVE: # __init__.REMOVE
            d = self.json_info
            k = Flags['key']

            if not k in d: return None

            Remove(Flags['filename'], self.json_info, Flags['key'])
            if Flags['reloadJSON']: self.load_to_mem(Flags['filename']) # Refresh data
