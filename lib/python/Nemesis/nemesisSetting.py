from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap, ActionMap
from Components.config import config, ConfigNothing, ConfigFile
from Components.SystemInfo import SystemInfo
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from nemesisTool import GetSkinPath, createProxy, createInadynConf, createIpupdateConf
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.LoadPixmap import LoadPixmap
from enigma import eTimer
import xml.etree.cElementTree as xml
setupfile = file('/usr/share/enigma2/nemesis.xml', 'r')
setupdom = xml.etree.cElementTree.parse(setupfile)
setupfile.close()
configfile = ConfigFile()

class NSetupSum(Screen):
    skin = '\n\t\t<screen position="80,95" size="560,430" title="Addons">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (50, 5), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=2),\n\t\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget source="conn" Render="Label" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" transparent="1" />\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['title'] = Label(_('System Settings'))
        self['key_red'] = Label(_('Exit'))
        self['conn'] = StaticText('')
        skin_path = GetSkinPath()
        xmldata = setupdom.getroot()
        for x in xmldata.findall('setup'):
            requires = x.get('requires')
            if requires and not SystemInfo.get(requires, False):
                continue
            
            self.list.append((x.get('key'), _(x.get('title', '').encode('UTF-8')), LoadPixmap(skin_path + 'icons/setup.png')))
        self['list'] = List(self.list)
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.okbuttonClick,
            'red': self.close,
            'back': self.close })
        self.activityTimer = eTimer()
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(_('System Settings'))

    
    def okbuttonClick(self):
        self.indice = self['list'].getCurrent()[0]
        self.session.openWithCallback(self.saveConfig, NSetup, self.indice)

    
    def saveConfig(self, *ret):
        if ret:
            self['conn'].text = _('Saving Setting.\nPlease wait...')
            self.activityTimer.timeout.get().append(self.saveConf(ret[0]))
            self.activityTimer.start(100, False)
        

    
    def saveConf(self, ret):
        self.activityTimer.stop()
        if ret == 'proxy':
            createProxy()
        elif ret == 'inadyn':
            createInadynConf()
        elif ret == 'ipupdate':
            createIpupdateConf()
        
        configfile.save()
        self['conn'].text = ''



class NSetup(ConfigListScreen, Screen):
    ALLOW_SUSPEND = True
    skin = '\n\t\t<screen name="NSetup" position="330,130" size="620,500">\n\t\t\t<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="config" position="10,10" size="590,440" scrollbarMode="showOnDemand" />\n\t\t\t<eLabel position="0,459" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="canceltext" position="10,460" zPosition="1" size="300,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />\n\t\t\t<widget name="oktext" position="310,460" zPosition="1" size="300,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />\n\t\t</screen>'
    
    def refill(self, list):
        xmldata = setupdom.getroot()
        for x in xmldata.findall('setup'):
            if x.get('key') != self.setup:
                continue
            
            self.addItems(list, x)
            self.setup_title = _(x.get('title', '').encode('UTF-8'))

    
    def __init__(self, session, setup):
        Screen.__init__(self, session)
        self.onChangedEntry = []
        self.setup_title = ''
        self.setup = setup
        list = []
        self.refill(list)
        self['oktext'] = Label(_('OK'))
        self['canceltext'] = Label(_('Exit'))
        self['actions'] = NumberActionMap([
            'SetupActions'], {
            'cancel': self.keyCancel,
            'save': self.okPress }, -2)
        ConfigListScreen.__init__(self, list, session = session, on_change = self.changedEntry)
        self.changedEntry()
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(_(self.setup_title))

    
    def changedEntry(self):
        for x in self.onChangedEntry:
            x()

    
    def getCurrentEntry(self):
        return self['config'].getCurrent()[0]

    
    def getCurrentValue(self):
        return str(self['config'].getCurrent()[1].getText())

    
    def addItems(self, list, parentNode):
        for x in parentNode:
            if x.tag == 'item':
                item_level = int(x.get('level', 0))
                item_text = _(x.get('text', '??').encode('UTF-8'))
                if not x.text:
                    pass
                item = eval('')
                if item == '':
                    continue
                
                if not isinstance(item, ConfigNothing):
                    list.append((item_text, item))
                
            isinstance(item, ConfigNothing)

    
    def okPress(self):
        self.saveAll()
        self.close(self.setup)


