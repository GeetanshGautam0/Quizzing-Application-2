# The powerful convertor
# All code in the following script is original
# Object Oriented Prog. ahead

import math

class data:
    # Indexes
    re_values_index_isValidBool = 0
    re_values_index_coveretedToDtype = 1
    re_values_index_convertedData = 2

    # Hardcoded Values
    re_values_invalid_dtype = [False, None, None]
    re_values_convErr = [None, None, None]

    # Changeable lists
    re_valid_template = [bool, type, 'Data']

    # Vars
    re_list_len = 3

class STR:
    def __init__(self, data: any, **kwargs) -> None: # Create instance of the variable in mem, call CONV to convert.
        self.supported = [
            int, tuple, list, dict, bytes, float, str
        ] # Supported From
        self.raw = data

        # raw handler
        if type(data) is bytes: # Convert to utf-8
            self.raw = bytes_reencode(self.raw, 'utf-8')

        self.dtype = type(data)

        self.function_map = {
            int: self.fint,
            tuple: self.ftuple,
            list: self.flist,
            dict: self.fdict,
            bytes: self.fbytes,
            float: self.ffloat,
            str: self.fstr
        }

        self.flags = {

            # Strip
            'strip': [True, (bool, )],
            'stripChars': [[], (list, tuple)],

            # Tuple / List
            'tu_lst_concat_sep': ['\n', (str, )],

            # Dict
            'dict_key_val_concat_sep': [' ', (str, )],
            'dict_line_sep': ['\n', (str, )],

            # Data
            'returnOnlyData': [False, (bool, )] # Set to True if you only want the data as an output (output = list[2] > str)

        }

        self.flags_editable: dict = flags_handler(self.flags, kwargs)
        flags_plain(Object=self) # Do not need to set to var; instance level var will be reset automatically

    def CONV(self) -> str:
        output = '' # Str

        toPP = False # PP = Post Processing (Apply Flags)
        PP_Skip = False

        # data vars pulled in
        template = data.re_valid_template
        invalid_dtype_output = data.re_values_invalid_dtype # No dtypes that cannot be converted to; comment out and save mem
        err_output = data.re_values_convErr

        valid_bool_ind = data.re_values_index_isValidBool
        dt_ind = data.re_values_index_coveretedToDtype
        output_ind = data.re_values_index_convertedData

        # Pre-processing (Is the same dt already?)

        if self.dtype is str:
            output = template
            output[valid_bool_ind] = True
            output[dt_ind] = str
            output[output_ind] = self.raw

            toPP = True # Set skip to post-processing to "True"

        # Mid processing (conversion)

        if not toPP: # To be converted
            if self.dtype in self.supported:

                try:

                    # Step 1: Get the right function
                    _func = self.function_map[self.dtype]

                    # Step 2: Call the function and save the result
                    _res = _func()

                    # Step 3: Set output
                    if type(_res) is str: # Is valid
                        output = template
                        output[valid_bool_ind] = True
                        output[dt_ind] = str
                        output[output_ind] = _res

                    else: # Is invalid
                        raise Exception("Pass to ERR Handler")

                except Exception as E:
                    print(f"Conversion err: {E}")

                    output = err_output
                    PP_Skip = True

            else:
                output = invalid_dtype_output
                PP_Skip = True

        # Post Processing

        if self.flags['strip'] and not PP_Skip:
            output[output_ind] = output[output_ind].strip()

        if not PP_Skip:
            for i in self.flags['stripChars']:
                output[output_ind] = output[output_ind].strip(i)

        if self.flags['returnOnlyData'] and not PP_Skip:
            output = output[output_ind]

        return output

    def fint(self) -> str:
        # Integer => str
        out: str = str(self.raw)
        return out

    def ftuple(self) -> str:
        # Tuple > str
        out: str = ''
        for i in self.raw: out += f"{i}{self.flags['tu_lst_concat_sep']}"
        return out

    def flist(self) -> str:
        # List > str
        out: str = ''
        for i in self.raw: out += f"{i}{self.flags['tu_lst_concat_sep']}"
        return out

    def fdict(self) -> str:
        # Dict > str
        out: str = ''
        for k, v in self.raw.items(): out += f"{k}{self.flags['dict_key_val_concat_sep']}{v}{self.flags['dict_line_sep']}"
        return out

    def fbytes(self) -> str:
        # Bytes > str
        out: str = self.raw.decode('utf-8')
        return out

    def ffloat(self) -> str:
        # Float > str
        out: str = str(self.raw)
        return out

    def fstr(self) -> str:
        # Str > str
        return self.raw

