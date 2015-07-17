from Screens.Screen import Screen
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.Console import Console
from Components.FileList import FileList
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, ConfigYesNo, NoSave, config, ConfigFile, ConfigNothing, ConfigSelection
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Sources.StaticText import StaticText
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS
from os import system, remove as os_remove
from nemesisTool import GetSkinPath, nemesisTool
from nemesisConsole import nemesisConsole
from nemesisShowPanel import nemesisShowPanel
from nemesisDeviceManager import manageDevice
from nemesisDttManager import manageDttDevice
from enigma import eTimer
from Tools.HardwareInfo import HardwareInfo
from Components.About import about
KERNELVER = about.getKernelVersionStringL()
isNetworkPlugin = True
if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/plugin.py')):
    
    try:
        from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser
    isNetworkPlugin = False

else:
    isNetworkPlugin = False
t = nemesisTool()
configfile = ConfigFile()

def checkDev():
    
    try:
        mydev = []
        f = open('/proc/mounts', 'r')
        for line in f.readlines():
            if line.find('/cf') != -1:
                mydev.append(('/media/cf/', 'COMPACT FLASH'))
            
            if line.find('/media/usb') != -1:
                mydev.append(('/media/usb/', 'USB PEN'))
            
            if line.find('/hdd') != -1:
                mydev.append(('/media/hdd/', 'HARD DISK'))
                continue
        f.close()
        if mydev:
            return mydev
    except:
        return None



class NUtility(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (50, 2), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=2),\n\t\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 35\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,400" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.menuList = [
            ('Services', _('Start/Stop Services'), 'icons/enigma.png', True),
            ('Module', _('Manage Kernel Modules'), 'icons/module.png', True),
            ('Ssetup', _('Manage Startup Services'), 'icons/log.png', True),
            ('Slog', _('View Services Logs'), 'icons/setup.png', True),
            ('NetBrowser', _('Network Browser'), 'icons/network.png', isNetworkPlugin),
            ('Ccommand', _('Execute commands'), 'icons/terminal.png', True),
            ('NUserScript', _('Execute Users Scripts'), 'icons/user.png', True),
            ('NSwap', _('Manage Swap File'), 'icons/swapsettings.png', True),
            ('NDevice', _('Manage Devices'), 'icons/device.png', True),
            ('DttDevice', _('Manage DVB-T/C Adapter'), 'icons/device.png', True),
            ('Csave', _('Save Enigma Setting'), 'icons/save.png', True)]
        self['title'] = Label(_('System Utility'))
        self['list'] = List(self.list)
        self['key_red'] = Label(_('Exit'))
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'red': self.close,
            'back': self.close })
        self.saveConfTimer = eTimer()
        self.saveConfTimer.timeout.get().append(self.saveConf)
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.updateList)

    
    def setWindowTitle(self):
        self.setTitle(_('System Utility'))

    
    def KeyOk(self):
        self.sel = self['list'].getCurrent()[0]
        if self.sel == 'Services':
            self.session.open(NServices)
        elif self.sel == 'Module':
            self.session.open(NModule)
        elif self.sel == 'DttDevice':
            self.session.open(manageDttDevice)
        elif self.sel == 'Ssetup':
            self.session.open(NServicesSetup)
        elif self.sel == 'Slog':
            self.session.open(NServicesLog)
        elif self.sel == 'Ccommand':
            self.session.open(NCommand)
        elif self.sel == 'NUserScript':
            self.session.open(NUserScript)
        elif self.sel == 'NDevice':
            self.session.open(manageDevice)
        elif self.sel == 'NSwap':
            if checkDev() == None:
                msg = _('No device for swap found!')
                confBox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
                confBox.setTitle(_('Swap Error'))
            else:
                self.session.open(NSwap)
        elif self.sel == 'NetBrowser':
            self.session.open(NetworkBrowser, None, GetSkinPath())
        elif self.sel == 'Csave':
            msg = _('Saving Enigma Setting\nPlease Wait...')
            self.confBox = self.session.open(MessageBox, msg, MessageBox.TYPE_INFO, enable_input = False)
            self.confBox.setTitle(_('Saving'))
            self.saveConfTimer.start(50, False)
        

    
    def saveConf(self):
        self.saveConfTimer.stop()
        configfile.save()
        self.confBox.close()

    
    def updateList(self):
        del self.list[:]
        skin_path = GetSkinPath()
        for men in self.menuList:
            if men[3]:
                self.list.append((men[0], men[1], LoadPixmap(skin_path + men[2])))
                continue
        self['list'].setList(self.list)



