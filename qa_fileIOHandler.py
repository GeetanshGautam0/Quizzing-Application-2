"""
Custom Module for FileIO for Quizzing Application
Object Oriented Code
FileIO V4
"""

from cryptography.fernet import Fernet
import qa_appinfo as qaai
import qa_logging as llog
import sys, os, traceback, cryptography, random
import tkinter.messagebox as msb
import qa_typeConvertor as QATypeConv
import qa_errors as QAErrors

import matplotlib.pyplot as plt
import numpy as np

import datetime as dt

# Global Variables
global log;
global log_var
log = llog.Log();
log_var = llog.Variables();
key = qaai.k
CRError = cryptography.fernet.InvalidToken
IDs = []  # Object IDs


# if __name__ == "__main__": sys.exit('cannot run module standalone') # TODO: REMOVE THE COMMENT

class GlobalData:
    stripSeqs = ['\ufeff']
    bytes_encodings = [
        'utf-8',
        'utf-16',
        'utf-32',
        'ascii',
        'utf-7',
        'iso-2022-jp-ext',
        'cp936'
    ]
    banned_encodings = [
        'utf-16le',
        'utf-16be'
    ]


class ENC:
    def __init__(self, Object: object):
        self.key = Object.encKey

        self.object = Object
        self.fer = Fernet(self.key)
        self.fio = FILEIO(self.object)

        self.encoding = 'utf-8'

    def change_key(self, new_key):
        try:
            fer = Fernet(new_key)
            self.fer = fer
            debug(f"ENC.change_key <<1>> - Successfully changed key for object.")

        except Exception as e:
            debug(f"ENC.change_key <<1>> - Failed to set new key for object.")
            raise e.__class__(e)

    def encrypt(self):
        # Create a backup and store it
        BAK = self.fio.load_file()

        # Step 0: Pre Enryption
        self.__preEnc(BAK)
        __2 = self.fio.load_file()
        open(self.object.filename, 'w').close()

        # Step 1: Create FileIO (load_file/secure_save/read_file) instance
        __bytes = BYTES_OPS()
        debug(f"ENC.encrypt <<1.1>> for ID <<{self.object.id}>> - Created bytes operations instance <<{__bytes}>>")

        # Step 2: Load the raw data (Moved Up)
        __raw = __2  # Set from the new BAK var
        debug(
            f"ENC.encrypt <<2.1>> for ID <<{self.object.id}>> - Loaded raw bytes information <<{__raw}>> from file <<{self.object.filename}>>")

        # Step 3: Set encoding
        __data = __bytes.reencode(__raw, self.encoding).strip()
        debug(f"ENC.encrypt <<3.1>> for ID <<{self.object.id}>> - Re-encoded bytes to <<{__data}>>")

        # Step 4: Encrypt
        __enc = self.__enc(__data).strip()
        debug(f"ENC.encrypt <<4.1>> for ID <<{self.object.id}>> - Encrypted data to bytes <<{__enc}>>")

        # Step 5: Save
        self.fio.secure_save(__enc)
        debug(f"ENC.encrypt <<5.1>> for ID <<{self.object.id}>> - Ran <<FILEIO.secure_save>>")

        # Step 6: Validate
        __val = VALIDATORS(self.object).val_enc(__data, self)
        if not __val:
            open(self.object.filename, 'wb').write(BAK)  # Restore to backup

            debug(
                f"ENC.encrypt <<6.1>> for ID <<{self.object.id}>> - Failed Encryption Validation; raising error <<Restored to BAK>>")
            raise IOError(
                f"Unable to validate the encryption for file id <<{self.object.id}>> Actions taken: <<Restore to BAK>>")
        else:
            debug(f"ENC.encrypt <<6.1>> for ID <<{self.object.id}>> - Passed Encryption Validation")

    def decrypt(self) -> bytes:
        # Step 1: Load raw
        __raw = self.fio.load_file()
        debug(f"ENC.decrypt <<1.1>> for ID <<{self.object.id}>> - Loaded raw data <<{__raw}>>")

        # Step 2: Decrypt
        __dec = self.fer.decrypt(__raw)
        debug(f"ENC.decrypt <<2.1>> for ID <<{self.object.id}>> - Decrypted data <<{__dec}>>")

        return __dec

    def __preEnc(self, __raw) -> None:
        # Step 1: Load raw
        # __raw = self.fio.load_file() # Passed as an argument now
        debug(f"ENC.__preEnc <<1.1>> for ID <<{self.object.id}>> - Loaded raw data <<{__raw}>>")

        # Step 2: Reencode to utf-8
        __enco = __raw.decode(
            BYTES_OPS().get_bytes_encoding(__raw)
        ).encode('utf-8').strip()

        debug(f"ENC.__preEnc <<2.1>> for ID <<{self.object.id}>> - Encoded raw data <<{__enco}>>")

        # Step 3: Convert to list
        __data: list = QATypeConv.convert(__enco, str, returnDataOnly=True).split("\n")
        for i in __data:
            __data[__data.index(i)] = i.encode('utf-8')

        debug(f"ENC.__preEnc <<3.1>> for ID <<{self.object.id}>> - Converted encoded data to list <<{__data}>>")

        # Step 4: Create the final data
        __final = []
        debug(f"ENC.__preEnc <<4.1>> for ID <<{self.object.id}>> - Decrypting/Appending Data <<{__final}>>")

        for i in __data:
            debug(f"ENC.__preEnc <<4.2>> for ID <<{self.object.id}>> - Decrypting/Appending Data <<{i}>>")
            try:
                temp1 = self.__dec(i)
                temp1 = post_decrypt_cleaner(temp1).encode('utf-8')
                __final.append(temp1)
            except:
                __final.append(i.strip())

        pops = []

        for i in range(len(__final)):
            if __final[i].strip() == b"": pops.append(i)

        # Reverse "pops" so that it doesn't cause issues with the varying list size
        pops = pops[::-1]

        for i in pops:
            debug(f"ENC_preEnc <<4.3>> for ID <<{self.object.id}>> - Popping index {i}/{len(__final)} ({__final[i]})")
            __final.pop(i)

        debug(f"ENC.__preEnc <<4.4>> for ID <<{self.object.id}>> - Loaded pre-save data <<{__final}>>")

        # Step 5: Convert to the right encoding and owr file with __final
        __save = ''.encode(self.encoding)
        for i in __final:
            # __save += "\n".encode(self.encoding) if len(__final) > 1 else ''.encode(self.encoding)+ \
            #           BYTES_OPS().reencode(i, self.encoding)

            sep = "\n".encode(self.encoding) if len(__final) > 1 else ''.encode(self.encoding)
            data = BYTES_OPS().reencode(i, self.encoding)

            __save += sep
            __save += data

            __save = __save.strip()

            print(f"4.4.2 :: {sep} {data} {__save}")

        debug(f"ENC.__preEnc <<5.1>> for ID <<{self.object.id}>> - Created to save data <<{__save}>>")

        # Step 6: Write the data
        self.fio.quick_save(__save)
        debug(f"ENC.__preEnc <<6.1>> for ID <<{self.object.id}>> - Saved data with quick_save <<{__save}>>")

    def __enc(self, _data) -> bytes:
        return self.fer.encrypt(_data)  # Simple

    def __dec(self, _data) -> bytes:
        return self.fer.decrypt(_data).strip()  # Simple, again