class BYTES:
    def __init__(self, data: any, **kwargs) -> None:
        self.supported = [
            int, tuple, list, dict, bytes, float, str
        ]  # Supported From
        self.raw = data

        if type(self.raw) is bytes:
            self.raw = bytes_reencode(self.raw, 'utf-8')

        self.dtype = type(data)

        self.function_map = {
            int: self.fint,
            tuple: self.ftuple,
            list: self.flist,
            dict: self.fdict,
            bytes: self.fbytes,
            float: self.ffloat,
            str: self.fstr
        }

        self.flags = {

            # Tuple / List
            'tu_lst_concat_sep': ['\n', (str, )],

            # Dict
            'dict_key_val_concat_sep': [' ', (str,)],
            'dict_line_sep': ['\n', (str,)],

            # Data
            'returnOnlyData': [False, (bool,)],
            # Set to True if you only want the data as an output (output = list[2] > str)

            # Misc
            'encodingFormat': ['utf-8', (str, )]

        }

        self.flags_editable: dict = flags_handler(self.flags, kwargs)
        flags_plain(Object=self)  # Do not need to set to var; instance level var will be reset automatically

    def CONV(self) -> bytes:
        output: bytes = b''  # Bytes

        toPP = False  # PP = Post Processing (Apply Flags)
        PP_Skip = False

        # data vars pulled in
        template = data.re_valid_template
        invalid_dtype_output = data.re_values_invalid_dtype  # No dtypes that cannot be converted to; comment out and save mem
        err_output = data.re_values_convErr

        valid_bool_ind = data.re_values_index_isValidBool
        dt_ind = data.re_values_index_coveretedToDtype
        output_ind = data.re_values_index_convertedData

        # Pre-processing (Is the same dt already?)

        if self.dtype is bytes:
            output = template
            output[valid_bool_ind] = True
            output[dt_ind] = bytes
            output[output_ind] = self.raw

            toPP = True  # Set skip to post-processing to "True"

        # Mid processing (conversion)

        if not toPP:  # To be converted
            if self.dtype in self.supported:

                try:

                    # Step 1: Get the right function
                    _func = self.function_map[self.dtype]

                    # Step 2: Call the function and save the result
                    _res = _func()

                    # Step 3: Set output
                    if type(_res) is bytes:  # Is valid
                        output = template
                        output[valid_bool_ind] = True
                        output[dt_ind] = bytes
                        output[output_ind] = _res

                    else:  # Is invalid
                        raise Exception("Pass to ERR Handler")

                except Exception as E:
                    print(f"Conversion err: {E}")

                    output = err_output
                    PP_Skip = True

            else:
                output = invalid_dtype_output
                PP_Skip = True

            # Post Processing

            output[output_ind] = bytes_reencode(output[output_ind], self.flags['encodingFormat'])

            if self.flags['returnOnlyData'] and not PP_Skip: # Last post conversion thing
                output = output[output_ind]

            return output

    def fint(self) -> bytes:
        # Int >> bytes
        out: bytes = str(self.raw).encode('utf-8')
        return out

    def fstr(self) -> bytes:
        # str >> bytes
        out: bytes = self.raw.encode('utf-8')
        return out

    def fbytes(self) -> bytes:
        # Bytes >> bytes
        return self.raw

    def flist(self) -> bytes:
        tmp: str = ''
        for i in self.raw: tmp += f"{i}{self.flags['tu_lst_concat_sep']}"
        out: bytes = tmp.encode('utf-8')
        return out

    def ftuple(self) -> bytes:
        tmp: str = ''
        for i in self.raw: tmp += f"{i}{self.flags['tu_lst_concat_sep']}"
        out: bytes = tmp.encode('utf-8')
        return out

    def fdict(self) -> bytes:
        tmp: str = ''
        for k, v in self.raw.items(): tmp += f"{k}{self.flags['dict_key_val_concat_sep']}{v}{self.flags['dict_line_sep']}"
        out: bytes = tmp.encode('utf-8')
        return out

    def ffloat(self) -> bytes:
        out: bytes = str(self.raw).encode('utf-8')

