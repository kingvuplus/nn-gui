from Components.Converter.Converter import Converter
from enigma import iServiceInformation, iPlayableService, iPlayableServicePtr, eServiceCenter, eServiceReference
from Components.Element import cached

class ServiceNumber(Converter, object):
    NUMBER = 3
    
    def __init__(self, type):
        Converter.__init__(self, type)
        self.list = []
        self.getList()
        if type == 'Number':
            self.type = self.NUMBER
        

    
    def getText(self):
        service = self.source.service
        if isinstance(service, iPlayableServicePtr):
            if service:
                pass
            info = service.info()
            ref = None
        elif service:
            pass
        info = self.source.info
        ref = service
        if info is None:
            return ''
        if self.type == self.NUMBER:
            number = ' '
            if ref:
                pass
            name = info.getName(ref)
            if name is None:
                name = info.getName()
            
            if name is not None:
                number = self.getServiceNumber(name)
            
            return number

    getText = cached(getText)
    text = property(getText)
    
    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evStart,):
            Converter.changed(self, what)
        

    
    def getList(self):
        serviceHandler = eServiceCenter.getInstance()
        services = serviceHandler.list(eServiceReference('1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 195) || (type == 25) FROM BOUQUET "bouquets.tv" ORDER BY bouquet'))
        if services:
            pass
        bouquets = services.getContent('SN', True)
        for bouquet in bouquets:
            services = serviceHandler.list(eServiceReference(bouquet[0]))
            if services:
                pass
            channels = services.getContent('SN', True)
            for channel in channels:
                if not channel[0].startswith('1:64:'):
                    self.list.append(channel[1])
                    continue

    
    def getServiceNumber(self, name):
        name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
        if name in self.list:
            for idx in range(1, len(self.list)):
                if name == self.list[idx - 1]:
                    return str(idx) + '. '
            
        else:
            return ' '
        return name in self.list


