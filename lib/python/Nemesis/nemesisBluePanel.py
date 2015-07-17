from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ParentalControlSetup import ParentalControlSetup
from Screens.PluginBrowser import PluginBrowser
from Components.ActionMap import ActionMap, NumberActionMap
from Components.FileList import FileList
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.ConfigList import ConfigList
from Components.config import ConfigSelection, getConfigListEntry, ConfigNothing, KEY_LEFT, KEY_RIGHT, KEY_OK
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Tools.Directories import fileExists
from Tools.HardwareInfo import HardwareInfo
from nemesisTool import *
from nemesisShowPanel import nemesisShowPanel
from nemesisConsole import nemesisConsole
from nemesisInfo import NInfo
from nemesisUtility import NUtility
from nemesisSetting import NSetupSum
from nemesisAddons import NAddons
from Components.Console import Console
from Components.About import about
import os
from os import unlink
from enigma import eTimer, eDVBCI_UI, nemTool, iServiceInformation, eConsoleAppContainer
t = nemesisTool()
tool = nemTool()

class nemesisBluePanel(Screen):
    skin = '\n\t<screen name="nemesisBluePanel" position="center,130" size="800,500">\n\t\t<widget name="info_use" position="30,10" zPosition="2" size="360,30" halign="center" font="Prive2;20" foregroundColor="unb2e0b4" />\n\t\t<widget name="config" position="30,50" size="360,150" zPosition="2" transparent="1" foregroundColor="unb2e0b4" />\n\t\t<widget name="conn" position="30,200" size="360,140" font="Prive2;20" halign="center" valign="center" zPosition="2" foregroundColor="red" />\n\t\t<widget source="conninfo" render="Label" position="30,340" size="740,30" font="Prive2;18" halign="center" valign="center" foregroundColor="conncol" transparent="1" />\n\t\t<ePixmap pixmap="skin_default/buttons/select_p.png" position="43,380" size="335,44" zPosition="1" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/select_p.png" position="422,380" size="335,44" zPosition="1" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/select_p.png" position="43,440" size="335,44" zPosition="1" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/select_p.png" position="422,440" size="335,44" zPosition="1" alphatest="on" />\n\t\t<widget name="key_red" position="43,380" size="335,44" font="Prive2;22" valign="center" halign="center" foregroundColor="red" zPosition="2" transparent="1" />\n\t\t<widget name="key_green" position="43,440" size="335,44" font="Prive2;22" valign="center" halign="center" foregroundColor="green" zPosition="2" transparent="1" />\n\t\t<widget name="key_yellow" position="422,380" size="335,44" font="Prive2;22" valign="center" halign="center" foregroundColor="yellow" zPosition="2" transparent="1" />\n\t\t<widget name="key_blue" position="422,440" size="335,44" font="Prive2;22" valign="center" halign="center" foregroundColor="blue" zPosition="2" transparent="1" />\n\t\t<ePixmap position="43,164" size="355,206" pixmap="skin_default/menu/box-2.png" zPosition="1" alphatest="blend" />\n\t\t<eLabel text="Emu decode info:" position="422,10" size="335,30" halign="center" font="Prive2;20" foregroundColor="unb2e0b4" />\n\t\t<widget position="422,48" size="335,25" source="session.CurrentService" render="Label" font="Prive2;20" valign="bottom" halign="center" noWrap="1" foregroundColor="unb2e0b4">\n\t\t\t<convert type="ServiceName">Name</convert>\n\t\t</widget>\n\t\t<widget source="session.CurrentService" render="Label" position="422,74" size="335,25" font="Prive2;19" halign="center" foregroundColor="unb2e0b4">\n\t\t\t<convert type="ServiceName">Provider</convert>\n\t\t</widget>\n\t\t<widget name="ecmtext" position="407,118" size="392,230" font="Prive2;19" zPosition="2" halign="center" foregroundColor="un99bad6" />\n\t</screen>'
    NEMESISVER = '2.3'
    OEVER = '1.6'
    IMAGEVER = about.getImageVersionString()
    ENIGMAVER = about.getEnigmaVersionString()
    KERNELVER = about.getKernelVersionStringL()
    SVNVERSION = about.getSvnVersionString()
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['config'] = ConfigList(self.list)
        self['title'] = Label(_('Nemesis Blue Panel'))
        self['ecmtext'] = ScrollLabel('')
        self['conninfo'] = StaticText('')
        self['conn'] = Label('')
        self['conn'].hide()
        self['key_blue'] = Label(_('Addons Manager'))
        self['key_yellow'] = Label(_('System Settings'))
        self['key_green'] = Label(_('System Information'))
        self['key_red'] = Label(_('System Utility'))
        self['info_use'] = Label(_('Use arrows < > to select'))
        self['actions'] = NumberActionMap([
            'ColorActions',
            'CiSelectionActions',
            'WizardActions',
            'SetupActions'], {
            'left': self.keyLeft,
            'right': self.keyRight,
            'blue': self.naddons,
            'green': self.ninfo,
            'yellow': self.nsetting,
            'red': self.nutility,
            'ok': self.ok_pressed,
            'back': self._nemesisBluePanel__onClose }, -1)
        self.console = Console()
        self.nemPortNumber = t.readPortNumber()
        self.checkVersionTimer = eTimer()
        self.checkVersionTimer.timeout.get().append(self.checkVersion)
        self.checkVersionTimer.start(100, True)
        self.ecmTimer = eTimer()
        self.ecmTimer.timeout.get().append(self.readEcmInfo)
        self.ecmTimer.start(10000, False)
        self.upgradeTimer = eTimer()
        self.upgradeTimer.timeout.get().append(self.connShowHide)
        self.onLayoutFinish.append(self.loadEmuList)
        self.onShown.append(self.setWindowTitle)
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self.checkVersionContainer = eConsoleAppContainer()
        self.checkVersionContainer.appClosed.append(self.fetchFinished)
        self.readEcmInfo()

    
    def checkVersion(self):
        url = t.readAddonsUrl() + {
            True: 'ver-test.txt',
            False: 'ver.txt' }[fileExists('/etc/.testmode')]
        print '[BluePanel] downloading version file ' + url
        cmd = {
            True: '/var/etc/proxy.sh && ',
            False: '' }[config.proxy.isactive.value] + 'wget ' + url + ' -O /tmp/ver.txt'
        self.checkVersionContainer.execute(cmd)

    
    def fetchFinished(self, retval):
        if fileExists('/tmp/ver.txt') and retval == 0:
            hwVersion = HardwareInfo().get_device_name()
            newVer = self.SVNVERSION
            
            try:
                f = open('/tmp/ver.txt', 'r')
                for line in f.readlines():
                    line = line.split('=')
                    if line[0] == 'FreeSpaceNeed':
                        NAddons.FREESPACENEEDUPGRADE = int(line[1][:-1])
                    
                    if line[0] == hwVersion:
                        newVer = line[1][:-1]
                        continue
                f.close()
                NAddons.CANUPGRADE = False
                unlink('/tmp/ver.txt')
                if int(self.SVNVERSION) < int(newVer):
                    NAddons.CANUPGRADE = True
                    self.upgradeTimer.start(500, False)
                    self['conn'].setText(_('Update is available!\nCurrent version: %s\nNew Version: %s\nPlease upgrade Nemesis firmware!') % (self.SVNVERSION, newVer))

        

    
    def connShowHide(self):
        if self['conn'].visible:
            self['conn'].hide()
        else:
            self['conn'].show()

    
    def setWindowTitle(self):
        self.setTitle('%s - %s: %s SVN(%s)' % (_('Nemesis Blue Panel'), _('Image Version'), self.NEMESISVER, self.SVNVERSION))

    
    def _nemesisBluePanel__onClose(self):
        if self.container.running():
            self.container.kill()
            self['conninfo'].text = _('Process Killed by user, Server Not Connected!')
        elif self.checkVersionContainer.running():
            self.checkVersionContainer.kill()
        
        if self.upgradeTimer.isActive():
            self.upgradeTimer.stop()
        
        if self.ecmTimer.isActive():
            self.ecmTimer.stop()
        
        if self.checkVersionTimer.isActive():
            self.checkVersionTimer.stop()
        
        if fileExists('/tmp/ver.txt'):
            unlink('/tmp/ver.txt')
        
        if fileExists('/tmp/info.txt'):
            unlink('/tmp/info.txt')
        
        self.close()

    
    def loadEmuList(self):
        emu = []
        crd = []
        emu.append('None')
        crd.append('None')
        self.emu_list = { }
        self.crd_list = { }
        self.emu_list['None'] = 'None'
        self.crd_list['None'] = 'None'
        emufilelist = FileList('/usr/script', matchingPattern = '_em.*')
        srvfilelist = FileList('/usr/script', matchingPattern = '_cs.*')
        for x in emufilelist.getFileList():
            if x[0][1] != True:
                emuName = t.readEmuName(x[0][0][:-6])
                emu.append(emuName)
                self.emu_list[emuName] = x[0][0][:-6]
                continue
        softcam = ConfigSelection(default = t.readEmuName(t.readEmuActive()), choices = emu)
        for x in srvfilelist.getFileList():
            if x[0][1] != True:
                srvName = t.readSrvName(x[0][0][:-6])
                crd.append(srvName)
                self.crd_list[srvName] = x[0][0][:-6]
                continue
        cardserver = ConfigSelection(default = t.readSrvName(t.readSrvActive()), choices = crd)
        del self.list[:]
        self.list.append(getConfigListEntry(_('SoftCams (%s) :') % str(len(emu) - 1), softcam))
        self.list.append(getConfigListEntry(_('CardServers (%s) :') % str(len(crd) - 1), cardserver))
        self.list.append(getConfigListEntry(_('Nemesis News'), ConfigNothing()))
        self.list.append(getConfigListEntry(_('Nemesis Timeline'), ConfigNothing()))
        self.list.append(getConfigListEntry(_('Parental Control Setup'), ConfigNothing()))
        self.list.append(getConfigListEntry(_('About Nemesis'), ConfigNothing()))
        self['config'].list = self.list
        self['config'].l.setList(self.list)

    
    def keyLeft(self):
        self['config'].handleKey(KEY_LEFT)

    
    def keyRight(self):
        self['config'].handleKey(KEY_RIGHT)

    
    def ok_pressed(self):
        self['conninfo'].text = ''
        if self.container.running():
            self.container.kill()
        
        self.sel = self['config'].getCurrentIndex()
        if self.sel == 0:
            self.newemu = self.emu_list[self['config'].getCurrent()[1].getText()]
            self.ss_sc()
        elif self.sel == 1:
            self.newsrv = self.crd_list[self['config'].getCurrent()[1].getText()]
            self.ss_srv()
        elif self.sel == 2:
            if not self.container.running():
                self['conninfo'].text = _('Connetting to server. Please wait...')
                cmd = {
                    True: '/var/etc/proxy.sh && ',
                    False: '' }[config.proxy.isactive.value] + 'wget ' + t.readAddonsUrl() + 'info.txt -O /tmp/info.txt'
                self.container.execute(cmd)
            
        elif self.sel == 3:
            if not self.container.running():
                self['conninfo'].text = _('Connetting to server. Please wait...')
                cmd = {
                    True: '/var/etc/proxy.sh && ',
                    False: '' }[config.proxy.isactive.value] + 'wget ' + t.readAddonsUrl() + 'timeline.txt -O /tmp/info.txt'
                self.container.execute(cmd)
            
        elif self.sel == 4:
            self.session.open(ParentalControlSetup)
        elif self.sel == 5:
            self.message = '\nNemesis Version: %s OE(%s)' % (self.NEMESISVER, self.OEVER)
            self.message += '\n\nImage version: ' + self.IMAGEVER
            self.message += '\nBuild by Gianathem'
            self.message += '\nBased on Enigma Version: ' + self.ENIGMAVER
            self.message += '\nKernel version: ' + self.KERNELVER
            self.message += '\n\nFor download visit: http://www.genesi-project.it/'
            self.mbox = self.session.open(MessageBox, self.message, MessageBox.TYPE_INFO)
            self.mbox.setTitle('About Nemesis ' + self.NEMESISVER)
        

    
    def runFinished(self, retval):
        if fileExists('/tmp/info.txt') and retval == 0:
            self['conninfo'].text = ''
            self.session.open(nemesisShowPanel, '/tmp/info.txt', {
                2: _('Nemesis News'),
                3: _('Nemesis Timeline') }[self.sel])
            unlink('/tmp/info.txt')
        else:
            self['conninfo'].text = _('Server not found! Please check internet connection.')

    
    def naddons(self):
        self.session.openWithCallback(self.loadEmuList, NAddons)

    
    def nsetting(self):
        self.session.openWithCallback(self.loadEmuList, NSetupSum)

    
    def ninfo(self):
        self.session.openWithCallback(self.loadEmuList, NInfo)

    
    def nutility(self):
        self.session.openWithCallback(self.loadEmuList, NUtility)

    
    def readEcmInfo(self):
        service = self.session.nav.getCurrentService()
        if service:
            pass
        info = service.info()
        if info is not None:
            if info.getInfo(iServiceInformation.sIsCrypted):
                self['ecmtext'].setText(t.readEcmInfo())
            else:
                self['ecmtext'].setText('Free To Air')
        else:
            self['ecmtext'].setText('')

    
    def ss_sc(self):
        self.emuactive = t.readEmuActive()
        self.oldref = self.session.nav.getCurrentlyPlayingServiceReference()
        if self.emuactive != 'None' and self.newemu != 'None':
            if self.emuactive == self.newemu:
                mess = _('Restarting %s.') % t.readEmuName(self.emuactive)
            else:
                mess = _('Stopping %s and starting %s.') % (t.readEmuName(self.emuactive), t.readEmuName(self.newemu))
            cmd = '/var/script/%s_em.sh stop && ' % self.emuactive
            cmd += '/var/script/%s_em.sh start && ' % self.newemu
            cmd += 'echo %s > /var/bin/emuactive' % self.newemu
            self.executeCommand(mess, cmd, True, True)
            return None
        if self.emuactive != 'None':
            mess = _('Stopping %s.') % t.readEmuName(self.emuactive)
            cmd = '/var/script/%s_em.sh stop && ' % self.emuactive
            cmd += 'rm -f /var/bin/emuactive'
            self.executeCommand(mess, cmd)
            return None
        if self.newemu != 'None':
            mess = _('Starting %s.') % t.readEmuName(self.newemu)
            cmd = '/var/script/%s_em.sh start && ' % self.newemu
            cmd += 'echo %s > /var/bin/emuactive' % self.newemu
            self.executeCommand(mess, cmd, True, True)
        

    
    def ss_srv(self):
        self.serveractive = t.readSrvActive()
        if self.serveractive == 'None' and self.newsrv == 'None':
            return None
        self.emuactive = t.readEmuActive()
        if self.emuactive != 'None' and self.serveractive == 'None':
            self.box = self.session.open(MessageBox, _('Please stop %s\nbefore start cardserver!') % t.readEmuName(self.emuactive), MessageBox.TYPE_INFO)
            self.box.setTitle(_('Start Cardserver'))
            return None
        if self.serveractive != 'None' and self.newsrv != 'None':
            if self.serveractive == self.newsrv:
                mess = _('Restarting %s.') % t.readSrvName(self.serveractive)
            else:
                mess = _('Stopping %s and starting %s.') % (t.readSrvName(self.serveractive), t.readSrvName(self.newsrv))
            cmd = '/var/script/%s_cs.sh stop && ' % self.serveractive
            cmd += '/var/script/%s_cs.sh start && ' % self.newsrv
            cmd += 'echo %s > /var/bin/csactive' % self.newsrv
            self.executeCommand(mess, cmd)
            return None
        if self.serveractive != 'None':
            mess = _('Stopping %s.') % t.readSrvName(self.serveractive)
            cmd = '/var/script/%s_cs.sh stop && ' % self.serveractive
            cmd += 'rm -f /var/bin/csactive'
            self.executeCommand(mess, cmd)
            return None
        if self.newsrv != 'None':
            mess = _('Starting  %s.') % t.readSrvName(self.newsrv)
            cmd = '/var/script/%s_cs.sh start && ' % self.newsrv
            cmd += 'echo %s > /var/bin/csactive' % self.newsrv
            self.executeCommand(mess, cmd)
        

    
    def executeCommand(self, mess, cmd, panelClose = False, playServ = False):
        self.playServ = playServ
        self.panelClose = panelClose
        self.hide()
        self.mbox = self.session.open(MessageBox, mess, MessageBox.TYPE_INFO, enable_input = False)
        self.mbox.setTitle(_('Running..'))
        if self.playServ:
            self.session.nav.stopService()
        
        self.console.ePopen("nemesisc '%s' '%s' '%s'" % ('127.0.0.1', self.nemPortNumber, cmd), self.commandFinished)

    
    def commandFinished(self, result, retval, extra_args):
        if self.playServ:
            self.session.nav.playService(self.oldref)
        
        self.mbox.close()
        if self.panelClose:
            self._nemesisBluePanel__onClose()
        else:
            self.show()



class nemesisBluePanelOpen:
    __module__ = __name__
    
    def __init__(self):
        self['nemesisBluePanelOpen'] = ActionMap([
            'InfobarExtensions'], {
            'nemesisBpanel': self.NemesisBpOpen })

    
    def NemesisBpOpen(self):
        self.session.open(nemesisBluePanel)



class nemesisPluginsPanelOpen:
    __module__ = __name__
    
    def __init__(self):
        self['nemesisPluginsPanelOpen'] = ActionMap([
            'InfobarTimeshiftActions',
            'InfobarAudioSelectionActions'], {
            'nemesisOPlugins': self.NemesisPluginsOpen })

    
    def NemesisPluginsOpen(self):
        self.session.open(PluginBrowser)