class FILEIO:
    def __init__(self, Object: object):
        self.object = Object

    def secure_save(self, __data, **kwargs) -> None:
        flags = {
            'append': [False, (bool,)],
            'append_seperator': ['\n', (str, bytes)],
            'encoding': ['utf-8', (str,)]
        };
        flags = flags_handler(flags, kwargs)

        # Step 0: IO Integ checks
        if not VALIDATORS(self.object).IO_integrity('-securesave'): raise IOError(
            f"Unable to validate the file before saving new data.")

        # Step 1: Create a backup
        try:
            BAK = open(self.object.filename, 'rb').read()

        except Exception as E:
            raise QAErrors.FileIO_NoBackup(self.object.filename, E)  # Custom error in qa_errors

        # Step 2: Data handling
        # <<2.1>> Variables
        __raw = BAK  # Utilize the already read information; save time by not calling open() again
        __dt = type(__data)  # Store data type
        __encoding = flags['encoding'][0];
        __append = flags['append'][0];
        __appendSep = flags['append_seperator'][0]

        __appendSep = BYTES_OPS().reencode(__appendSep, 'utf-8').decode('utf-8')

        singles = [str, bytes]
        multiples = [list, tuple]

        toWrite: bytes = b""

        # <<2.2>> Logic
        def lst_to_str(lst, sep) -> str:
            out: str = ""
            for i in lst:
                out += QATypeConv.convert(i, str, list_str_bytes_entrySep=sep)[-1]

        if __append:
            debug(f"Secure Save: __append = True")

            # any >> bytes
            if __dt in multiples:
                # Multi >> bytes
                __data = list(__data)
                __str = lst_to_str(__data, "\n")

                __newBytes = __str.encode(__encoding)

                debug(f"Secure Save: Converted {__data} to {__newBytes}")

            elif __dt in singles:
                # Single >> bytes
                __newBytes = BYTES_OPS().reencode(__data, __encoding)

                debug(f"Secure Save: Converted {__data} to {__newBytes}")

            else:
                raise QAErrors.UnsupportedType(__dt, *singles, *multiples)

            toWrite = BYTES_OPS().reencode(__raw, __encoding) + __appendSep.encode(__encoding) + __newBytes

        elif __dt in singles:
            debug(f"Secure Save; __append = False; Single >> bytes conversion")
            # Single (any) >>> Bytes
            if __dt is str:  # Convert
                toWrite = __data.encode(__encoding)

            elif __dt is bytes:  # Re-encode
                toWrite = BYTES_OPS().reencode(__data, __encoding)

        elif __dt in multiples:
            debug(f"Secure Save: __append = True; Multi >> bytes conversion")
            # Multi >> bytes
            __data = list(__data)
            __str = lst_to_str(__data, "\n")

            toWrite = __str.encode(__encoding)

        else:
            raise QAErrors.UnsupportedType(__dt, *singles, *multiples)

        # Step 3: Write the data
        debug(f"Secure Save: Going to write {toWrite}")

        try:
            # <<3.1>> Clear
            open(self.object.filename, 'w').close()

            # <<3.2>> Write
            open(self.object.filename, 'wb').write(toWrite)

        except Exception as E:  # <<3.Exceptions.1>>
            try:
                open(self.object.filename, 'wb').write(BAK)
                debug(
                    f"FILEIO.secure_save for ID <<{self.object.id}>> - Failed to save information (see end); restored to backup - Inforamtion attempted to store: {toWrite}; BAK = {BAK}")

            except Exception as E2:  # <<3.Exceptions.2>>
                debug(
                    f"FILEIO.secure_save for ID <<{self.object.id}>> - Failed to save data (see end) and backup (see end) -- data = {toWrite}, BAK = {BAK}")
                raise QAErrors.RestorationFailed

    def quick_save(self, __data) -> None:
        open(self.object.filename, 'wb').write(__data)

    def load_file(self) -> bytes:
        _raw = open(self.object.filename, 'rb').read().strip()

        debug(
            f"FILEIO.load_file <<1>> - Loaded raw bytes [see end] for file with FIO-ID::{self.object.id} >> data = {_raw}")

        return _raw

    def read_file(self) -> str:
        try:
            _raw = ENC(self.object).decrypt()
        except:
            _raw = self.load_file()

        debug(
            f"FILEIO.read_file <<1>> - Loaded raw bytes [see end] for file with FIO-ID::{self.object.id} >> data = {_raw}")

        Str: str = post_decrypt_cleaner(_raw)

        debug(
            f"FILEIO.read_file <<2>> - Loaded string [see end] for file with FIO-ID::{self.object.id} >> data = {Str}")

        return Str


