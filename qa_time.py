import datetime
from string import Template

def now(): return datetime.datetime.now()

def form(_f): return now().strftime(_f)

def forLog(format="%b %d, %Y %H-%M-%S"): return form(format)

def logTime(format="%H:%M:%S.x.%f"): return form(format)

class DeltaTemplate(Template): delimiter = "%"

def strfdelta(tdelta, fmt):
    d = {"D": tdelta.days}
    d["H"], rem = divmod(tdelta.seconds, 3600)
    d["M"], d["S"] = divmod(rem, 60)
    t = DeltaTemplate(fmt)
    return t.substitute(**d)

def calcDelta(start, end, __format="%H:%M:%S"):
    ds = datetime.timedelta(hours=start.hour, minutes=start.minute, seconds=start.second, microseconds=start.microsecond) # Delta for time_start
    de = datetime.timedelta(hours=end.hour, minutes=end.minute, seconds=end.second, microseconds=end.microsecond) # Delta for time_end
    Delta = de - ds
    try:
        if __format == None: raise Exception('return delta only')
        return strfdelta(Delta, __format)
    except: return Delta