class INT:
    def __init__(self, data: any, **kwargs) -> None:
        self.supported = [
            bytes, str, float, int, list, tuple
        ]  # Supported From
        self.raw = data
        self.dtype = type(data)
        self.type = int
        self.NORMAL_ROUND = 'norm'
        self.FLOOR = 'floor'
        self.CEIL = 'ceil'

        if type(self.raw) is bytes:
            self.raw = bytes_reencode(self.raw, 'utf-8')

        self.function_map = {
            int: self.fint,
            bytes: self.fbytes,
            float: self.ffloat,
            str: self.fstr,
            tuple: self.ftuple,
            list: self.flist
        }

        self.flags = {

            # Floor / Ceil
            'round': [self.NORMAL_ROUND, (str, )],

            # Data
            'returnOnlyData': [False, (bool,)]
            # Set to True if you only want the data as an output (output = list[2] > str)

        }

        self.flags_editable: dict = flags_handler(self.flags, kwargs)
        flags_plain(Object=self)  # Do not need to set to var; instance level var will be reset automatically

    def CONV(self) -> int:
        output: int = 0  # Int

        toPP = False  # PP = Post Processing (Apply Flags)
        PP_Skip = False

        # data vars pulled in
        template = data.re_valid_template
        invalid_dtype_output = data.re_values_invalid_dtype  # No dtypes that cannot be converted to; comment out and save mem
        err_output = data.re_values_convErr

        valid_bool_ind = data.re_values_index_isValidBool
        dt_ind = data.re_values_index_coveretedToDtype
        output_ind = data.re_values_index_convertedData

        # Pre-processing (Is the same dt already?)

        if self.dtype is self.type:
            output = template
            output[valid_bool_ind] = True
            output[dt_ind] = self.type
            output[output_ind] = self.raw

            toPP = True  # Set skip to post-processing to "True"

        # Mid processing (conversion)

        if not toPP:  # To be converted
            if self.dtype in self.supported:

                try:

                    # Step 1: Get the right function
                    _func = self.function_map[self.dtype]

                    # Step 2: Call the function and save the result
                    _res = _func()

                    # Step 3: Set output
                    if type(_res) is self.type:  # Is valid
                        output = template
                        output[valid_bool_ind] = True
                        output[dt_ind] = self.type
                        output[output_ind] = _res

                    else:  # Is invalid
                        raise Exception("Pass to ERR Handler")

                except Exception as E:
                    print(f"Conversion err: {E}")

                    output = err_output
                    PP_Skip = True

            else:
                output = invalid_dtype_output
                PP_Skip = True

        # Post Processing

        if self.flags['returnOnlyData'] and not PP_Skip:  # Last post conversion thing
            output = output[output_ind]

        return output

    def fint(self) -> int:
        return self.raw

    def fstr(self) -> int:
        raw = filter_non_nums(self.raw)
        out_fl: float = float(raw)
        out: int = self.round(out_fl)
        return out

    def fbytes(self) -> int:
        raw = filter_non_nums(self.raw.decode('utf-8'))
        out_fl: float = float(raw)
        out: int = self.round(out_fl)
        return out

    def ffloat(self) -> int:
        out: int = self.round(self.raw)
        return out

    def ftuple(self):
        # Tuple > Int (sum)
        return self.flist()

    def flist(self):
        # List > Int (sum)
        out: int = 0

        for i in self.raw:
            # conv to str first to have reliable conversion
            tmp = STR(i, returnOnlyData=True)
            tmp = tmp.CONV()

            # filter
            tmp = filter_non_nums(tmp, allow_decimal=True) # Float

            # Round
            tmp = self.round(Float=tmp)

            # add
            out += tmp

        return out


    def round(self, Float: float) -> int:
        if type(Float) is int: return Float
        elif type(Float) is not float:
            Float = FLOAT(Float, returnDataOnly=True)
            Float = Float.CONV()

        def round_round(FLOAT):
            out: int = int(FLOAT)
            if FLOAT >= out + 0.5: return out + 1
            return out

        if self.flags['round'] == self.NORMAL_ROUND: return round_round(Float)
        elif self.flags['round'] == self.CEIL: return int(math.ceil(Float))
        elif self.flags['round'] == self.FLOOR: return int(math.floor(Float))
        else: raise AttributeError(f"Invalid key '{self.flags['round']}' for flag 'round' - INT")