class VALIDATORS:
    def __init__(self, Object: object) -> None:
        self.object = Object

    def IO_integrity(self, *args) -> bool:  # For *easy* expansion
        """
        :param args: specifier (optional)
        :return: boolean

        **Valid Specifiers**

        1) *-securesave*:
            * For FILEIO.secure_save()

        """

        # Global checks

        # Specific checks
        if "-securesave" in args:

            if not os.path.exists(self.object.filename):
                open(self.object.filename, 'w').close()  # Create the file

        return True

    def val_enc(self, refference: bytes, instance: object) -> bool:
        debug(f"Verifying encryption for object {self.object.id}")

        # Load the current data (easy)
        __curr = instance.fio.read_file()

        # Convert refference data
        __og = refference
        __og = __og.decode(
            BYTES_OPS().get_bytes_encoding(__og, instance.encoding)
        )

        # Get to state for comparison
        compare_c = __curr.lower().strip()
        compare_o = __og.lower().strip()

        for i in GlobalData.stripSeqs:
            compare_o = compare_o.replace(i, '');
            compare_c = compare_c.replace(i, '')

        debug(f"Verifying encryption for object {self.object.id} :: Comparing (c::o) {compare_c} to {compare_o}")

        # Compare
        if not compare_c == compare_o: return False
        return True