class NCommand(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (0, 0), size = (340, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 30\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,400" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_yellow" position="280,400" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['title'] = Label(_('Execute commands'))
        self['list'] = List(self.list)
        self['key_red'] = Label(_('Exit'))
        self['key_yellow'] = Label(_('Custom'))
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'red': self.close,
            'yellow': self.openCustom,
            'back': self.close })
        self.onLayoutFinish.append(self.updateList)
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(_('Execute Commands'))

    
    def KeyOk(self):
        cmd = self['list'].getCurrent()[0]
        self.runCommand(cmd)

    
    def updateList(self):
        del self.list[:]
        if fileExists('/etc/custom_command'):
            f = open('/etc/custom_command', 'r')
            for line in f.readlines():
                a = line.split(':')
                self.list.append((a[1].strip(), a[0].strip()))
            
        else:
            self.list.append(('None', _('File /etc/custom_command  not found!')))
        self['list'].setList(self.list)

    
    def openCustom(self):
        if config.nemesis.usevkeyboard.value:
            self.session.openWithCallback(self.runCommand, VirtualKeyBoard, title = _('Enter command to run:'), text = '')
        else:
            self.session.openWithCallback(self.runCommand, InputBox, title = _('Enter command to run:'), windowTitle = _('Execute Commands'), text = '')

    
    def runCommand(self, cmd):
        if cmd is not None:
            self.session.open(Console, title = _('Execute command: ') + cmd, cmdlist = [
                cmd])
        



class NUserScript(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (0, 0), size = (340, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 30\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,400" size="510,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['title'] = Label(_('Execute Users Scripts'))
        self['list'] = List(self.list)
        self['key_red'] = Label(_('Exit'))
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'red': self.close,
            'back': self.close })
        self.onLayoutFinish.append(self.updateList)
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(_('Execute Users Scripts'))

    
    def KeyOk(self):
        cmd = self['list'].getCurrent()[0]
        if cmd:
            self.runCommand('/usr/script/' + cmd + '_user.sh')
        

    
    def updateList(self):
        del self.list[:]
        filelist = FileList('/usr/script', matchingPattern = '_user.sh')
        for x in filelist.getFileList():
            if x[0][1] != True:
                self.list.append((x[0][0][:-8], t.getScriptName(x[0][0][:-8])))
                continue
        if len(self.list) == 0:
            self.list.append(('None', _('No Users Script Found!')))
        
        self['list'].setList(self.list)

    
    def runCommand(self, cmd):
        if cmd is not None:
            self.session.open(Console, title = _('Execute script: ') + cmd, cmdlist = [
                cmd])
        



