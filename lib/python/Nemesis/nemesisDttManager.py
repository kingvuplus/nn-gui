from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.Ipkg import Ipkg
from Components.Sources.List import List
from Components.Ipkg import IpkgComponent
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Sources.StaticText import StaticText
from Components.config import config
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from nemesisTool import nemesisTool, GetSkinPath
from nemesisConsole import nemesisConsole
from nemesisTunerList import tList
from enigma import eTimer
from os import path as os_path, listdir, unlink
import os
t = nemesisTool()

def readFile(myFile):
    
    try:
        mounts = open(myFile)
    except IOError:
        return 'None'

    line = mounts.readlines()
    mounts.close()
    return line[0].strip()


def checkDev():
    deviceDir = '/sys/bus/usb/devices/'
    devDir = listdir(deviceDir)
    myDevices = []
    for x in devDir[:]:
        idv = 'None'
        idp = 'None'
        if os_path.isdir(deviceDir + x):
            devFiles = listdir(deviceDir + x)
            for y in devFiles[:]:
                if os_path.isfile(deviceDir + x + '/' + y):
                    if y == 'idVendor':
                        idv = readFile(deviceDir + x + '/' + y)
                    
                    if y == 'idProduct':
                        idp = readFile(deviceDir + x + '/' + y)
                    
                y == 'idProduct'
            myDevices.append('%s:%s' % (idv, idp))
            continue
    if myDevices:
        devicesList = []
        for myDevice in myDevices:
            for myTuner in tList.tunerList:
                if myDevice == myTuner[0]:
                    devicesList.append(myTuner)
                    continue
        if devicesList:
            return devicesList
        return None
    return None


