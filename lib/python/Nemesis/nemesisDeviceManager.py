from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Harddisk import harddiskmanager
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Tools.LoadPixmap import LoadPixmap
from Components.config import getConfigListEntry, config, ConfigFile
from Components.ConfigList import ConfigListScreen
from nemesisTool import ListboxE1, GetSkinPath
from nemesisConsole import nemesisConsole
from nemesisSetting import NSetup
from os import path, statvfs
import os
configfile = ConfigFile()
mScript = '/usr/script/format_utils.sh'

def getMountPoint(dev):
    
    try:
        mounts = open('/proc/mounts')
    except IOError:
        return 'None'

    lines = mounts.readlines()
    mounts.close()
    for line in lines:
        if line.startswith('/dev/%s' % dev):
            return line.strip().split(' ')[1]
    return 'None'


def getUnit(val):
    if val == -1:
        return 'None'
    if val >= 1024:
        return '%.1f%s' % (float(val) / 1024, ' GB')
    return '%.1f%s' % (float(val), ' MB')


def free(dev_path):
    
    try:
        mounts = open('/proc/mounts')
    except IOError:
        return -1

    lines = mounts.readlines()
    mounts.close()
    for line in lines:
        parts = line.strip().split(' ')
        if path.realpath(parts[0]).startswith(dev_path):
            
            try:
                stat = statvfs(parts[1])
            except OSError:
                continue

            return (stat.f_bfree / 1024) * stat.f_bsize / 1024
    return -1


def readFile(filename):
    
    try:
        file = open(filename)
    except IOError:
        return _('File :%s\nnot Found!') % filename

    data = ''
    for line in file.readlines():
        data += line.strip() + '\n'
    file.close()
    return data


class HDDSetup(ConfigListScreen, Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="330,160" size="620,440">\n\t\t\t<eLabel position="0,0" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="config" position="20,20" size="580,330" scrollbarMode="showOnDemand" />\n\t\t\t<widget source="conn" render="Label" position="20,350" size="580,30" font="Regular;20" halign="center" valign="center"  foregroundColor="#ffffff" transparent="1" />\n\t\t\t<eLabel position="0,399" size="620,2" backgroundColor="grey" zPosition="5"/>\n\t\t\t<widget name="canceltext" position="20,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="red" transparent="1" />\n\t\t\t<widget name="oktext" position="310,400" zPosition="1" size="290,40" font="Regular;20" halign="center" valign="center" foregroundColor="green" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.list.append(getConfigListEntry(_('Timeout Harddisk in min:'), config.usage.hdd_standby))
        self.list.append(getConfigListEntry(_('Acoustics Harddisk:'), config.usage.hdd_acoustics))
        self.list.append(getConfigListEntry(_('Enable/Disable UDMA'), config.usage.hdd_udma))
        ConfigListScreen.__init__(self, self.list)
        self['oktext'] = Label(_('OK'))
        self['canceltext'] = Label(_('Exit'))
        self['conn'] = StaticText(_('Status: HDD is active'))
        l = os.popen('hdparm -C /dev/sda', 'r').readlines()
        if l[2].find('standby') != -1:
            self['conn'].text = _('Status: HDD is in Standby')
        
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'red': self.close,
            'back': self.close,
            'green': self.saveSetting })
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(_('Hard Disk Setup'))

    
    def saveSetting(self):
        for hdd in harddiskmanager.HDDList():
            hdd[1].setIdleTime(int(config.usage.hdd_standby.value))
        cmd = "echo 'Setting HDD Parameter'"
        cmd += 'hdparm -M%s' % str(config.usage.hdd_acoustics.value)
        cmd += ' /dev/sda\n\n'
        if config.usage.hdd_udma.value:
            cmd += 'hdparm -X66 /dev/sda\n\n'
        
        self.autoClose = config.nemesis.autocloseconsole.value
        config.nemesis.autocloseconsole.value = False
        self.session.openWithCallback(self.consoleCallback, nemesisConsole, cmd, _('Saving HDD Configuration..'))

    
    def consoleCallback(self, answer):
        if self.autoClose:
            config.nemesis.autocloseconsole.value = True
        
        configfile.save()
        self.close()