class NServices(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (0, 0), size = (400, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(405, 6), size=(80, 23), png=png),\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 30\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,400" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_yellow" position="400,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.servicesList = [
            ('nfs', '/etc/init.d/nfsserver', '[nfsd]', 'NFS Server'),
            ('smb', '/etc/init.d/samba', '/usr/sbin/smbd', 'Samba'),
            ('autofs', '/etc/init.d/autofs', '/usr/sbin/automount', 'Automount'),
            ('vpn', '/etc/init.d/openvpn', '/usr/sbin/openvpn', 'OpenVPN'),
            ('ipudate', '/etc/init.d/ipupdate', '/usr/bin/ez-ipupdate', 'IpUpdate'),
            ('inadyn', '/etc/init.d/inadyn', 'inadyn', 'InaDyn'),
            ('sshd', '/etc/init.d/sshd', 'sshd', 'Openssh (SSHD)'),
            ('vsftpd', '/etc/init.d/vsftpd', '/usr/sbin/vsftpd', 'FTP Server'),
            ('crond', '/etc/init.d/busybox-cron', '/usr/sbin/crond', 'Crontab'),
            ('pcscd', '/etc/init.d/pcscd', '/usr/sbin/pcscd', 'Omnikey Smart Card')]
        self.servicestatus = { }
        self['title'] = Label(_('Manage Services'))
        self['key_red'] = Label(_('Exit'))
        self['key_yellow'] = Label(_('Setup'))
        self['list'] = List(self.list)
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'yellow': self.openSetting,
            'red': self.close,
            'back': self.close })
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.updateList)

    
    def setWindowTitle(self):
        self.setTitle(_('Manage services'))

    
    def openSetting(self):
        self.session.open(NServicesSetup)

    
    def KeyOk(self):
        ser = self['list'].getCurrent()[0]
        if ser:
            for s in self.servicesList:
                if s[0] == ser:
                    cmd = {
                        True: s[1] + ' stop',
                        False: s[1] + ' start' }[self.servicestatus.get(s[0])]
                    continue
            self.session.openWithCallback(self.executedScript, nemesisConsole, cmd, _('Execute command: ') + cmd)
        

    
    def executedScript(self, *answer):
        self.updateList()

    
    def readStatus(self):
        for ser in self.servicesList:
            self.servicestatus[ser[0]] = False
        system('ps -ef > /tmp/status.log')
        f = open('/tmp/status.log', 'r')
        for line in f.readlines():
            for ser in self.servicesList:
                if line.find(ser[2]) != -1:
                    self.servicestatus[ser[0]] = True
                    continue
        f.close()

    
    def updateList(self):
        self.readStatus()
        del self.list[:]
        skin_path = GetSkinPath() + 'menu/'
        for ser in self.servicesList:
            png = LoadPixmap({
                True: skin_path + 'menu_on.png',
                False: skin_path + 'menu_off.png' }[self.servicestatus.get(ser[0])])
            self.list.append((ser[0], {
                False: _('Start'),
                True: _('Stop') }[self.servicestatus.get(ser[0])] + ' ' + ser[3], png))
        self['list'].setList(self.list)



class NModule(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (0, 0), size = (400, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(405, 6), size=(80, 23), png=png),\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 30Label\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,400" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.modules = [
            ('usbhid', 'USB Human Int. Device', True),
            ('ftdi_sio', 'USB Serial (FTDI Smargo)', True),
            ('pl2303', 'USB Serial (PL2303)', True),
            ('tun', 'TUN (OpenVPN)', True),
            ('rt73', 'WLAN Usb Adapter RT73', fileExists('/lib/modules/%s/kernel/drivers/net/rt73.ko' % KERNELVER)),
            ('zd1211b', 'WLAN Usb Adapter ZD1211B', fileExists('/lib/modules/%s/kernel/drivers/net/zd1211b.ko' % KERNELVER)),
            ('rtl8187', 'WLAN Usb Adapter RTL8187L', fileExists('/lib/modules/%s/kernel/drivers/net/rtl8187.ko' % KERNELVER)),
            ('rt3070', 'WLAN Usb Adapter RT3070', fileExists('/lib/modules/%s/drivers/net/wireless/rt3070sta.ko' % KERNELVER)),
            ('8712u', 'WLAN Usb Adapter R8712U', fileExists('/lib/modules/%s/extra/8712u.ko' % KERNELVER)),
            ('isofs', 'ISOFS (CD/DVD)', fileExists('/lib/modules/%s/kernel/fs/isofs/isofs.ko' % KERNELVER)),
            ('udf', 'UDF (CD/DVD)', fileExists('/lib/modules/%s/kernel/fs/udf/udf.ko' % KERNELVER)),
            ('cdfs', 'CDFS (Audio-CD)', fileExists('/lib/modules/%s/extra/cdfs.ko' % KERNELVER)),
            ('ntfs', 'NTFS (Windows)', True),
            ('smbfs', 'SMBFS (Windows)', True)]
        self.modstatus = { }
        self.list = []
        self['title'] = Label(_('Manage Modules'))
        self['key_red'] = Label(_('Exit'))
        self['list'] = List(self.list)
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'red': self.close,
            'back': self.close })
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.updateList)

    
    def setWindowTitle(self):
        self.setTitle(_('Manage Modules'))

    
    def KeyOk(self):
        sel = self['list'].getCurrent()[0]
        if sel:
            cmd = 'modprobe ' + {
                True: '-rv ',
                False: '-v ' }[self.modstatus.get(sel)] + sel
            self.session.openWithCallback(self.executedScript, nemesisConsole, cmd, _('Execute command: ') + sel)
        

    
    def executedScript(self, *answer):
        self.updateList()

    
    def saveStatus(self):
        out = open('/etc/nemesis.modules', 'w')
        for mod in self.modules:
            if self.modstatus.get(mod[0]):
                out.write(mod[0] + '\n')
                continue
        out.close()

    
    def readStatus(self):
        for mod in self.modules:
            self.modstatus[mod[0]] = False
        system('lsmod > /tmp/status.log')
        f = open('/tmp/status.log', 'r')
        for line in f.readlines():
            for mod in self.modules:
                if line.find(mod[0]) != -1:
                    self.modstatus[mod[0]] = True
                    continue
        f.close()
        self.saveStatus()

    
    def updateList(self):
        self.readStatus()
        del self.list[:]
        skin_path = GetSkinPath()
        for mod in self.modules:
            if mod[2]:
                png = LoadPixmap({
                    True: skin_path + 'menu/menu_on.png',
                    False: skin_path + 'menu/menu_off.png' }[self.modstatus.get(mod[0])])
                self.list.append((mod[0], mod[1], png))
                continue
        self['list'].setList(self.list)