class manageDttDevice(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget source="conn" render=Label position="10,10" size="540,340" font="Regular;20" halign="center" transparent="1" />\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (0, 0), size = (400, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(405, 6), size=(80, 23), png=png),\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 30\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,400" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_yellow" position="400,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.devList = checkDev()
        self.devstatus = { }
        self.needInstall = False
        self.updating = True
        self['list'] = List(self.list)
        self['key_red'] = Label(_('Exit'))
        self['key_yellow'] = Label('')
        self['conn'] = StaticText('')
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'yellow': self.modulesInstall,
            'red': self.exit,
            'back': self.exit })
        self.cmdList = []
        self.ipkg = IpkgComponent()
        self.ipkg.addCallback(self.ipkgCallback)
        self.timeoutTimer = eTimer()
        self.timeoutTimer.callback.append(self.doTimeoutTimer)
        self.onLayoutFinish.append(self.updateList)
        self.onShown.append(self.setWindowTitle)

    
    def exit(self):
        if not self.ipkg.isRunning():
            self.close()
        

    
    def setWindowTitle(self):
        self.setTitle(_('Manage DVB-T/C Adapter'))

    
    def KeyOk(self):
        if self.devList:
            sel = self['list'].getCurrent()[0]
            if sel:
                self.devstatus[sel] = not self.devstatus[sel]
                self.saveStatus()
                self.updateList()
                if self.devstatus[sel]:
                    msg = _('Enigma2 will be now hard restarted to enable DVB/T.please wait\nDo You want restart now?')
                    box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg, MessageBox.TYPE_YESNO)
                    box.setTitle(_('Restart Enigma2'))
                else:
                    msg = _('Dreambox will be now rebooted to disable DVB/T.\nDo You want reboot the box now?')
                    box = self.session.openWithCallback(self.rebootDream, MessageBox, msg, MessageBox.TYPE_YESNO)
                    box.setTitle(_('Reboot Dreambox'))
            
        else:
            self.close()

    
    def restartEnigma2(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        

    
    def rebootDream(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 2)
        

    
    def readStatus(self):
        
        try:
            if self.devList:
                for x in self.devList:
                    self.devstatus[x[1]] = False
                if fileExists('/etc/dtt.devices'):
                    loadedDevices = open('/etc/dtt.devices', 'r')
                    for d in loadedDevices.readlines():
                        for dev in self.devList:
                            if dev[1] == d[:-1]:
                                self.devstatus[dev[1]] = True
                                continue
                    loadedDevices.close()
                
            elif fileExists('/etc/dtt.devices'):
                unlink('/etc/dtt.devices')
            
            return None
        except IOError:
            return None


    
    def saveStatus(self):
        out = open('/etc/dtt.devices', 'w')
        for dev in self.devList:
            if self.devstatus.get(dev[1]):
                out.write(dev[1] + '\n')
                continue
        out.close()

    
    def updateList(self):
        del self.list[:]
        if fileExists('/usr/script/loaddttmodules.sh'):
            self['conn'].text = ''
            self['key_yellow'].setText(_('Remove Driver'))
            self.readStatus()
            self.needInstall = False
            skin_path = GetSkinPath()
            if self.devList:
                for dev in self.devList:
                    res = [
                        dev[1]]
                    png = LoadPixmap({
                        True: skin_path + 'menu/menu_on.png',
                        False: skin_path + 'menu/menu_off.png' }[self.devstatus.get(dev[1])])
                    self.list.append((dev[1], dev[2], png))
                
            
            self['list'].setList(self.list)
        else:
            self.needInstall = True
            self['key_yellow'].setText(_('Install Driver'))
            self.showInstMess()

    
    def showInstMess(self):
        diskSpace = t.getVarSpaceKb()
        percFree = int((diskSpace[0] / diskSpace[1]) * 100)
        strMess = _('Modules for support\nUSB DVB-T/C adapter\nare not installed!\n\nPress yellow button\nto install it.')
        self['conn'].text = '%s\n\nFree: %d kB (%d%%)' % (strMess, int(diskSpace[0]), percFree)

    
    def modulesInstall(self):
        if self.needInstall:
            if int(t.getVarSpaceKb()[0]) < 2500:
                msg = _('Not enough space!\nPlease delete addons before install new.')
                self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
                return None
            self['conn'].setText(_('Connetting to addons server.\nPlease wait...'))
            self.updating = True
            self.timeoutTimer.start(config.nemesis.ipkg.updateTimeout.value * 1000)
            self.ipkg.startCmd(IpkgComponent.CMD_UPDATE)
        else:
            msg = _('Do you want remove the support\npackages, for DVB-T/C adapters?') + _('\nAfter pressing OK, please wait!')
            self.session.openWithCallback(self.runRemove, MessageBox, msg, MessageBox.TYPE_YESNO)

    
    def doTimeoutTimer(self):
        self['conn'].text = _('Server connection timeout!\nPlease try again later.')
        self.ipkg.stop()

    
    def runUpgrade(self, result):
        if result:
            self.session.openWithCallback(self.updateList, Ipkg, cmdList = self.cmdList)
        else:
            self.showInstMess()

    
    def runRemove(self, result):
        if result:
            self.cmdList = []
            self.cmdList.append((IpkgComponent.CMD_REMOVE, {
                'package': 'dreambox-tuner-usb' }))
            if len(self.cmdList):
                self.session.openWithCallback(self.pakageRemoved, Ipkg, cmdList = self.cmdList)
            
        

    
    def pakageRemoved(self):
        self.updateList()
        if fileExists('/etc/dtt.devices'):
            unlink('/etc/dtt.devices')
        
        msg = _('Dreambox will be now rebooted to disable DVB/T.\nDo You want reboot the box now?')
        box = self.session.openWithCallback(self.rebootDream, MessageBox, msg, MessageBox.TYPE_YESNO)
        box.setTitle(_('Reboot Dreambox'))

    
    def ipkgCallback(self, event, param):
        if event == IpkgComponent.EVENT_ERROR:
            self.updating = False
            self['conn'].text = _('Server not found!\nPlease check internet connection.')
        elif event == IpkgComponent.EVENT_DONE:
            if self.timeoutTimer.isActive():
                self.timeoutTimer.stop()
            
            if self.updating:
                self.cmdList = []
                self.cmdList.append((IpkgComponent.CMD_INSTALL, {
                    'package': 'dreambox-tuner-usb' }))
                if len(self.cmdList):
                    self.session.openWithCallback(self.runUpgrade, MessageBox, _('Do you want install the support\npackages, for DVB-T/C adapters?') + _('\nAfter pressing OK, please wait!'), MessageBox.TYPE_YESNO)
                
            
        


