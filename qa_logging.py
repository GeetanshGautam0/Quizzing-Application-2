import qa_time, appdirs, sys, json, traceback, os
import tkinter.messagebox as msb
import threading

global gen; global __ref__; global logFilename
gen = False
logFilename = ""

def close(exCode): sys.exit(exCode)

scriptName = __file__.replace("/","\\").split("\\")[-1].strip()

def errorHandler(errCode="Error Code Unknown", exit=False, exit_code="Exit Code Unknown",showGUIMessage=False):
    if gen:
        LOGREF = Log()
        log_information = f'An error occurred whilst running {scriptName}; more information:\n    Require termination: {exit}\n   Show GUI: {showGUIMessage}\n    Error Code: {errCode}\n    Exit Code:{exit_code}'
        LOGREF.log(log_information, scriptName)
    if exit: ex_req = "; the application may not continue with said error and therefore will be terminated."
    else: ex_req = "; however, the error is not critical enough to require the termination of the application."
    if showGUIMessage: msb.showerror("Quizzing Application Error", f"An error occurred{ex_req}.\n\nDiagnostic Information:\n\n{errCode}")
    if exit: close(exit_code)


versionFilename = "qa_versionInfo.json"
VFKeys = {'au': 'AuthorName', 'v': 'Version', 'pro': 'Product', 'roam': "Roaming"}

try:
    with open(versionFilename) as verFile:
        versionData = json.load(verFile)
    if not type(versionData) is dict: raise TypeError("Version Data Input was not {}; it was instead {}. INPUT: {}".format(dict, type(versionData), versionData))
except Exception as e:
    errorHandler(traceback.format_exc(), True, e.__class__.__name__, True)

# AppData Variables
global appdataLoc
appdataLoc = appdirs.user_data_dir(appauthor=versionData[VFKeys['au']],appname=versionData[VFKeys['pro']],version=str(versionData[VFKeys['v']]),roaming=bool(versionData[VFKeys['roam']]))
fileInUse = ""

def filter_path(path: str, index: int, *replace):
    for i in replace: path = path.replace(i, "\\")
    return path.strip().split("\\")[index]

class Variables():
    def genDebugFilename(self): # Create a filename and return
        f = [f"{self.folderName()}", f"{qa_time.forLog()}.qaLog"]
        return f

    def genDebugFile(self): return gen # Return gen (bool; is the debug file generated)

    def folderName(self): return f"{appdataLoc}\\Logs"

    def logFilename(self): return logFilename


class Log(threading.Thread):

    def __init__(self):
        self.thread = threading.Thread
        self.thread.__init__(self)
        self.start()

    def logFile_create(self, from_: str = "Unknown origin"):
        global gen; global fileInUse

        if gen: return None

        gen = True
        try:
            if not type(from_) is str: raise TypeError
            else:
                # Filename
                f = __ref__['Variables'].genDebugFilename()
                if not os.path.exists(f[0]):
                    print(f"Making Folder {f[0]}")
                    os.makedirs(f[0])
                f = f"{f[0]}\\{f[1]}"

                try:
                    if not os.path.exists(f): open(f, 'x').close()  # Create the file
                except Exception as e:
                    pass

                fileInUse = f

                print("Generating debug file {}".format(f))
                with open(f,'wt') as file:
                    file.write(__ref__['defaults'].get("def_fileHeader")[-1][-1].format(from_))
                    file.close()

        except Exception as _:
            gen = False  # reset the flag in case the error is suppressed and therefore ignored
            raise _  # Re-raise the error

    def log(self, data, from_="Unknown Origin"):
        global fileInUse

        if not gen:
            self.logFile_create(from_)

        time = qa_time.logTime()

        print(f"{from_} @ {time}: {data}\n")
        with open(fileInUse, 'a') as file:
            file.write(f"{from_} @ {time}: {data}\n")
            file.close()

    def __del__(self):
        self.thread.join(self, 0)

class defaults():
    def get(self, *args):
        self.defs = {
            'def_fileHeader' : "Quizzing Application Suite\n(C) Coding Made Fun, 2020\nLog generated by {}\nWord-Warp is reccommended\n\n\n"
        }
        self.args = args
        if not len(self.args) > 0: return self.ret()
        else: return self.ret_codes()

    def ret(self, code=None): return code

    def ret_codes(self):
        o = []
        for i in self.args:
             if i in self.defs: o.append((i, self.defs[i]))
        return o

__ref__ = {
    "Variables" : Variables(),
    "Log" : Log(),
    "defaults": defaults()
}
