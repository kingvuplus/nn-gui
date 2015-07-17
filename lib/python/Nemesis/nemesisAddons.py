from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from enigma import eTimer, eDVBDB, eConsoleAppContainer
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Sources.List import List
from Components.ProgressBar import ProgressBar
from Components.ScrollLabel import ScrollLabel
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.config import config
from Components.PluginComponent import plugins
from Components.Sources.StaticText import StaticText
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, pathExists, createDir
from os import system, remove, listdir, chdir, getcwd, rename
from nemesisTool import nemesisTool, GetSkinPath
from nemesisConsole import nemesisConsole
from nemesisDownloader import nemesisDownloader
from Tools import Notifications
import xml.etree.cElementTree as x
t = nemesisTool()

class util:
    pluginIndex = -1
    pluginType = ''
    typeDownload = 'A'
    addonsName = ''
    filename = ''
    dir = ''
    size = 0
    check = 0
    
    def removeSetting(self):
        print 'Remove settings'
        system('rm -f /etc/enigma2/*.radio')
        system('rm -f /etc/enigma2/*.tv')
        system('rm -f /etc/enigma2/lamedb')
        system('rm -f /etc/enigma2/blacklist')
        system('rm -f /etc/enigma2/whitelist')

    
    def reloadSetting(self):
        print 'Reload settings'
        self.eDVBDB = eDVBDB.getInstance()
        self.eDVBDB.reloadServicelist()
        self.eDVBDB.reloadBouquets()


u = util()

class loadXml:
    tree_list = []
    plugin_list = []
    
    def load(self, filename):
        del self.tree_list[:]
        del self.plugin_list[:]
        tree = x.parse(filename)
        root = tree.getroot()
        c = 0
        for tag in root.getchildren():
            self.tree_list.append([
                c,
                tag.tag])
            c1 = 0
            for b in tree.find(tag.tag):
                self.plugin_list.append([
                    c,
                    tag.tag,
                    b.find('Filename').text,
                    b.find('Descr').text,
                    b.find('Folder').text,
                    b.find('Size').text,
                    b.find('Check').text,
                    c1])
                c1 += 1
            c += 1


loadxml = loadXml()

class loadTmpDir:
    tmp_list = []
    
    def load(self):
        del self.tmp_list[:]
        pkgs = listdir('/tmp')
        count = 0
        for fil in pkgs:
            if fil.find('.ipk') != -1 or fil.find('.tbz2') != -1:
                self.tmp_list.append([
                    count,
                    fil])
                count += 1
                continue


loadtmpdir = loadTmpDir()

class loadUniDir:
    uni_list = []
    
    def load(self):
        del self.uni_list[:]
        pkgs = listdir('/usr/uninstall')
        count = 0
        for fil in pkgs:
            if fil.find('_remove.sh') != -1 or fil.find('_delete.sh') != -1:
                self.uni_list.append([
                    count,
                    fil])
                count += 1
                continue


loadunidir = loadUniDir()

