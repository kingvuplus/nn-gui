import os
from Converter import Converter
from time import localtime, strftime
from Components.Element import cached
from Components.Language import language

class ClockToText(Converter, object):
    DEFAULT = 0
    WITH_SECONDS = 1
    IN_MINUTES = 2
    DATE = 3
    FORMAT = 4
    AS_LENGTH = 5
    TIMESTAMP = 6
    
    def readLocaleStrings(self):
        self.lcMonths = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December']
        if os.path.isfile('/etc/lcstrings.list') is True:
            myfile = open('/etc/lcstrings.list', 'r').readlines()
            idx = language.getActiveLanguageIndex()
            tmp = myfile[idx].split(',')
            if not tmp[0].__contains__('#'):
                self.lcMonths = myfile[idx].split(',')
                for index in range(len(self.lcMonths)):
                    self.lcMonths[index] = self.lcMonths[index].strip()
                
            
        

    
    def toLocale(self, s):
        WeekDays = [
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday']
        Months = [
            'January',
            'February',
            'March',
            'April',
            'May',
            'June',
            'July',
            'August',
            'September',
            'October',
            'November',
            'December']
        for None in enumerate(WeekDays):
            (index, weekday) = None
            if s.find(weekday) >= 0:
                s = s.replace(weekday, _(weekday))
                break
                continue
        for None in enumerate(Months):
            (index, month) = None
            if s.find(month) >= 0:
                s = s.replace(month, _(month))
                break
                continue
        return s

    
    def __init__(self, type):
        Converter.__init__(self, type)
        if type == 'WithSeconds':
            self.type = self.WITH_SECONDS
        elif type == 'InMinutes':
            self.type = self.IN_MINUTES
        elif type == 'Date':
            self.type = self.DATE
        elif type == 'AsLength':
            self.type = self.AS_LENGTH
        elif type == 'Timestamp':
            self.type = self.TIMESTAMP
        elif str(type).find('Format:') != -1:
            self.type = self.FORMAT
            self.fmt_string = type[7:]
        else:
            self.type = self.DEFAULT
        self.readLocaleStrings()

    
    def getText(self):
        time = self.source.time
        if time is None:
            return ''
        if self.type == self.IN_MINUTES:
            return '%d min' % time / 60
        if self.type == self.AS_LENGTH:
            return '%d:%02d' % (time / 60, time % 60)
        if self.type == self.TIMESTAMP:
            return str(time)
        t = localtime(time)
        if self.type == self.WITH_SECONDS:
            return '%2d:%02d:%02d' % (t.tm_hour, t.tm_min, t.tm_sec)
        if self.type == self.DEFAULT:
            return '%02d:%02d' % (t.tm_hour, t.tm_min)
        if self.type == self.DATE:
            return self.toLocale(strftime('%A %B %d, %Y', t))
        if self.type == self.FORMAT:
            spos = self.fmt_string.find('%')
            if spos > 0:
                s1 = self.fmt_string[:spos]
                s2 = strftime(self.fmt_string[spos:], t)
                return self.toLocale(str(s1 + s2))
            return self.toLocale(strftime(self.fmt_string, t))
        self.type == self.FORMAT
        return '???'

    getText = cached(getText)
    text = property(getText)