class NServicesSetup(Screen, ConfigListScreen):
    __module__ = __name__
    skin = '\n\t\t<screen position="330,160" size="620,440">\n\t\t\t<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="config" position="20,20" size="580,330" scrollbarMode="showOnDemand" />\n\t\t\t<widget source="conn" render="Label" position="20,350" size="580,30" font="Regular;20" halign="center" valign="center"  foregroundColor="#ffffff" transparent="1" />\n\t\t\t<eLabel position="0,399" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="canceltext" position="20,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />\n\t\t\t<widget name="oktext" position="310,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.initPath = [
            '/etc/rc2.d',
            '/etc/rc3.d',
            '/etc/rc4.d',
            '/etc/rc5.d']
        self.servicesList = [
            ('nfsserver', 'S20nfsserver', _('Activate NFS Server at boot?')),
            ('samba', 'S20samba', _('Activate Samba Server at boot?')),
            ('autofs', 'S21autofs', _('Activate Automount at boot?')),
            ('openvpn', 'S30openvpn', _('Activate OpenVPN at boot?')),
            ('ipupdate', 'S20ipupdate', _('Activate IpUpdate at boot?')),
            ('inadyn', 'S30inadyn', _('Activate InaDyn at boot?')),
            ('sshd', 'S09sshd', _('Activate Openssh (SSHD) at boot?')),
            ('vsftpd', 'S20vsftpd', _('Activate FTP Server at boot?')),
            ('busybox-cron', 'S21cron', _('Activate Crontab at boot?')),
            ('pcscd', 'S19pcscd', _('Activate Omnikey Support at boot?'))]
        self.serviceconfig = { }
        ConfigListScreen.__init__(self, self.list)
        self['oktext'] = Label(_('OK'))
        self['canceltext'] = Label(_('Exit'))
        self['conn'] = StaticText('')
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'red': self.close,
            'back': self.close,
            'green': self.saveSetting })
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.loadSetting)

    
    def setWindowTitle(self):
        self.setTitle(_('Manage Startup Services'))

    
    def loadSetting(self):
        del self.list[:]
        for s in self.servicesList:
            self.serviceconfig[s[0]] = NoSave(ConfigYesNo(default = False))
            self.list.append(getConfigListEntry(s[2], self.serviceconfig[s[0]]))
            if fileExists('/etc/rc3.d/' + s[1]):
                self.serviceconfig[s[0]].value = True
            
            self['config'].list = self.list
            self['config'].l.setList(self.list)

    
    def saveSetting(self):
        self['conn'].text = _('Saving Setting. Please wait...')
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.saveConf)
        self.activityTimer.start(300, False)

    
    def saveConf(self):
        self.activityTimer.stop()
        for p in self.initPath:
            for s in self.servicesList:
                system({
                    True: 'ln -s ../init.d/%s %s/%s' % (s[0], p, s[1]),
                    False: 'rm -f %s/%s' % (p, s[1]) }[self.serviceconfig[s[0]].value])
        self.close()



