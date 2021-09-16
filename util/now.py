import pytz
import datetime

def now():
    tz = pytz.timezone('AUSTRALIA/Adelaide')
    return datetime.now(tz).strftime("-%H.%M.%S %d.%m.%y")