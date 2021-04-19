stem = "QuizzingApplicationError:"

class FileIO_NoBackup(Exception):
    def __init__(self, Filename: str = "Unknown File", ErrInfo: str = "Unknown Error"):
        self.ErrInfo = ErrInfo
        self.filename = Filename

    def __str__(self):
        global stem
        return f'{stem} Unable to create backup for file {self.filename}; unsafe to continue. Original error: {self.ErrInfo}'

class UnsupportedType(Exception):
    def __init__(self, got: type, *expected):
        self.got = got
        self.expected = expected

    def __str__(self):
        global stem
        return f"{stem} Unsupported Data Type: Expected: {self.expected}; Got: {self.got}"

class RestorationFailed(Exception):
    def __init__(self, FileIOObject: object):
        self.filename = FileIOObject.filename
        self.id = FileIOObject.id

    def __str__(self):
        global stem
        return f"{stem} Failed to restore to (automatic) backup after a failed operation; filename = {self.filename}, objectID = {self.id}"

class ConfigurationError(Exception):
    def __init__(self, info=None):
        self.info = info
    
    def __str__(self):
        global stem
        err = f"{stem} An error occured whilst attempting to handle the configuration settings"
        err += ": {self.info}" if self.info is not None else '.'
        return err

class QA_InvalidFlag(Exception):
    def __init__(self, info=None):
        self.info = info
        
    def __str__(self):
        global stem
        err = f"{stem} QA_InvalidFlag :: An error occured whilst attempting to run application scripts"
        err += f": {self.info}" if type (self.info) is str else '.'
        return err

class QA_SetupException(Exception):
    def __init__(self, info=None):
        self.info = info

    def __str__(self):
        global stem
        err = f"{stem} QA_SetupException :: Fatal: An error occurred during the setup routine"
        err += f": {self.info}" if type(self.info) is str else '.'
        return err

class QAQuizDatabase_UnknownException(Exception):
    def __init__(self, info=None):
        self.info = info

    def __str__(self):
        global stem
        err = f"{stem} QAQuizDatabase_UnknownException :: Fatal: An error occurred whilst decompiling the quiz file"
        err += f": {self.info}" if type(self.info) is str else '.'
        return err

class QACannotDetermineQuestionType(Exception):
    def __init__(self, info=None):
        self.info = info

    def __str__(self):
        global stem
        err = f"{stem} QACannotDetermineQuestionType :: Fatal: Cannot determine question type"
        err += f": {self.info}" if type(self.info) is str else ''
        return err