class NServicesLog(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430" title="Addons">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (50, 2), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=2),\n\t\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 35\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_yellow" position="280,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.logsList = [
            ('inadyn', config.inadyn.log.value.strip() + '/inadyn.log', _('Show InaDyn Log')),
            ('smb', '/var/log/log.smbd', _('Show SMB Server Log')),
            ('nmb', '/var/log/log.nmbd', _('Show NMB Log')),
            ('vsftpd', '/var/log/vsftpd.log', _('Show FTP Server Log')),
            ('openvpn', '/etc/openvpn/openvpn.log', _('Show OpenVPN Log'))]
        self['title'] = Label(_('Services Logs'))
        self['list'] = List(self.list)
        self['key_red'] = Label(_('Exit'))
        self['key_yellow'] = Label(_('Clear log'))
        self.updateList()
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'yellow': self.deleteLog,
            'red': self.close,
            'back': self.close })
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(_('Services Logs'))

    
    def KeyOk(self):
        log = self['list'].getCurrent()[0]
        if log:
            for l in self.logsList:
                if l[0] == log:
                    cmd = l
                    continue
            self.session.open(nemesisShowPanel, cmd[1], cmd[0] + _(' logged info'))
        

    
    def deleteLog(self):
        self.session.open(deleteLog)

    
    def updateList(self):
        del self.list[:]
        skin_path = GetSkinPath()
        for log in self.logsList:
            self.list.append((log[0], log[2], LoadPixmap(skin_path + 'icons/log.png')))
        self['list'].setList(self.list)



class deleteLog(Screen, ConfigListScreen):
    __module__ = __name__
    skin = '\n\t\t<screen position="330,160" size="620,440" title="Delete log files">\n\t\t\t<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="config" position="20,20" size="580,330" scrollbarMode="showOnDemand" />\n\t\t\t<widget source="conn" render="Label" position="20,350" size="580,30" font="Regular;20" halign="center" valign="center" foregroundColor="#ffffff" transparent="1" />\n\t\t\t<eLabel position="0,399" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="canceltext" position="20,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />\n\t\t\t<widget name="oktext" position="310,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.logsList = [
            ('inadyn', config.inadyn.log.value.strip() + '/inadyn.log', _('Delete InaDyn log file?')),
            ('smb', '/var/log/log.smbd', _('Delete SMB log file?')),
            ('nmb', '/var/log/log.nmbd', _('Delete NMB log file?')),
            ('vsftpd', '/var/log/vsftpd.log', _('Delete FTP log file?')),
            ('openvpn', '/etc/openvpn/openvpn.log', _('Delete OpenVPN log file?')),
            ('enigma', '/hdd/*.log', _('Delete Enigma Crash log file?'))]
        self.logconfig = { }
        ConfigListScreen.__init__(self, self.list)
        self['oktext'] = Label(_('Delete'))
        self['canceltext'] = Label(_('Exit'))
        self['conn'] = StaticText('')
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'red': self.close,
            'back': self.close,
            'green': self.delLog })
        self.onShown.append(self.setWindowTitle)
        self.onLayoutFinish.append(self.loadSetting)

    
    def setWindowTitle(self):
        self.setTitle(_('Delete Log Files'))

    
    def loadSetting(self):
        del self.list[:]
        for l in self.logsList:
            self.logconfig[l[0]] = NoSave(ConfigYesNo(default = False))
            self.list.append(getConfigListEntry(l[2], self.logconfig[l[0]]))
            self['config'].list = self.list
            self['config'].l.setList(self.list)

    
    def delLog(self):
        self['conn'].text = _('Deleting log files. Please wait...')
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.DLog)
        self.activityTimer.start(300, False)

    
    def DLog(self):
        self.activityTimer.stop()
        for l in self.logsList:
            if self.logconfig[l[0]].value:
                system('rm -f ' + l[1])
                continue
        self.close()