class LIST:
    def __init__(self, data: any, **kwargs) -> None:
        self.supported = [
            str, bytes, tuple, list
        ]  # Supported From
        self.raw = data
        self.dtype = type(data)
        self.type = list

        if type(data) is bytes: self.raw = bytes_reencode(data, 'utf-8')

        print(f"<<0x001010>> self.raw = {self.raw}")

        self.function_map = {
            tuple: self.ftuple,
            bytes: self.fbytes,
            list: self.flist,
            str: self.fstr
        }

        self.flags = {

            # Str, bytes sep
            'str_bytes_sep': ['\n', (str, )],

            # Data
            'returnOnlyData': [False, (bool,)]
            # Set to True if you only want the data as an output (output = list[2] > str)

        }

        self.flags_editable: dict = flags_handler(self.flags, kwargs)
        flags_plain(Object=self)  # Do not need to set to var; instance level var will be reset automatically

    def CONV(self) -> list:
        output: list = []  # List

        toPP = False  # PP = Post Processing (Apply Flags)
        PP_Skip = False

        # data vars pulled in
        template = data.re_valid_template
        invalid_dtype_output = data.re_values_invalid_dtype  # No dtypes that cannot be converted to; comment out and save mem
        err_output = data.re_values_convErr

        valid_bool_ind = data.re_values_index_isValidBool
        dt_ind = data.re_values_index_coveretedToDtype
        output_ind = data.re_values_index_convertedData

        # Pre-processing (Is the same dt already?)

        if self.dtype is self.type:
            output = template
            output[valid_bool_ind] = True
            output[dt_ind] = self.type
            output[output_ind] = self.raw

            toPP = True  # Set skip to post-processing to "True"

        # Mid processing (conversion)

        if not toPP:  # To be converted
            if self.dtype in self.supported:

                try:

                    # Step 1: Get the right function
                    _func = self.function_map[self.dtype]

                    # Step 2: Call the function and save the result
                    _res = _func()

                    # Step 3: Set output
                    if type(_res) is self.type:  # Is valid
                        output = template
                        output[valid_bool_ind] = True
                        output[dt_ind] = self.type
                        output[output_ind] = _res

                    else:  # Is invalid
                        raise Exception("Pass to ERR Handler")

                except Exception as E:
                    print(f"Conversion err: {E}")

                    output = err_output
                    PP_Skip = True

            else:
                output = invalid_dtype_output
                PP_Skip = True

        # Post Processing
        # Remove whitespace
        tmp = []

        print(f'<<0x001018>> {output}')

        for i in output[-1]:
            iqd = STR(i).CONV()[-1] if type(i) is not str else i
            if len(iqd.strip()) > 0: tmp.append(
                iqd.strip().encode(
                    'utf-8'
                )
            )

        output[output_ind] = tmp

        print(f'<<0x001019>> {output}')

        if self.flags['returnOnlyData'] and not PP_Skip:  # Last post conversion thing
            output = output[output_ind]

        print(f'<<0x001020>> {output}')

        return output

    def flist(self) -> list:
        return self.raw

    def ftuple(self) -> list:
        out: list = list(self.raw)
        return out

    def fstr(self) -> list:
        sep = self.flags['str_bytes_sep']
        out: list = self.raw.split(sep)
        return out

    def fbytes(self) -> list:
        sep = self.flags['str_bytes_sep']
        strVar = STR(self.raw, returnOnlyData=True); strVar = strVar.CONV()
        tmp: list = strVar.split(sep); out: list = []

        # Re-encode
        for i in tmp: out.append(i.encode('utf-8'))

        print(f'0x001011 >> {out}')

        return out

class TUPLE:
    def __init__(self, data: any, **kwargs) -> None:
        self.supported = [
            str, bytes, tuple, list
        ]  # Supported From
        self.raw = data
        self.dtype = type(data)
        self.type = tuple

        if type(data) is bytes: self.raw = bytes_reencode(data, 'utf-8')

        self.function_map = {
            tuple: self.ftuple,
            bytes: self.fbytes,
            list: self.flist,
            str: self.fstr
        }

        self.flags = {

            # Str, bytes sep
            'str_bytes_sep': ['\n', (str,)],

            # Data
            'returnOnlyData': [False, (bool,)]
            # Set to True if you only want the data as an output (output = list[2] > str)

        }

        self.flags_editable: dict = flags_handler(self.flags, kwargs)
        flags_plain(Object=self)  # Do not need to set to var; instance level var will be reset automatically

    def CONV(self) -> tuple:
        output: tuple = ()  # Tuple

        toPP = False  # PP = Post Processing (Apply Flags)
        PP_Skip = False

        # data vars pulled in
        template = data.re_valid_template
        invalid_dtype_output = data.re_values_invalid_dtype  # No dtypes that cannot be converted to; comment out and save mem
        err_output = data.re_values_convErr

        valid_bool_ind = data.re_values_index_isValidBool
        dt_ind = data.re_values_index_coveretedToDtype
        output_ind = data.re_values_index_convertedData

        # Pre-processing (Is the same dt already?)

        if self.dtype is self.type:
            output = template
            output[valid_bool_ind] = True
            output[dt_ind] = self.type
            output[output_ind] = self.raw

            toPP = True  # Set skip to post-processing to "True"

        # Mid processing (conversion)

        if not toPP:  # To be converted
            if self.dtype in self.supported:

                try:

                    # Step 1: Get the right function
                    _func = self.function_map[self.dtype]

                    # Step 2: Call the function and save the result
                    _res = _func()

                    # Step 3: Set output
                    if type(_res) is self.type:  # Is valid
                        output = template
                        output[valid_bool_ind] = True
                        output[dt_ind] = self.type
                        output[output_ind] = _res

                    else:  # Is invalid
                        raise Exception("Pass to ERR Handler")

                except Exception as E:
                    print(f"Conversion err: {E}")

                    output = err_output
                    PP_Skip = True

            else:
                output = invalid_dtype_output
                PP_Skip = True

        # Post Processing

        # Clear white space
        tmp = []
        for i in output[-1]:
            iqd = STR(i).CONV() if type(i) is not str else i
            if len(iqd.strip()) > 0: tmp.append(iqd)
        output = (
            output[valid_bool_ind],
            output[dt_ind],
            self.ltt(tmp)
        )

        if self.flags['returnOnlyData'] and not PP_Skip:  # Last post conversion thing
            output = output[output_ind]

        return output

    def ftuple(self) -> tuple:
        return self.raw

    def flist(self) -> tuple:
        return self.ltt(self.raw)

    def fstr(self) -> tuple:
        sep = self.flags['str_bytes_sep']
        out: list = self.raw.split(sep)
        return self.ltt(out)

    def fbytes(self) -> tuple:
        sep = self.flags['str_bytes_sep']
        strVar = STR(self.raw, returnOnlyData=True); strVar = strVar.CONV()
        tmp: list = strVar.split(sep); out: list = []

        # Re-encode
        for i in tmp: out.append(i.encode('utf-8'))

        return self.ltt(out)

    def ltt(self, lst) -> tuple:
        return tuple(lst) if type(lst) is list else lst

