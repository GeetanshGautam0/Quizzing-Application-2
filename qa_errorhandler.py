from tkinter import messagebox as tkmsb
import sys, threading
import tkinter as tk
import qa_logging as Log

if __name__ == "__main__":
    tkmsb.showerror(f"QA Error", "This module may not be run by itself")
    sys.exit(0)

class vars():
    def __init__(self):
        self.Log = Log.Log()
        self.Log_var = Log.Variables()

def jsr_debug(debug_data):
    try: script_name = __file__.replace('/', '\\').split("\\")[-1].split(".")[0].strip()
    except: script_name = sys.argv[0].replace('/', '\\').split("\\")[-1].split(".")[0].strip()
    V = vars()
    if not V.Log_var.genDebugFile(): V.Log.logFile_create(script_name)
    V.Log.log(debug_data, script_name)

def flag_handler(ref, flags, __raiseError: bool= False):
    # Name conversion
    Flags = ref
    flags = flags

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

def close_app(ecode: str = "0"):
    jsr_debug(f"Calling sys.exit({ecode})")
    sys.exit(ecode)

class Error(threading.Thread): # Run on separate thread
    def __init__(self, err_code: str ='No Diagnostic Information Found', **flags):

        """
        A more advanced error handler that runs on its own separate thread

        :param err_code: Error Code (optional)
        :param flags: flags (dict)

        --------------

        **Supported Flags:**\n

        1. *doNotLog*
            * Type: boolean
            * Default: False
            * Information: If set to true, the function will not log the error to the log file.

        2. *useCustomText*
            * Type: boolean
            * Default: False
            * Information: If set to true, the function will use data from the flag *customText* instead of appending the error code to the base error

        3. *customText*
            * Type: str
            * Default: 'No error data'
            * Information: If *useCustomText* is set to *True*, the string from this flag will be used to display the message.

        4. *exit*
            * Type: bool
            * Default: False
            * Information: Calls sys.exit(*exitCode*) if set to True after showing the error.

        5. *exitCode*
            * Type: str
            * Default: 1
            * Information: Exit code to be used to exit (if *exit* flag is set to True)

        6. *showUI*
            * Type: bool
            * Default: True
            * Information: Show the error information as a UI

        7. *title*
            * Type: str
            * Default: QA Error
            * Information: Title of error UI
        """

        Flags = {
            'doNotLog': [False, (False, bool)],
            'useCustomText': [False, (False, bool)],
            'customText': ['No error data', ('No error data', str)],
            'exit': [False, (False, bool)],
            'exitCode': ['1', ('1', str)],
            'showUI': [True, (True, bool)],
            'title': ['QA Error', ('QA Error', str)]
        }

        self.err_code = err_code
        try:
            self.flags = flag_handler(Flags, flags)
        except:
            sys.exit(1) # Can't proceed

        self.bg = tk.Tk()
        self.bg.withdraw()
        self.bg.title("Qa Error Handler")

        self.thread = threading.Thread
        self.thread.__init__(self)
        try: self.start()
        except:

            close_app('Unable to log error')
        self.bg.mainloop()

    def close_thread(self):
        # jsr_debug(f"Closing Thread")
        # self.bg.after(0, lambda: self.thread.join(self))
        jsr_debug(f"Destroying bg window")
        self.bg.after(0, self.bg.destroy)

    def run(self):

        flags = self.flags # Just to avoid redundant usage of 'self'

        # Step 1: Figure out what text to display
        dt: str = "" # Display Text

        if flags['useCustomText'][0]: dt = flags['customText'] # If custom text is used

        else:
            dt = "An error occured whilst running an application script; "
            if flags['exit']:
                dt += "the error's severity requires the application to be terminated."
            else:
                dt += "the error's severity is not severe enough for termination."

            dt += f"\n\nMore Diagnostic Information: {self.err_code}"

        # Step 2: Log (or skip)
        if not flags['doNotLog'][0]:
            jsr_debug(f"An error was raised; more information: Error: {dt}\n\n{self.err_code}; {self.flags}")

        # Step 3: Show the error (if required)
        if flags['showUI']:
            jsr_debug(f"Showing UI with title '{flags['title']}' and text '{dt}'")
            tkmsb.showerror(flags['title'], dt)

        # Step 4: Close background UI
        self.close_thread()

        # Step 5: Close the app (if required)
        if flags['exit']:
            close_app(flags['exitCode'])