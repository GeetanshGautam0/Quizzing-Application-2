import appdirs, os, sys, shutil, json, traceback
import tkinter.messagebox as msb
import qa_globalFlags as qaFlags
from qa_logging import *
import qa_theme as Theme

if __name__ == "__main__": sys.exit("Cannot run as main file")

# General
global scriptName; k = b'FJf5hmYl7OiaUkOpiU-7xrrGtRaN_11mSRjiG6xf_ps='; global themegetter
qaEnck = b"j2nrg0rAJX_nW9b7TArrThApadsAs5T5WdGn4lprewQ="

scriptName = __file__.replace("/","\\").split("\\")[-1].strip()
themegetter = Theme.Get()

# Logging
global logFilename; global logRef; global variablesRef
logRef = Log()
variablesRef = Variables()
def createLogFile(__from__): logFilename = logRef.logFile_create(__from__)


def close(exCode): sys.exit(exCode)

# Error Handling Method
def errorHandler(errCode="Error Code Unknown", exit=False, exit_code="Exit Code Unknown",showGUIMessage=False):
    if not variablesRef.genDebugFile(): createLogFile(scriptName)
    log_information = f'An error occurred whilst running {scriptName}; more information:\n    Require termination: {exit}\n   Show GUI: {showGUIMessage}\n    Error Code: {errCode}\n    Exit Code:{exit_code}'
    logRef.log(log_information, scriptName)
    if exit: ex_req = "; the application may not continue with said error and therefore will be terminated."
    else: ex_req = "; however, the error is not critical enough to require the termination of the application."
    if showGUIMessage: msb.showerror("Quizzing Application Error", f"An error occurred{ex_req}.\n\nDiagnostic Information:\n\n{errCode}")
    if exit: close(exit_code)

# Version File Variables + Loading + Checking
versionFilename = "qa_versionInfo.json"
VFKeys = {
    'au': 'AuthorName',
    'v': 'Version',
    'pro': 'Product',
    'roam': "Roaming"
}

qa_flags_ref = qaFlags.QAFlags()
try:
    versionData = qa_flags_ref.io(
        qa_flags_ref.GET,
        filename=versionFilename,
        key=None, # Return the entire thing
        reloadJSON=True,
        re_bool=False # Return the stored data
    )
    if not type(versionData) is dict: raise TypeError("Version Data Input was not {}; it was instead {}. INPUT: {}".format(dict, type(versionData), versionData))

except Exception as e:
    errorHandler(traceback.format_exc(), True, e.__class__.__name__, True)

# AppData Variables
appdataLoc = appdirs.user_data_dir(appauthor=versionData[VFKeys['au']],appname=versionData[VFKeys['pro']],version=str(versionData[VFKeys['v']]),roaming=bool(versionData[VFKeys['roam']]))
if not os.path.exists(appdataLoc):
    os.makedirs(appdataLoc)
    logRef.log("Created missing AppData DIRs", scriptName)

def log_isGen(): return [variablesRef.genDebugFile(), variablesRef.logFilename()]

# Filename varaibles
confFilename = "configuration.json"
readOnlyFilename = "disp.qaFile"
qasFilename = "qas.qaFile"
scoresFolderName = "Scores"
themeFilename = "theme.qaFile"

cdfn = 'codes.json'

codes_keys = {
    'incomplete_install': {
        'FTSRA': 'FTSRA_INCOMPLETE_FILES'
    },
    'configuration_file_error' : {
        'conf_file_missing': 'QAADMT_NO_CONFIG_FILE',
        'conf_file_corrupted': 'QAADMT_CANNOT_READ_CONFIG'
    },
    "quick_theme_error": {
        "cannot_determine_path": "QAADMT_CANNOT_DETERMINE_QUICK-THEME_FILENAME"
    }
}

exten = 'qaFile'

# FTSRA Variables
ftsFolder = ".fts"
QaFTSRAFiles = ("configuration.json", "qas.qaFile", "disp.qaFile", "theme.qaFile", "Scores")

# Flags File
global_nv_flags_fn = f"{appdataLoc}\\{qa_flags_ref.flags_fn}"

# Theme Variables
THEME: dict = themegetter.get('theme')
SuiteName: str = "Quizzing Application"
AppNames: dict = {
    'ftsra': "First Time Setup + Recovery Agent\nUtility",
    'quf': 'Quizzing Form',
    'adts': 'Administrator Tools',
    'th': 'Custom Theming Utility'
}
def getAppName(key: str): return AppNames[key] if key in AppNames else None

# Icons
icons_ico = {
    'tu': '.icons\\themer.ico',
    'ftsra': '.icons\\ftsra.ico',
    'admt': '.icons\\admin_tools.ico',
    'qt': '.icons\\quizzing_tool.ico',
    'installer': '.icons\\setup.ico'
}; icons_png = {
    'tu': '.icons\\themer.png',
    'ftsra': '.icons\\ftsra.png',
    'admt': '.icons\\admin_tools.png',
    'qt': '.icons\\quizzing_tool.png'
}

help_files = {
    'ftsra': f".ftsraAid\\fa.pdf"
}
theme_presets_foldername = '.defaultThemes'

export_file_extension = "qa_export"
export_quizFile = 'qaQuiz'
export_score_dbFile = 'qaScore'

fileIO_version_info_header = "<<QA::COMPATABILITY::FILE_VERSION>> :: "

QuestionSeperators = {
    'N': '<<%%QA::0&000001%%>>', # Newline (In question, questions are seperated by \n)
    'S': '<<%%QA::0&000002%%>>', # Space
    'QA': '<<%%QA::0&000003%%>>' # Question Answer
}

QAS_MCCode = "<QAS :: MC_set?True>"
QAS_MC_OPTION_CODE = "[QAS :: Option]"
QAS_TFCode = "<<QAS :: T/F>>"

QA_ENTRY_HELP = ".questionAid\\ADMT_Q-ADD_AID.pdf"

questions_file_info = {
    'enc': True,
    'encoding': 'utf-16'
}

icons_regFile = ".installerRes\\reg_icons.bat"

bugReportLink = "https://codingmadefun.wixsite.com/database/qas-bug-report-form"
version_check_url = "https://raw.githubusercontent.com/GeetanshGautam-CodingMadeFun/cmfvers/master/qas/qas.json"


# ------------------------------ Control Variables ---------------------------

doNotUseSplash = False # If set to True, the splash screen won't be shown