class NAddons(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430" title="Addons">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (50, 5), size = (300, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos=(5, 1), size=(34, 34), png=2),\n\t\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 40\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget source="conn" render="Label" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" transparent="1" />\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    FREESPACENEEDUPGRADE = 4000
    CANUPGRADE = False
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['title'] = Label(_('Addons Manager'))
        self['list'] = List(self.list)
        self['conn'] = StaticText('')
        self['spaceused'] = ProgressBar()
        self['key_red'] = Label(_('Cancel'))
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self.containerExtra = eConsoleAppContainer()
        self.containerExtra.appClosed.append(self.runFinishedExtra)
        self.reloadTimer = eTimer()
        self.reloadTimer.timeout.get().append(self.relSetting)
        self.linkAddons = t.readAddonsUrl()
        self.linkExtra = t.readExtraUrl()
        isPluginManager = False
        if fileExists(resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/SoftwareManager/plugin.py')):
            isPluginManager = True
        
        self.MenuList = [
            ('NAddons', _('Download Addons'), 'icons/network.png', True),
            ('NExtra', _('Download Extra'), 'icons/network.png', fileExists('/etc/extra.url')),
            ('NManual', _('Manual Package Install'), 'icons/manual.png', True),
            ('NRemove', _('Remove Addons'), 'icons/remove.png', True),
            ('NReload', _('Reload Settings'), 'icons/enigma.png', True),
            ('NExtension', _('Manage extensions'), 'icons/extensions.png', isPluginManager),
            ('NPacket', _('Packet management'), 'icons/package.png', isPluginManager),
            ('NUpdate', _('Software update'), 'icons/update.png', isPluginManager)]
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'red': self.cancel,
            'back': self.cancel })
        self.onLayoutFinish.append(self.updateList)
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        diskSpace = t.getVarSpaceKb()
        percFree = int((diskSpace[0] / diskSpace[1]) * 100)
        percUsed = int(((diskSpace[1] - diskSpace[0]) / diskSpace[1]) * 100)
        self.setTitle('%s - Free: %d kB (%d%%)' % (_('Addons Manager'), int(diskSpace[0]), percFree))
        self['spaceused'].setValue(percUsed)

    
    def KeyOk(self):
        self['conn'].text = ''
        if not self.container.running():
            sel = self['list'].getCurrent()[0]
            if sel == 'NAddons':
                self['conn'].text = _('Connetting to addons server.\nPlease wait...')
                u.typeDownload = 'A'
                self.container.execute({
                    True: '/var/etc/proxy.sh && ',
                    False: '' }[config.proxy.isactive.value] + 'wget ' + self.linkAddons + '/addonsE2.xml -O /tmp/addons.xml')
            elif sel == 'NExtra':
                self['conn'].text = _('Connetting to addons server.\nPlease wait...')
                u.typeDownload = 'E'
                if self.linkExtra != None:
                    self.containerExtra.execute({
                        True: '/var/etc/proxy.sh && ',
                        False: '' }[config.proxy.isactive.value] + 'wget ' + self.linkExtra + 'iuregdoiuwqcdiuewq/tmp.tmp -O /tmp/tmp.tmp')
                else:
                    self['conn'].text = _('Server not found!\nPlease check internet connection.')
            elif sel == 'NManual':
                self.session.open(RManual)
            elif sel == 'NRemove':
                self.session.open(RRemove)
            elif sel == 'NExtension':
                
                try:
                    PluginManager = PluginManager
                    import Plugins.SystemPlugins.SoftwareManager.plugin
                except ImportError:
                    self.session.open(MessageBox, _('The Softwaremanagement extension is not installed!\nPlease install it.'), type = MessageBox.TYPE_INFO, timeout = 10)

                self.session.open(PluginManager, GetSkinPath())
            elif sel == 'NPacket':
                
                try:
                    PacketManager = PacketManager
                    import Plugins.SystemPlugins.SoftwareManager.plugin
                except ImportError:
                    self.session.open(MessageBox, _('The Softwaremanagement extension is not installed!\nPlease install it.'), type = MessageBox.TYPE_INFO, timeout = 10)

                self.session.open(PacketManager, GetSkinPath())
            elif sel == 'NUpdate':
                if not (self.CANUPGRADE) and not fileExists('/etc/.testmode'):
                    msg = _('No Upgrade available!\nYour decoder is up to date.')
                    self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
                    return None
                if int(t.getVarSpaceKb()[0]) < self.FREESPACENEEDUPGRADE:
                    msg = _('Not enough free space on flash to perform Upgrade!\nUpgrade require at least %d kB free on Flash.\nPlease remove some addons or skins before upgrade.') % self.FREESPACENEEDUPGRADE
                    self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
                    return None
                self.session.openWithCallback(self.runUpgrade, MessageBox, _('Do you want to update your Dreambox?') + '\n' + _('\nAfter pressing OK, please wait!'))
            elif sel == 'NReload':
                self['conn'].text = _('Reload settings, please wait...')
                self.reloadTimer.start(250, True)
            
        

    
    def relSetting(self):
        u.reloadSetting()
        self['conn'].text = _('Settings reloaded succesfully!')

    
    def runUpgrade(self, result):
        if result:
            
            try:
                UpdatePlugin = UpdatePlugin
                import Plugins.SystemPlugins.SoftwareManager.plugin
            except ImportError:
                self.session.open(MessageBox, _('The Softwaremanagement extension is not installed!\nPlease install it.'), type = MessageBox.TYPE_INFO, timeout = 10)

            self.session.open(UpdatePlugin, GetSkinPath())
        

    
    def runFinishedExtra(self, retval):
        if fileExists('/tmp/tmp.tmp'):
            
            try:
                f = open('/tmp/tmp.tmp', 'r')
                line = f.readline()[:-1]
                f.close()
                self.container.execute({
                    True: '/var/etc/proxy.sh && ',
                    False: '' }[config.proxy.isactive.value] + 'wget ' + self.linkExtra + 'iuregdoiuwqcdiuewq/' + line + ' -O /tmp/addons.xml')
            self['conn'].text = _('Server not found!\nPlease check internet connection.')

        else:
            self['conn'].text = _('Server not found!\nPlease check internet connection.')

    
    def runFinished(self, retval):
        if fileExists('/tmp/addons.xml'):
            
            try:
                loadxml.load('/tmp/addons.xml')
                remove('/tmp/addons.xml')
                self['conn'].text = ''
                self.session.open(RAddons)
            self['conn'].text = _('File xml is not correctly formatted!.')

        else:
            self['conn'].text = _('Server not found!\nPlease check internet connection.')

    
    def cancel(self):
        if not self.container.running() and not self.containerExtra.running():
            del self.container.appClosed[:]
            del self.container
            del self.containerExtra.appClosed[:]
            del self.containerExtra
            self.close()
        elif self.container.running():
            self.container.kill()
        
        if self.containerExtra.running():
            self.containerExtra.kill()
        
        if fileExists('/tmp/addons.xml'):
            remove('/tmp/addons.xml')
        
        if fileExists('/tmp/tmp.tmp'):
            remove('/tmp/tmp.tmp')
        
        self['conn'].text = _('Process Killed by user\nServer Not Connected!')

    
    def updateList(self):
        del self.list[:]
        skin_path = GetSkinPath()
        for i in self.MenuList:
            if i[3]:
                self.list.append((i[0], i[1], LoadPixmap(skin_path + i[2])))
                continue
        self['list'].setList(self.list)



