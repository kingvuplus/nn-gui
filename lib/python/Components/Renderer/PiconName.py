from Components.config import config
from Renderer import Renderer
from enigma import ePixmap, eEnv
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename

class PiconName(Renderer):
    
    def __init__(self):
        Renderer.__init__(self)
        self.path = 'picon'
        self.nameCache = { }
        self.pngname = ''

    
    def applySkin(self, desktop, parent):
        attribs = []
        for None in self.skinAttributes:
            (attrib, value) = None
            if attrib == 'path':
                self.path = value
                continue
            attribs.append((attrib, value))
        self.skinAttributes = attribs
        return Renderer.applySkin(self, desktop, parent)

    GUI_WIDGET = ePixmap
    
    def changed(self, what):
        if self.instance:
            pngname = ''
            if what[0] != self.CHANGED_CLEAR:
                sname = self.source.text.upper()
                sname = sname.replace('\xc2\x86', '').replace('\xc2\x87', '')
                pngname = self.nameCache.get(sname, '')
                if pngname == '':
                    pngname = self.findPicon(sname)
                
            
            if pngname == '':
                pngname = self.nameCache.get('default', '')
                if pngname == '':
                    pngname = self.findPicon('picon_default')
                    if pngname == '':
                        tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
                        if fileExists(tmp):
                            pngname = tmp
                        else:
                            pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
                    
                    self.nameCache['default'] = pngname
                
            
            if self.pngname != pngname:
                self.instance.setPixmapFromFile(pngname)
                self.pngname = pngname
            
        

    
    def findPicon(self, serviceName):
        if config.nemesis.usepiconinhdd.value:
            searchPaths = ('/media/hdd/%s/', eEnv.resolve('${datadir}/%s/'), '/media/cf/%s/', '/media/usb/%s/')
        else:
            searchPaths = (eEnv.resolve('${datadir}/%s/'), '/media/usb/%s/', '/media/cf/%s/')
        for path in searchPaths:
            pngname = path % self.path + serviceName + '.png'
            if fileExists(pngname):
                return pngname
        return ''