class BYTES_OPS:
    def __init__(self):
        self.possible_encodings = GlobalData.bytes_encodings

    def reencode(self, Data: bytes, encoding: str) -> bytes:
        _str = Data.decode(self.get_bytes_encoding(Data)) if type(Data) is bytes else Data if type(
            Data) is str else None

        _bytes = _str.encode(encoding)

        return _bytes

    def str_housekeeping(self, data: str) -> str:
        out: str = data

        for i in GlobalData.stripSeqs: out = out.replace(i, '')

        return out

    def get_bytes_encoding(self, Data: bytes, expected: str = 'utf-8') -> str:
        encoding_found: str = ''

        try:
            Data.decode(expected)
            encoding_found = expected

        except:
            for i in self.possible_encodings:
                try:
                    Data.decode(i)
                    encoding_found = i
                except:
                    pass

        if encoding_found.strip() == '' or encoding_found is None: raise UnicodeError(
            f"Unable to find encoding for bytes [[see end]]; searched through: {self.possible_encodings} >>> bytes = {Data}")

        if encoding_found in GlobalData.banned_encodings: raise Exception(f"Unsupported encoding '{encoding_found}'")

        return encoding_found


class InstanceGenerator:
    def __init__(self, filename: str, key: bytes = qaai.k):
        global IDs

        self.filename = filename
        mult = random.randint(1, 9) * (10 ** 20)  # Some random int * a large number
        self.id = int(random.random() * mult)  # Even more random to make a unique id
        self.encKey = key

        debug(f"Typical key: {qaai.k}; using {self.encKey}")

        while self.id in IDs: self.id = int(random.random() * mult)

        IDs.append(self.id)  # TO keep track of debugging

        self.get()  # Load the information

    def get(self, k=None):
        info = {
            'object': self,
            'id': self.id,
            None: None
        }

        return info[k.lower().strip() if type(k) is str else None]


# Internal Methods

def post_decrypt_cleaner(__raw: bytes) -> str:
    _a = BYTES_OPS()

    # To str
    Str = __raw.decode(
        _a.get_bytes_encoding(__raw)
    )

    # Clean
    Str = _a.str_housekeeping(Str)

    return Str


def flags_handler(__ref: dict, __kwargs: dict) -> dict:
    out: dict = __ref

    for i in __kwargs:
        if i in out:

            if type(__kwargs[i]) in __ref[i][-1] or any in __ref[i][-1]:

                out[i] = [
                    __kwargs[i],
                    __ref[i][-1]
                ]

            else:
                raise TypeError(f"Invalid type {type(i)} for flag '{i}' expected {__ref[i][-1]}")

        else:
            raise NameError(f"Invalid flag name '{i}'")

    return out


def debug(debugData: str) -> None:
    global log;
    global log_var

    try:
        sc_name = __file__.replace("/", "\\").split("\\")[-1].split('.')[0].strip()
    except:
        sc_name = sys.argv[0].replace("/", "\\").split("\\")[-1].split('.')[0].strip()

    if not log_var.genDebugFile(): log.logFile_create(from_=sc_name)

    try:

        log.log(data=debugData, from_=sc_name)

    except Exception as e:
        try:
            log.log(data=f"Failed to log data <<{e}>>", from_=sc_name)
        except:
            log.log(data='ERRx2 :: Failed to log data', from_=sc_name)


# Callers

def encrypt(Object: object, **kwargs) -> None:
    debug(f"Enorypting file (Obj ID = {Object.id})")
    flags = {

    };
    flags = flags_handler(flags, kwargs)

    __inst = ENC(Object)
    __inst.encrypt()


def decrypt(Object: object, **kwargs) -> bytes:
    flags = {

    };
    flags = flags_handler(flags, kwargs)

    debug(f"Decrypting data from file (Obj ID = {Object.id})")

    __inst = ENC(Object)
    _res = __inst.decrypt()

    debug(f"Decrypted data from file (Obj ID = {Object.id}); result = {_res}")

    return _res