class RAddons(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (0, 0), size = (340, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 35\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self.wtitle = {
            'A': _('Download Addons'),
            'E': _('Download Extra') }[u.typeDownload]
        self['list'] = List(self.list)
        self['title'] = Label(self.wtitle)
        self['key_red'] = Label(_('Cancel'))
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'red': self.close,
            'back': self.close })
        self.onLayoutFinish.append(self.loadData)
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(self.wtitle)

    
    def KeyOk(self):
        u.pluginType = self['list'].getCurrent()[0]
        u.pluginIndex = self['list'].getIndex()
        self.session.open(RAddonsDown)

    
    def loadData(self):
        del self.list[:]
        for tag in loadxml.tree_list:
            self.list.append((tag[1], tag[1]))
        self['list'].setList(self.list)



class RAddonsDown(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,530" title="Addons">\n\t\t\t<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>\n\t\t\t<widget source="list" render="Listbox" position="10,10" size="540,340" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (5, 0), size = (530, 30), font=0, flags = RT_HALIGN_LEFT | RT_HALIGN_LEFT, text = 1),\n\t\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20)],\n\t\t\t\t\t"itemHeight": 30\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget source="conn" render="Label" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" transparent="1" />\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self['conn'] = StaticText(_('Loading elements.\nPlease wait...'))
        self['type'] = Label('')
        self['key_red'] = Label(_('Cancel'))
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self['type'].setText(_('Download ') + str(u.pluginType))
        self.linkAddons = t.readAddonsUrl()
        self.linkExtra = t.readExtraUrl()
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'red': self.cancel,
            'back': self.cancel })
        self.onLayoutFinish.append(self.loadPlugin)
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(_('Download ') + str(u.pluginType))

    
    def KeyOk(self):
        if not self.container.running():
            self.sel = self['list'].getIndex()
            for tag in loadxml.plugin_list:
                if tag[0] == u.pluginIndex:
                    if tag[7] == self.sel:
                        u.addonsName = tag[3]
                        self.downloadAddons()
                        return None
                    continue
                tag[7] == self.sel
            self.close()
        

    
    def loadPlugin(self):
        del self.list[:]
        for tag in loadxml.plugin_list:
            if tag[0] == u.pluginIndex:
                self.list.append((tag[3], tag[3]))
                continue
        self['list'].setList(self.list)
        self['conn'].text = _('Elements Loaded!.\nPlease select one to install.')

    
    def downloadAddons(self):
        self.getAddonsPar()
        if int(u.size) > int(t.getVarSpaceKb()[0]) and int(u.check) != 0:
            msg = _('Not enough space!\nPlease delete addons before install new.')
            self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
            return None
        url = {
            'E': self.linkExtra,
            'A': self.linkAddons }[u.typeDownload] + u.dir + '/' + u.filename
        if not pathExists('/tmp/.-'):
            createDir('/tmp/.-')
        
        if config.proxy.isactive.value:
            cmd = '/var/etc/proxy.sh && wget %s -O /tmp/.-/%s' % (url, '.-')
            self.session.openWithCallback(self.executedScript, nemesisConsole, cmd, _('Download: ') + u.filename)
        else:
            self.session.openWithCallback(self.executedScript, nemesisDownloader, url, '/tmp/.-/', '.-')

    
    def executedScript(self, *answer):
        if answer[0] == nemesisConsole.EVENT_DONE:
            if fileExists('/tmp/.-/.-'):
                msg = _('Do you want install the addon:\n%s?') % u.addonsName
                box = self.session.openWithCallback(self.installAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle(_('Install Addon'))
            else:
                msg = _('File: %s not found!\nPlease check your internet connection.') % u.filename
                self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)
        elif answer[0] == nemesisConsole.EVENT_KILLED:
            self['conn'].text = _('Process Killed by user!\nAddon not downloaded.')
        

    
    def installAddons(self, answer):
        if answer is True:
            self['conn'].text = _('Installing addons.\nPlease Wait...')
            if u.filename.find('.ipk') != -1:
                args = {
                    True: '--force-overwrite --force-defaults ',
                    False: '' }[config.nemesis.ipkg.overwriteUpgrade.value]
                args = {
                    True: '--force-reinstall --force-defaults ',
                    False: '' }[config.nemesis.ipkg.forceReInstall.value]
                rename('/tmp/.-/.-', '/tmp/.-/p.ipk')
                self.container.execute('ipkg ' + args + 'install /tmp/.-/p.ipk')
            elif u.filename.find('.tbz2') != -1:
                if u.pluginType == 'Settings' or u.pluginType == 'e2Settings':
                    self['conn'].text = _('Remove old Settings\nPlease wait...')
                    u.removeSetting()
                
                self.container.execute('tar -jxvf /tmp/.-/.- -C /')
            else:
                self['conn'].text = _('File: %s\nis not a valid package!') % u.filename
        elif pathExists('/tmp/.-'):
            system('rm -rf /tmp/.-')
        

    
    def runFinished(self, retval):
        if pathExists('/tmp/.-'):
            system('rm -rf /tmp/.-')
        
        if u.pluginType == 'Settings' or u.pluginType == 'e2Settings':
            self['conn'].text = _('Reload new Settings\nPlease wait...')
            u.reloadSetting()
        
        if u.pluginType == 'Plugins' or u.pluginType == 'e2Plugins':
            self['conn'].text = _('Reload Plugins list\nPlease Wait...')
            self.reloadPluginlist()
        
        self['conn'].text = _('Addon installed succesfully!')
        if fileExists('/tmp/.restartE2'):
            remove('/tmp/.restartE2')
            msg = _('Enigma2 will be now hard restarted to complete package installation.') + '\n' + _('Do You want restart enigma2 now?')
            box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg, MessageBox.TYPE_YESNO)
            box.setTitle(_('Restart Enigma2'))
        

    
    def reloadPluginlist(self):
        print 'Read plugin list'
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))

    
    def cancel(self):
        if not self.container.running():
            del self.container.appClosed[:]
            del self.container
            self.close()
        else:
            self.container.kill()
            self['conn'].text = _('Process Killed by user.\nAddon not installed correctly!')

    
    def restartEnigma2(self, answer):
        if answer is True:
            system('killall -9 enigma2')
        

    
    def getAddonsPar(self):
        for tag in loadxml.plugin_list:
            if tag[0] == u.pluginIndex:
                if tag[3] == u.addonsName:
                    u.filename = tag[2]
                    u.dir = tag[4]
                    u.size = tag[5]
                    u.check = tag[6]
                
            tag[3] == u.addonsName