class DICT:
    def __init__(self, data: any, **kwargs) -> None:
        self.supported = [
            str, bytes, dict
        ]  # Supported From
        self.raw = data
        self.dtype = type(data)
        self.type = dict

        if type(data) is bytes: self.raw = bytes_reencode(data, 'utf-8')

        self.function_map = {
            dict: self.fdict, # Fallback ofc
            bytes: self.fbytes,
            str: self.fstr
        }

        self.flags = {

            # Str, bytes sep
            'key_val_sep': [' ', (str,)],
            'entry_sep': ['\n', (str, )],

            # Data
            'returnOnlyData': [False, (bool,)]
            # Set to True if you only want the data as an output (output = list[2] > str)

        }

        self.flags_editable: dict = flags_handler(self.flags, kwargs)
        flags_plain(Object=self)  # Do not need to set to var; instance level var will be reset automatically

    def CONV(self) -> dict:
        output: dict = {}  # Dict

        toPP = False  # PP = Post Processing (Apply Flags)
        PP_Skip = False

        # data vars pulled in
        template = data.re_valid_template
        invalid_dtype_output = data.re_values_invalid_dtype  # No dtypes that cannot be converted to; comment out and save mem
        err_output = data.re_values_convErr

        valid_bool_ind = data.re_values_index_isValidBool
        dt_ind = data.re_values_index_coveretedToDtype
        output_ind = data.re_values_index_convertedData

        # Pre-processing (Is the same dt already?)

        if self.dtype is self.type:
            output = template
            output[valid_bool_ind] = True
            output[dt_ind] = self.type
            output[output_ind] = self.raw

            toPP = True  # Set skip to post-processing to "True"

        # Mid processing (conversion)

        if not toPP:  # To be converted
            if self.dtype in self.supported:

                try:

                    # Step 1: Get the right function
                    _func = self.function_map[self.dtype]

                    # Step 2: Call the function and save the result
                    _res = _func()

                    # Step 3: Set output
                    if type(_res) is self.type:  # Is valid
                        output = template
                        output[valid_bool_ind] = True
                        output[dt_ind] = self.type
                        output[output_ind] = _res

                    else:  # Is invalid
                        raise Exception("Pass to ERR Handler")

                except Exception as E:
                    print(f"Conversion err: {E}")

                    output = err_output
                    PP_Skip = True

            else:
                output = invalid_dtype_output
                PP_Skip = True

        # Post Processing
        # Pop empty strings
        if self.dtype is str or self.dtype is bytes:
            pop = []
            for i in output[-1]:
                q = output[-1][i] # Data
                qd = STR(q, returnOnlyData=True).CONV() if type(q) is not str else q

                if len(qd.strip()) <= 0:
                    pop.append(i)

            for i in pop:
                output[-1].pop(i)

        if self.flags['returnOnlyData'] and not PP_Skip:  # Last post conversion thing
            output = output[output_ind]

        return output

    def fdict(self):
        return self.raw

    def fstr(self):
        kvSep = self.flags['key_val_sep']; eSep = self.flags['entry_sep']
        lst = self.raw.split(eSep)
        out: dict = {}

        for i in lst:
            i = i.strip()
            k = i.split(kvSep)[0]
            v = i.replace(k, '', 1).strip()
            out[k] = v

        return out

    def fbytes(self):
        raw = STR(self.raw, returnOnlyData=True)
        raw = raw.CONV()

        kvSep = self.flags['key_val_sep']
        eSep = self.flags['entry_sep']
        lst = raw.split(eSep)
        out: dict = {}

        for i in lst:
            i = i.strip()
            k = i.split(kvSep)[0]
            v = i.replace(k, '', 1).strip().encode('utf-8')
            k = k.encode('utf-8')

            out[k] = v

        return out

