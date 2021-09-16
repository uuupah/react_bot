import pytz
from datetime import datetime # fuck this library

def now():
    tz = pytz.timezone('AUSTRALIA/Adelaide')
    return datetime.now(tz).strftime("-%H.%M.%S %d.%m.%y")