class RManual(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430">\n\t\t\t<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>\n\t\t\t<widget source="list" render="Listbox" position="50,20" size="400,390" zPosition="2" scrollbarMode="showOnDemand" transparent="1">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (0, 0), size = (410, 30), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),\n\t\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Prive2", 20)],\n\t\t\t\t\t"itemHeight": 30\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget source="conn" render="Label" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" transparent="1" />\n\t\t\t<widget name="key_red" position="0,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget name="key_yellow" position="280,510" size="280,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#bab329" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self['conn'] = StaticText('')
        self['title'] = Label(_('Manual Installation'))
        self['key_red'] = Label(_('Cancel'))
        self['key_yellow'] = Label(_('Reload /tmp'))
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'yellow': self.readTmp,
            'red': self.cancel,
            'back': self.cancel })
        self.onLayoutFinish.append(self.readTmp)
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(_('Manual Installation'))

    
    def readTmp(self):
        del self.list[:]
        loadtmpdir.load()
        if len(loadtmpdir.tmp_list) > 0:
            for fil in loadtmpdir.tmp_list:
                self.list.append((fil[1], fil[1]))
            
        else:
            self['conn'].text = _('Put your plugin xxx.tbz2 or xxx.ipk\nvia FTP in /tmp.')
        self['list'].setList(self.list)

    
    def KeyOk(self):
        if not self.container.running():
            if len(loadtmpdir.tmp_list) > 0:
                self.sel = self['list'].getIndex()
                for p in loadtmpdir.tmp_list:
                    if p[0] == self.sel:
                        u.filename = p[1]
                        continue
                msg = _('Do you want install the addon:\n%s?') % u.filename
                box = self.session.openWithCallback(self.installAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle(_('Install Addon'))
            else:
                self.close()
        

    
    def installAddons(self, answer):
        if answer is True:
            self['conn'].text = _('Installing: %s.\nPlease wait...') % u.filename
            if u.filename.find('.ipk') != -1:
                args = {
                    True: '--force-overwrite --force-defaults ',
                    False: '' }[config.nemesis.ipkg.overwriteUpgrade.value]
                args = {
                    True: '--force-reinstall --force-defaults ',
                    False: '' }[config.nemesis.ipkg.forceReInstall.value]
                self.container.execute('ipkg ' + args + 'install /tmp/' + u.filename)
            elif u.filename.find('.tbz2') != -1:
                self.container.execute('tar -jxvf /tmp/' + u.filename + ' -C /')
            else:
                self['conn'].text = _('File: %s\nis not a valid package!') % u.filename
        

    
    def runFinished(self, retval):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        remove('/tmp/' + u.filename)
        self['conn'].text = _('Addon: %s\ninstalled succesfully!') % u.filename
        self.readTmp()
        if fileExists('/tmp/.restartE2'):
            remove('/tmp/.restartE2')
            msg = 'Enigma2 will be now hard restarted to complete package installation.\nDo You want restart enigma2 now?'
            box = self.session.openWithCallback(self.restartEnigma2, MessageBox, msg, MessageBox.TYPE_YESNO)
            box.setTitle('Restart enigma')
        

    
    def cancel(self):
        if not self.container.running():
            del self.container.appClosed[:]
            del self.container
            self.close()
        else:
            self.container.kill()
            self['conn'].text = _('Process Killed by user.\nAddon not installed correctly!')

    
    def restartEnigma2(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        



class RRemove(Screen):
    __module__ = __name__
    skin = '\n\t\t<screen position="80,95" size="560,430" title="Addons">\n\t\t\t<widget name="title" position="10,5" size="320,55" font="Regular;28" foregroundColor="#ff2525" backgroundColor="transpBlack" transparent="1"/>\n\t\t\t<widget source="list" render="Listbox" position="50,20" size="400,390" zPosition="2" scrollbarMode="showOnDemand" transparent="1">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (0, 0), size = (410, 30), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 1),\n\t\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Prive2", 20)],\n\t\t\t\t\t"itemHeight": 30\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<widget source="conn" render="Label" position="0,360" size="540,50" font="Regular;20" halign="center" valign="center" transparent="1" />\n\t\t\t<widget name="key_red" position="0,510" size="560,20" zPosition="1" font="Regular;22" valign="center" foregroundColor="#0064c7" backgroundColor="#9f1313" transparent="1" />\n\t\t</screen>'
    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.list = []
        self['list'] = List(self.list)
        self['conn'] = StaticText('')
        self['title'] = Label(_('Remove Addons'))
        self['key_red'] = Label(_('Cancel'))
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self['actions'] = ActionMap([
            'WizardActions',
            'ColorActions'], {
            'ok': self.KeyOk,
            'red': self.cancel,
            'back': self.cancel })
        self.onLayoutFinish.append(self.readTmp)
        self.onShown.append(self.setWindowTitle)

    
    def setWindowTitle(self):
        self.setTitle(_('Remove Addons'))

    
    def readTmp(self):
        loadunidir.load()
        del self.list[:]
        if len(loadunidir.uni_list) > 0:
            for fil in loadunidir.uni_list:
                self.list.append((fil[1], fil[1][:-10]))
            
        else:
            self['conn'].text = _('Nothing to uninstall!')
        self['list'].setList(self.list)

    
    def KeyOk(self):
        if not self.container.running():
            if len(loadunidir.uni_list) > 0:
                self.sel = self['list'].getIndex()
                for p in loadunidir.uni_list:
                    if p[0] == self.sel:
                        u.filename = p[1]
                        continue
                msg = _('Do you want remove the addon:\n%s?') % u.filename[:-10]
                box = self.session.openWithCallback(self.removeAddons, MessageBox, msg, MessageBox.TYPE_YESNO)
                box.setTitle('Remove Addon')
            else:
                self.close()
        

    
    def removeAddons(self, answer):
        if answer is True:
            self['conn'].text = _('Removing: %s.\nPlease wait...') % u.filename[:-10]
            self.container.execute('/usr/uninstall/' + u.filename)
        

    
    def runFinished(self, retval):
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        self.readTmp()
        self['conn'].text = _('Addons: %s\nremoved succeffully.') % u.filename[:-10]

    
    def cancel(self):
        if not self.container.running():
            del self.container.appClosed[:]
            del self.container
            self.close()
        else:
            self.container.kill()
            self['conn'].text = _('Process Killed by user.\nAddon not removed completly!')


