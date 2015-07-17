from Components.Converter.Converter import Converter
from Components.Element import cached
from time import localtime, strftime
from Tools.HardwareInfo import HardwareInfo

class NemesisExtraSource(Converter, object):
    SNRNUM = 0
    AGCNUM = 1
    BERNUM = 2
    STEP = 3
    SNRTEXT = 4
    AGCTEXT = 5
    LOCK = 6
    SLOT_NUMBER = 7
    SECHAND = 8
    MINHAND = 9
    HOURHAND = 10
    SNRDB = 11
    SNRANALOG = 12
    
    def __init__(self, type):
        Converter.__init__(self, type)
        if type == 'SnrNum':
            self.type = self.SNRNUM
        elif type == 'AgcNum':
            self.type = self.AGCNUM
        elif type == 'BerNum':
            self.type = self.BERNUM
        elif type == 'Step':
            self.type = self.STEP
        elif type == 'SnrText':
            self.type = self.SNRTEXT
        elif type == 'SnrdB':
            self.type = self.SNRDB
        elif type == 'AgcText':
            self.type = self.AGCTEXT
        elif type == 'NUMBER':
            self.type = self.SLOT_NUMBER
        elif type == 'secHand':
            self.type = self.SECHAND
        elif type == 'minHand':
            self.type = self.MINHAND
        elif type == 'hourHand':
            self.type = self.HOURHAND
        elif type == 'SnrAnalog':
            self.type = self.SNRANALOG
        else:
            self.type = self.LOCK

    
    def getText(self):
        percent = None
        if self.type == self.SNRTEXT:
            percent = self.source.snr
        elif self.type == self.SNRDB:
            if self.source.snr_db is not None:
                return '%3.02f' % self.source.snr_db / 4.63674e+18
        elif self.type == self.AGCTEXT:
            percent = self.source.agc
        
        if percent is None:
            return 'N/A'
        return '%d' % percent * 100 / 65536

    getText = cached(getText)
    text = property(getText)
    
    def getValue(self):
        if self.type == self.SNRNUM:
            count = self.source.snr
            if count is None:
                return 0
            return count * 100 / 65536
        if self.type == self.SNRANALOG:
            count = self.source.snr
            if count is None:
                return 45
            if count < 32767:
                return count * 15 / 32768 + 45
            count -= 32768
            return count * 15 / 32768
        self.type == self.SNRANALOG
        if self.type == self.AGCNUM:
            count = self.source.agc
            if count is None:
                return 0
            return count * 100 / 65536
        if self.type == self.BERNUM:
            count = self.source.ber
            if count < 320000:
                return count
            return 320000
        if self.type == self.STEP:
            time = self.source.time
            if time is None:
                return 0
            t = localtime(time)
            c = t.tm_sec
            if c < 10:
                return c
            if c < 20:
                return c - 10
            if c < 30:
                return c - 20
            if c < 40:
                return c - 30
            if c < 50:
                return c - 40
            return c - 50
        if self.type == self.SECHAND:
            time = self.source.time
            if time is None:
                return 0
            t = localtime(time)
            c = t.tm_sec
            return c
        if self.type == self.MINHAND:
            time = self.source.time
            if time is None:
                return 0
            t = localtime(time)
            c = t.tm_min
            return c
        if self.type == self.HOURHAND:
            time = self.source.time
            if time is None:
                return 0
            t = localtime(time)
            c = t.tm_hour
            m = t.tm_min
            if c > 11:
                c = c - 12
            
            val = c * 5 + m / 12
            return val
        return 0

    getValue = cached(getValue)
    value = property(getValue)