class FLOAT:
    def __init__(self, data: any, **kwargs) -> None:
        self.supported = [
            str, bytes, int, float, list, tuple
        ]  # Supported From
        self.raw = data
        self.dtype = type(data)
        self.type = float

        if type(data) is bytes: self.raw = bytes_reencode(data, 'utf-8')

        self.function_map = {
            float: self.ffloat, # fallback
            str: self.fstr,
            bytes: self.fbytes,
            int: self.fint,
            list: self.flist,
            tuple: self.ftuple
        }

        self.flags = {

            # Data
            'returnOnlyData': [False, (bool,)]
            # Set to True if you only want the data as an output (output = list[2] > str)

        }

        self.flags_editable: dict = flags_handler(self.flags, kwargs)
        flags_plain(Object=self)  # Do not need to set to var; instance level var will be reset automatically

    def CONV(self) -> float:
        output: float = 0.00  # Float

        toPP = False  # PP = Post Processing (Apply Flags)
        PP_Skip = False

        # data vars pulled in
        template = data.re_valid_template
        invalid_dtype_output = data.re_values_invalid_dtype  # No dtypes that cannot be converted to; comment out and save mem
        err_output = data.re_values_convErr

        valid_bool_ind = data.re_values_index_isValidBool
        dt_ind = data.re_values_index_coveretedToDtype
        output_ind = data.re_values_index_convertedData

        # Pre-processing (Is the same dt already?)

        if self.dtype is self.type:
            output = template
            output[valid_bool_ind] = True
            output[dt_ind] = self.type
            output[output_ind] = self.raw

            toPP = True  # Set skip to post-processing to "True"

        # Mid processing (conversion)

        if not toPP:  # To be converted
            if self.dtype in self.supported:

                try:

                    # Step 1: Get the right function
                    _func = self.function_map[self.dtype]

                    # Step 2: Call the function and save the result
                    _res = _func()

                    # Step 3: Set output
                    if type(_res) is self.type:  # Is valid
                        output = template
                        output[valid_bool_ind] = True
                        output[dt_ind] = self.type
                        output[output_ind] = _res

                    else:  # Is invalid
                        raise Exception("Pass to ERR Handler")

                except Exception as E:
                    print(f"Conversion err: {E}")

                    output = err_output
                    PP_Skip = True

            else:
                output = invalid_dtype_output
                PP_Skip = True

        # Post Processing

        if self.flags['returnOnlyData'] and not PP_Skip:  # Last post conversion thing
            output = output[output_ind]

        return output

    def ffloat(self):
        return self.raw

    def fint(self):
        return float(self.raw)

    def fstr(self):
        return filter_non_nums(self.raw)

    def fbytes(self):
        return filter_non_nums(self.raw.decode('utf-8'))

    def flist(self):
        out: float = 0.00

        for i in self.raw: out += filter_non_nums(STR(i).CONV()[-1])

        return out

    def ftuple(self):
        return self.flist()

def flags_handler(reference: dict, flags: dict, __replain: bool = False, __raiseerr: bool = True) -> dict:
    """
    **flags_handler**
    Useful for setting reference dictionaries to that given as **kwargs
    *Reference syntax*: {'flag key': List[<set to>, Tuple(<supported data types)]}
    :param reference: dict
    :param flags: dict
    :param __replain: boolean; return plain dictionary? i.e. {<flag key>: <value>}
    :param __raiseerr: boolean; raise error for usupported and incorrect entries/flags
    :return: dict
    """

    converted = [] # Although useless because dicts only keep one instance.
    ref = reference; kwargs = flags; out = ref

    for i in kwargs:

        given = kwargs[i]

        if i in ref:
            if type(given) in ref[i][-1] and i not in converted:
                out[i] = [given, ref[i][-1]]
                converted.append(i)

            elif __raiseerr:
                if i in converted:
                    raise AttributeError(f"Set data for flag '{i}' already.")
                else:
                    raise TypeError(f"Unsupported type {type(given)} for flag {i}; expected one of {ref[i][-1]}")

        elif __raiseerr:
            raise NameError(f"Invalid flag name '{i}'")

    if __replain:
        for i in out.keys(): out[i] = out[i][0]

    return out

def flags_plain(Object=None, Flags: list = None) -> dict:
    out: dict = {}; flags = Object.flags if Object is not None else Flags if Flags is not None else None

    for i in flags.keys():
        out[i] = flags[i][0]

    if Object is not None: Object.flags = out # Set the flags

    return out