def save(Object: object, data: any, **kwargs):
    debug(f"Saving data (see end) to file (Obj ID = {Object.id}); Data = {data}")

    flags = {
        'encryptData': [False, (bool,)],
        'append': [False, (bool,)],
        'appendSeperator': ['\n', (str, bytes)],
        'encoding': ['utf-8', (str,)]
    };
    flags = flags_handler(flags, kwargs)

    # Save
    __FIOinst = FILEIO(Object)
    _as = QATypeConv.convert(flags['appendSeperator'][0], str, returnDataOnly=True)

    __FIOinst.secure_save(data,
                          append=flags['append'][0],
                          append_seperator=flags['appendSeperator'][0],
                          encoding=flags['encoding'][0]
                          )

    # Encrypt (Optional)    
    if flags['encryptData'][0]:
        __ENCinst = ENC(Object)
        __ENCinst.encrypt()


def load(Object: object, **kwargs) -> bytes:
    debug(f'Loading data from file (Obj ID = {Object.id})')

    flags = {

    };
    flags = flags_handler(flags, kwargs)

    __inst = FILEIO(Object)
    __res = __inst.load_file()

    debug(f'Loaded data (see end) from file (Obj ID = {Object.id}); result = {__res}')

    return __res


def read(Object: object, **kwargs) -> str:
    debug(f"Reading data from file (Obj ID = {Object.id})")

    flags = {

    };
    flags = flags_handler(flags, kwargs)

    __inst = FILEIO(Object)
    __res = __inst.read_file()

    debug(f"Read data (see end) from file (Obj ID = {Object.id}); data = {__res}")

    return __res


def create_fileIO_object(filename: str) -> object:
    """
    ** WARNING: Creating an object with this function will NOT allow you to change the ENC KEY; **
    ** Use InstanceGenerator to use custom key **

    :param filename: filename
    :return: fileIOHandler object
    """

    __object = InstanceGenerator(filename)
    debug(f"Created IO object {__object} (ID {__object.get('id')})")
    return __object


def test_timing(path, data: str = "Hello, World!", enco=None, tms=None):
    open(path, 'w').close()

    a = create_fileIO_object(path)
    b = FILEIO(a)

    b.secure_save(data)

    e = ENC(a)
    if enco is None:
        encoding = input(f"Enter the encoding format (%%exit%% to exit) >> ")
    else:
        encoding = enco
    e.encoding = encoding

    if encoding == "%%exit%%": return -1

    x = [];
    y = [];
    lens = [];
    rawLens = [];
    y2 = [];
    dec = []

    if tms is None:
        times = int(input("Please enter the number of encryptions to test >> "))
    else:
        times = tms

    for i in range(times):
        start = dt.datetime.now()
        debug(f"\n\n------------------------ {i + 1} ------------------------\n\n")

        e.encrypt()
        ll = e.decrypt()
        l = len(ll)

        end = dt.datetime.now()

        time_delta = (end - start)
        x.append(i + 1)
        y.append(time_delta.total_seconds())
        lens.append(((time_delta.total_seconds() / l) / 1000))
        rawLens.append(l)
        dec.append(len(ll.decode(
            encoding
        )))
        y2.append(time_delta.total_seconds())

    de = e.decrypt()

    print(QATypeConv.convert(de, str)[-1].strip())
    print(BYTES_OPS().get_bytes_encoding(de))

    xs = np.array(x);
    ys = np.array(y);
    lens = np.array(lens);
    rawLens = np.array(rawLens);
    y2 = np.array(y2);
    dec = np.array(dec)

    plt.figure()

    plt.suptitle(f"FileIOHandler Encryption Timing ({times} runs, {encoding})")

    plt.subplot(411)

    plt.plot(xs, rawLens, 'g')
    # plt.xlabel(f"Calculation #")
    plt.ylabel(f"# Characters")

    plt.subplot(412)

    plt.plot(xs, dec, 'y')
    # plt.xlabel(f"Calculation #")
    plt.ylabel(f"# Decoded Chracters")

    plt.subplot(413)

    plt.plot(xs, ys, 'r')
    # plt.xlabel(f"Calculation #")
    plt.ylabel(f"Run Time (s)")

    plt.subplot(414)

    plt.plot(xs, lens, 'b')
    plt.xlabel(f"Calculation #")
    plt.ylabel(f"Run Time / Character (ms)")

    plt.show()

# path = 'testfile.txt'
#
# test_timing(path, 'Hello, World!', 'utf-32', 500)
#
# obj = create_fileIO_object(path)
#
# save(obj, "Hello, World!", encryptData=True, encoding='utf-16')
#
# print(read(obj))
