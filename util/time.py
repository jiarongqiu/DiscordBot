import pytz
from datetime import datetime,timedelta


class TimeUtil:

    TIMEZONE = 'Asia/Shanghai'

    @staticmethod
    def get_current_time():
        tz = pytz.timezone('Asia/Shanghai')
        time = datetime.now(tz)
        return time

    @staticmethod
    def get_date(offset=None,format='%Y%m%d'):
        time = TimeUtil.get_current_time()
        if offset:
            time = time +timedelta(days=offset)
        format_date = time.strftime(format)
        return format_date
    
    @staticmethod
    def get_time():
        time = TimeUtil.get_current_time()
        format_time = time.strftime('%Y%m%d %H:%M:%S')
        return format_time