def filter_non_nums(Data, allow_decimal=True) -> float:
    out_s: str = ''; output: float = 0.00; dec: bool = False
    if type(Data) is int or type(Data) is float: return Data

    if Data is not str:
        tmp_1 = STR(Data, returnOnlyData=True)
        Data = tmp_1.CONV()

    allowed_chars: list = [str(i) for i in range(10)]
    if allow_decimal: allowed_chars.append('.')

    for i in range(len(Data)):
        if Data[i] in allowed_chars: out_s += Data[i] if not (Data[i] == '.' and dec) else ''
        if Data[i] == '.': dec = True

    output = float(out_s) if not out_s == '' else 0.00

    return output

def EDIT_FLAGS(Object, __plain=True, **kwargs) -> dict:
    # Template
    template = Object.flags_editable

    # Handler
    _chg = flags_handler(template, kwargs) # Do not plain

    # Set
    Object.flags_editable = _chg
    Object.flags = _chg

    # Plain
    if __plain:
        flags_plain(Object=Object)

    return Object.flags

def conv_isSupported(Object, Data: any) -> bool:
    return type(Data) in Object.supported

def org_flags(mapper, categories, kwargs, key, glKey) -> dict:

    # print(f"\n\n\nMapper:{mapper}\nCats:{categories}\nKWARGS:{kwargs}\nKey:{key}\nGlKey:{glKey}\n")

    out: dict = {}

    # Step 1: Find the right flags
    fls = categories.get(key)
    fls.append(*categories.get(glKey))

    # print(f'FLS = {fls}')

    # Step 2: Map names from fls back to kwargs
    app_fs = {}
    for i in mapper:
        if mapper[i] in fls:
            app_fs[i] = mapper[i]
    tmp = []; pop = []
    for i in app_fs:
        if app_fs[i] in tmp:
            pop.append(i)
        else: tmp.append(app_fs[i])

    for i in pop: app_fs.pop(i)

    # print(f"app_fs={app_fs}")

    # Step 3: Find the flags and plain
    for i in app_fs:
        out[app_fs[i]] = kwargs.get(i)[0]

    # print(f"out={out}\n\n\n")

    return out

# Bytes
def bytes_find_encoding(Data: bytes, expected: str = 'utf-8') -> str:
    if not type(Data) is bytes: raise TypeError(f"Expected type {bytes} got {type(Data)}")

    possible = ['utf-8', 'utf-16', 'utf-32']
    encoding = None

    try:
        Data.decode(expected)
        encoding = expected

    except:
        for i in possible:
            try:
                Data.decode(i)
                encoding = i
            except: pass

    if encoding is None:
        raise UnicodeError(f"Unable to find encoding format for data {Data}; checked within formats {possible}")

    return encoding

def bytes_reencode(Data: bytes, encoding: str) -> bytes:
    enc = bytes_find_encoding(Data, encoding)

    deco = Data.decode(enc)

    enco = deco.encode(encoding)

    return enco

# Caller Method