class HDDInfo(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (0, 0), size = (340, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 30\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.menuList = [
            ('CID', _('Current Information'), 'hdparm -I /dev/sda', True),
            ('DTI', _('HDD Temperature'), 'hddtemp PATA:/dev/sda', False),
            ('STOP', _('Stop Hard Disk'), 'hdparm -y /dev/sda', False),
            ('PCR', _('Execute cache read test'), 'hdparm -T /dev/sda', False),
            ('PDR', _('Execute device read test'), 'hdparm -t /dev/sda', False),
            ('UDL', _('Update device list (hddtemp.db)'), 'wget http://www.guzu.net/linux/hddtemp.db -O /var/etc/hddtemp.db', False),
            ('FSCK', _('File System Check'), '/usr/script/format_utils.sh hdd_filecheck', False)]
        self['title'] = Label(_('Hard Disk Informations'))
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
        self.setTitle(_('Hard Disk Informations'))

    
    def updateList(self):
        del self.list[:]
        for men in self.menuList:
            self.list.append((men[0], men[1]))
        self['list'].setList(self.list)

    
    def KeyOk(self):
        if self['list'].getCurrent()[0]:
            for men in self.menuList:
                if men[0] == self['list'].getCurrent()[0]:
                    if men[0] == 'STOP':
                        os.system(men[2])
                        continue
                    else:
                        self.autoClose = config.nemesis.autocloseconsole.value
                        config.nemesis.autocloseconsole.value = False
                        self.session.openWithCallback(self.consoleCallback, nemesisConsole, men[2], men[1], men[3])
                    continue
                men[0] == 'STOP'
            
        

    
    def consoleCallback(self, answer):
        if self.autoClose:
            config.nemesis.autocloseconsole.value = True
        



class USBSetup(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,540">\n\t\t\t<widget name="model" position="10,10" size="540,200" font="Regular;22" foregroundColor="yellow" backgroundColor="transpBlack" transparent="1"/>\n\t\t\t<widget source="list" render="Listbox" position="10,220" size="540,300" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (0, 0), size = (340, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 30\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session, sel):
        Screen.__init__(self, session)
        self.hostID = {
            'USB0': 'b',
            'USB1': 'c',
            'USB2': 'd',
            'USB3': 'e',
            'USB4': 'f' }[sel]
        self.host = 'sd%s' % self.hostID
        self.list = []
        self['title'] = Label(_('USB-Pen Setup') + ' (%s)' % self.host)
        self['model'] = Label('')
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
        self.setTitle(_('USB-Pen Setup') + ' (%s)' % self.host)

    
    def updateList(self):
        mountPoint = getMountPoint(self.host)
        mountPointNew = mountPoint
        mountCmd = ''
        isMounted = True
        if mountPoint == 'None':
            if os.path.exists('/dev/sdb'):
                mountPointNew = '/media/usb%s' % {
                    'b': '',
                    'c': '1',
                    'd': '2',
                    'e': '3',
                    'f': '4' }[self.hostID]
            else:
                mountPointNew = '/media/usb%s' % {
                    'b': '',
                    'c': '',
                    'd': '2',
                    'e': '3',
                    'f': '4' }[self.hostID]
            isMounted = False
        
        check_umount = {
            False: '0',
            True: '1' }[isMounted]
        force_umount = {
            False: '0',
            True: '1' }[config.nemesis.forceumount.value]
        if os.path.exists('/dev/%s1' % self.host):
            mountCmd = 'mount /dev/%s1 %s' % (self.host, mountPointNew)
        else:
            mountCmd = 'mount /dev/%s %s' % (self.host, mountPointNew)
        self.menuList = [
            ('FA', _('Format USB-Pen (auto)'), '%s %s %s %s %s %s' % (mScript, 'usb_auto', self.host, mountPointNew, check_umount, force_umount), True, True),
            ('FP', _('Format USB-Pen (part1)'), '%s %s %s %s %s %s' % (mScript, 'usb_part1', self.host, mountPointNew, check_umount, force_umount), True, True),
            ('FD', _('Format USB-Pen (disk)'), '%s %s %s %s %s %s' % (mScript, 'usb_disc', self.host, mountPointNew, check_umount, force_umount), True, True),
            ('FSCK', _('File System Check'), '%s %s %s %s %s %s' % (mScript, 'usb_filecheck', self.host, mountPointNew, check_umount, force_umount), False, True),
            ('MOUNT', _('Mount'), mountCmd, False, not isMounted),
            ('UMOUNT', _('Umount'), 'umount %s' % mountPoint, False, isMounted)]
        dev_info = 'Free space: %s\n' % getUnit(free('/dev/%s' % self.host))
        dev_info += 'Mount point: %s\n' % mountPoint
        dev_info += readFile('/proc/scsi/usb-storage/%s' % {
            'b': '1',
            'c': '2',
            'd': '3',
            'e': '4',
            'f': '5' }[self.hostID])
        self['model'].setText(dev_info)
        del self.list[:]
        for men in self.menuList:
            if men[4]:
                self.list.append((men[0], men[1]))
                continue
        self['list'].setList(self.list)

    
    def KeyOk(self):
        self.res = self['list'].getCurrent()[0]
        if self.res:
            if self.res == 'MOUNT' or self.res == 'UMOUNT':
                self.execCommand()
            elif config.nemesis.forceumount.value:
                msg = _('Force Umount is Enabled!\nIf you continue your system may become instable.\nDo you want continue?')
                box = self.session.openWithCallback(self.msgAnswer, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle(_('Confirm Format'))
            elif self.res != 'FSCK':
                msg = _('Format device, will erase all data permanently!\nDo you want continue?')
                box = self.session.openWithCallback(self.msgAnswer, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle(_('Confirm Format'))
            
        

    
    def msgAnswer(self, answer):
        if answer is True:
            self.execCommand()
        

    
    def execCommand(self):
        for men in self.menuList:
            if men[0] == self.res:
                self.autoClose = config.nemesis.autocloseconsole.value
                config.nemesis.autocloseconsole.value = False
                self.session.openWithCallback(self.consoleCallback, nemesisConsole, men[2], men[1], men[3])
                continue
                continue

    
    def consoleCallback(self, answer):
        if self.autoClose:
            config.nemesis.autocloseconsole.value = True
        
        self.updateList()



class CFSetup(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>\n\t\t\t<widget name="list" position="10,10" size="540,340" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.menuList = [
            ('FA', _('Format CF-Card (Auto)'), '%s %s' % (mScript, 'cf_auto'), False),
            ('FP', _('Format CF-Card (part1)'), '%s %s' % (mScript, 'cf_part1'), False),
            ('FD', _('Format CF-Card (disk)'), '%s %s' % (mScript, 'cf_disc'), False),
            ('FSCK', _('File System Check'), '%s %s' % (mScript, 'cf_filecheck'), False)]
        self['title'] = Label(_('CF-Card Setup'))
        self['list'] = ListboxE1(self.list)
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
        self.setTitle(_('CF-Card Setup'))

    
    def updateList(self):
        del self.list[:]
        for men in self.menuList:
            res = [
                men[0]]
            res.append(MultiContentEntryText(pos = (0, 0), size = (340, 25), font = 0, text = men[1]))
            self.list.append(res)
        self['list'].l.setList(self.list)

    
    def KeyOk(self):
        if self['list'].getCurrent()[0]:
            for men in self.menuList:
                if men[0] == self['list'].getCurrent()[0]:
                    self.autoClose = config.nemesis.autocloseconsole.value
                    config.nemesis.autocloseconsole.value = False
                    self.session.openWithCallback(self.consoleCallback, nemesisConsole, men[2], men[1], men[3])
                    continue
                    continue
            
        

    
    def consoleCallback(self, answer):
        if self.autoClose:
            config.nemesis.autocloseconsole.value = True
        



def checkDev():
    
    try:
        mydev = []
        if os.path.exists('/dev/sda'):
            mydev.append(('HDI', _('Hard Disk Informations'), 'icons/space.png'))
            mydev.append(('HDS', _('Hard Disk Setup'), 'icons/space.png'))
        
        if os.path.exists('/dev/sdb'):
            mydev.append(('USB0', _('USB-Pen Setup') + ' (sdb)', 'icons/usb.png'))
        
        if os.path.exists('/dev/sdc'):
            mydev.append(('USB1', _('USB-Pen Setup') + ' (sdc)', 'icons/usb.png'))
        
        if os.path.exists('/dev/sdd'):
            mydev.append(('USB2', _('USB-Pen Setup') + ' (sdd)', 'icons/usb.png'))
        
        if os.path.exists('/dev/sde'):
            mydev.append(('USB3', _('USB-Pen Setup') + ' (sde)', 'icons/usb.png'))
        
        if os.path.exists('/dev/sdf'):
            mydev.append(('USB4', _('USB-Pen Setup') + ' (sdf)', 'icons/usb.png'))
        
        if os.path.exists('/dev/ide/host1/bus0/target0/lun0/disc'):
            mydev.append(('CF', _('CF-Card Setup'), 'icons/cf.png'))
        
        mydev.append(('configDEV', _('Setup'), 'icons/setup.png'))
        if mydev:
            return mydev
        return None
    except:
        return None



class manageDevice(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (50, 2), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=2),\n\t\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 35\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.menuList = checkDev()
        self['title'] = Label(_('Manage Devices'))
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
        self.setTitle(_('Manage Devices'))

    
    def KeyOk(self):
        sel = self['list'].getCurrent()[0]
        if sel:
            if sel == 'HDI':
                self.session.open(HDDInfo)
            elif sel == 'HDS':
                self.session.open(HDDSetup)
            elif sel == 'USB0' and sel == 'USB1' and sel == 'USB2' and sel == 'USB3' or sel == 'USB4':
                self.session.open(USBSetup, sel)
            elif sel == 'CF':
                self.session.open(CFSetup)
            elif sel == 'configDEV':
                self.session.openWithCallback(self.saveConfig, NSetup, 'dev')
            
        

    
    def saveConfig(self, *answer):
        if answer:
            configfile.save()
        

    
    def updateList(self):
        del self.list[:]
        skin_path = GetSkinPath()
        if self.menuList != None:
            for men in self.menuList:
                self.list.append((men[0], men[1], LoadPixmap(skin_path + men[2])))
            self['list'].setList(self.list)
        