class NSwap(Screen, ConfigListScreen):
    __module__ = __name__
    skin = '\n\t\t<screen position="330,160" size="620,440">\n\t\t\t<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="config" position="20,20" size="580,330" scrollbarMode="showOnDemand" />\n\t\t\t<widget source="conn" render="Label" position="20,350" size="580,30" font="Regular;20" halign="center" valign="center"  foregroundColor="#ffffff" transparent="1" />\n\t\t\t<eLabel position="0,399" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="canceltext" position="20,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />\n\t\t\t<widget name="oktext" position="310,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['oktext'] = Label(_('Save'))
        self['canceltext'] = Label(_('Exit'))
        self['conn'] = StaticText('')
        self.active = False
        self.loc = ''
        self.size = 0
        self.activityTimer = eTimer()
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'red': self.close,
            'back': self.close,
            'green': self.saveSwap })
        self.loadSetting()
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(_('Manage Swap File'))

    
    def loadSetting(self):
        self.mydev = checkDev()
        mystat = self.findSwap()
        del self.list[:]
        self.loc = self.mydev[0][0]
        self.size = 32768
        if mystat != None:
            self.active = True
            self.loc = mystat[0]
            self.size = mystat[1] + 8
        
        self.swap_active = NoSave(ConfigYesNo(default = self.active))
        self.list.append(getConfigListEntry(_('Activate Swap File?'), self.swap_active))
        self.swap_size = NoSave(ConfigSelection(default = self.size, choices = [
            (8192, '8 MB'),
            (16384, '16 MB'),
            (32768, '32 MB'),
            (65536, '64 MB'),
            (131072, '128 MB'),
            (262144, '256 MB')]))
        self.list.append(getConfigListEntry(_('Swap file size'), self.swap_size))
        self.swap_location = NoSave(ConfigSelection(default = self.loc, choices = self.mydev))
        self.list.append(getConfigListEntry(_('Swap file location'), self.swap_location))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    
    def saveSwap(self):
        self['conn'].text = _('Saving swap config. Please wait...')
        self.activityTimer.timeout.get().append(self.Dsave)
        self.activityTimer.start(500, False)

    
    def Dsave(self):
        self.activityTimer.stop()
        swapfile = self.swap_location.value.strip() + 'swapfile'
        cmd = ''
        if self.swap_active.value and not (self.active):
            cmd += "echo 'Creating swap file...'"
            cmd += ' && '
            cmd += 'dd if=/dev/zero of=' + swapfile + ' bs=1024 count=' + str(self.swap_size.value)
            cmd += ' && '
            cmd += "echo 'Creating swap device...'"
            cmd += ' && '
            cmd += 'mkswap ' + swapfile
            cmd += ' && '
            cmd += "echo 'Activating swap device...'"
            cmd += ' && '
            cmd += 'swapon ' + swapfile
            self.session.openWithCallback(self.scriptReturn, nemesisConsole, cmd, _('Creating Swap file...'))
        elif not (self.swap_active.value) and self.active:
            cmd += "echo 'Dectivating swap device...'"
            cmd += ' && '
            cmd += 'swapoff ' + swapfile
            cmd += ' && '
            cmd += "echo 'Removing swap file...'"
            cmd += ' && '
            cmd += 'rm -f ' + swapfile
            self.session.openWithCallback(self.scriptReturn, nemesisConsole, cmd, _('Deleting Swap file...'))
        else:
            self['conn'].text = _('Nothing to do!')

    
    def scriptReturn(self, *answer):
        if answer[0] == nemesisConsole.EVENT_DONE:
            self['conn'].text = _('Swap process completed successfully!')
        else:
            self['conn'].text = _('Swap process killed by user!')
        self.loadSetting()

    
    def findSwap(self):
        
        try:
            myswap = []
            f = open('/proc/swaps', 'r')
            for line in f.readlines():
                if line.find('/swapfile') != -1:
                    myswap = line.strip().split()
                    continue
            f.close()
            if myswap:
                return ('/media/' + myswap[0].split('/')[2] + '/', int(myswap[2]))
        except:
            return None