def convert(data: any, to: type, **kwargs) -> any: # TODO: set this up
    """
    **QA_TYPECONVERTOR.convert**
    Main function to the conversion script.
    Powerful conversion from many types to others
    :param data: Data to convert (any)
    :param to: Datatype to convert to (type)
    :param kwargs: Flags (See "Supported Flags")
    :return: any
    ======================
    **Supported Conversions**
    1) str from...
        * bytes
        * int
        * tuple
        * list
        * dict
        * float
    2) bytes from...
        * str
        * int
        * tuple
        * list
        * dict
        * float
    3) int from...
        * bytes
        * str
        * float
        * list (sum)
        * tuple (sum)
    4) list from...
        * str
        * bytes
        * tuple
    5) tuple from...
        * str
        * bytes
        * list
    6) dict from...
        * str
        * bytes
    7) float from...
        * str
        * bytes
        * int
        * list (sum)
        * tuple (sum)
    * *Note that if a data type is the same as the convert to type it will be returned automatically*
    =======================
**Global Flags**
    1) 'returnDataOnly': [False, (bool, )]
**STR flags**
    1) 'str_strip' : bool def (True)
    2) 'str_stripChars' : list, tuple (def [])
    3) 'str_tu_list_concatSep' : str (def newline)
    4) 'str_dict_keyVal_concatSep' : str (def ' ')
    5) 'str_dict_entrySep' : str (def newline)
**BYTES flags**
    1) 'bytes_tu_list_concatSep' : str (def newline)
    2) 'bytes_dict_keyVal_concatSep': str (def ' ')
    3) 'bytes_dict_entrySep' : str (def newline)
    4) 'bytes_encoding': str (def 'utf-8') [See *Warnings.B1*]
**INT flags**
    1) 'int_roundingMethod' : str (def INT(inst).NORMAL_ROUND) [See *Warnings.I1*]
**LIST flags**
    1) 'list_str_bytes_entrySep': str (def newline)
**TUPLE flags**
    1) 'tuple_str_bytes_entrySep': str (def newline)
**DICT flags**
    1) 'dict_keyValSep': str (def ' ')
    2) 'dict_entrySep': str (def newline)
**FLOAT flags**
    *<none>*
    """

    tmp_intInst = INT(0)

    flags = {

        # Global Flags
        # 'returnOnlyData': [False, (bool, )] # Set to True if you only want the data as an output (output = list[2] > str)
        'returnDataOnly': [False, (bool, )],

        # STR flags
        # 'strip': [True, (bool, )],
        # 'stripChars': [[], (list, tuple)],
        # 'tu_lst_concat_sep': ['\n', (str, )],
        # 'dict_key_val_concat_sep': [' ', (str, )],
        # 'dict_line_sep': ['\n', (str, )],
        'str_strip': [True, (bool, )],
        'str_stripChars': [[], (list, tuple)],
        'str_tu_list_concatSep': ['\n', (str, )],
        'str_dict_keyVal_concatSep': [' ', (str, )],
        'str_dict_entrySep': ['\n', (str, )],

        # BYTES flags
        # 'tu_lst_concat_sep': ['\n', (str, )],
        # 'dict_key_val_concat_sep': [' ', (str,)],
        # 'dict_line_sep': ['\n', (str,)],
        # 'encodingFormat': ['utf-8', (str, )]
        'bytes_tu_list_concatSep': ['\n', (str, )],
        'bytes_dict_keyVal_concatSep': [' ', (str, )],
        'bytes_dict_entrySep': ['\n', (str, )],
        'bytes_encodingFormat': ['utf-8', (str, )],

        # INT flags
        # 'round': [self.NORMAL_ROUND, (str, )], - use <instance>.NORMAL_ROUND/FLOOR/CEIL
        'int_roundingMethod': [tmp_intInst.NORMAL_ROUND, (str, )],

        # LIST flags
        # 'str_bytes_sep': ['\n', (str, )],
        'list_str_bytes_entrySep': ['\n', (str, )],

        # TUPLE flags
        # 'str_bytes_sep': ['\n', (str, )],
        'tuple_str_bytes_entrySep': ['\n', (str, )],

        # DICT flags
        # 'key_val_sep': [' ', (str,)],
        # 'entry_sep': ['\n', (str, )],
        'dict_keyValSep': [' ', (str, )],
        'dict_entrySep': ['\n', (str, )]

        # FLOAT flags
        # <none>

    }; flags = flags_handler(flags, kwargs)

    GLOBAL = 'global'

    flagMapper = {
        # Global
        'returnDataOnly': 'returnOnlyData',

        # STR
        'str_strip': 'strip',
        'str_stripChars': 'stripChars',
        'str_tu_list_concatSep': 'tu_lst_concat_sep',
        'str_dict_keyVal_concatSep': 'dict_key_val_concat_sep',
        'str_dict_entrySep': 'dict_line_sep',

        # BYTES
        'bytes_tu_list_concatSep': 'tu_lst_concat_sep',
        'bytes_dict_keyVal_concatSep': 'dict_key_val_concat_sep',
        'bytes_dict_entrySep': 'dict_line_sep',
        'bytes_encodingFormat': 'encodingFormat',

        # INT flags
        'int_roundingMethod': 'round',

        # LIST flags
        'list_str_bytes_entrySep': 'str_bytes_sep',

        # TUPLE flags
        'tuple_str_bytes_entrySep': 'str_bytes_sep',

        # DICT flags
        'dict_keyValSep': 'key_val_sep',
        'dict_entrySep': 'entry_sep'

        # FLOAT Flags
        # <none>

    }

    flag_cat = {

        GLOBAL: [
            'returnOnlyData'
        ],

        STR: [
            'strip',
            'stripChars',
            'tu_lst_concat_sep',
            'dict_key_val_concat_sep',
            'dict_line_sep',
        ],

        BYTES: [
            'tu_lst_concat_sep',
            'dict_key_val_concat_sep',
            'dict_line_sep',
            'encodingFormat'
        ],

        INT: [
            'round'
        ],

        LIST: [
            'str_bytes_sep'
        ],

        TUPLE: [
            'str_bytes_sep'
        ],

        DICT: [
            'key_val_sep',
            'entry_sep'
        ],

        FLOAT: [

        ]

    }

    classMapper = {
        float: FLOAT,
        str: STR,
        dict: DICT,
        list: LIST,
        tuple: TUPLE,
        int: INT,
        bytes: BYTES
    }

    filteredFlags: dict = org_flags(flagMapper, flag_cat, flags, classMapper[to], GLOBAL)

    dtype_og = type(data)

    Class = classMapper.get(to)
    call = Class(data, **filteredFlags)

    if not conv_isSupported(call, data):
        return data.re_values_invalid_dtype

    _res = call.CONV()

    return _res
