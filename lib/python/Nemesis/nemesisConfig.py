from Components.config import ConfigSubsection, ConfigYesNo, config, ConfigSelection, ConfigText, ConfigNumber, ConfigSet, ConfigLocations, ConfigSlider, ConfigText, ConfigEnableDisable, ConfigDateTime, ConfigInteger, ConfigNothing
from enigma import eDBoxLCD

def InitNemesisConfig():
    config.nemesis = ConfigSubsection()
    config.nemesis.einfo = ConfigYesNo(default = True)
    config.nemesis.replaceinfobar = ConfigYesNo(default = False)
    config.nemesis.einfotimeout = ConfigNumber(default = 800)
    config.nemesis.shownetdet = ConfigYesNo(default = True)
    config.nemesis.eiinfobardelayonzap = ConfigNumber(default = 100)
    config.nemesis.emminfodelay = ConfigNumber(default = 400)
    config.nemesis.ecminfodelay = ConfigNumber(default = 1000)
    config.nemesis.picontype = ConfigSelection(default = 'Reference', choices = [
        ('Name', _('Name')),
        ('Reference', _('Reference'))])
    if eDBoxLCD.getInstance().detected():
        config.nemesis.piconlcd = ConfigYesNo(default = False)
        config.nemesis.piconlcdtype = ConfigSelection(default = 'Reference', choices = [
            ('Name', _('Name')),
            ('Reference', _('Reference'))])
    else:
        config.nemesis.piconlcd = ConfigNothing()
        config.nemesis.piconlcdtype = ConfigNothing()
    config.nemesis.usevkeyboard = ConfigEnableDisable(default = False)
    config.nemesis.autocloseconsole = ConfigYesNo(default = True)
    config.nemesis.autocloseconsoledelay = ConfigSelection(default = '1', choices = [
        ('0', _('No Delay')),
        ('1', '1 ' + _('second')),
        ('2', '2 ' + _('seconds')),
        ('3', '3 ' + _('seconds')),
        ('4', '4 ' + _('seconds')),
        ('5', '5 ' + _('seconds')),
        ('6', '6 ' + _('seconds')),
        ('7', '7 ' + _('seconds')),
        ('8', '8 ' + _('seconds'))])
    config.nemesis.usepiconinhdd = ConfigYesNo(default = False)
    config.nemesis.forceumount = ConfigYesNo(default = False)
    config.nemesis.ipkg = ConfigSubsection()
    config.nemesis.ipkg.overwriteUpgrade = ConfigYesNo(default = True)
    config.nemesis.ipkg.forceReInstall = ConfigYesNo(default = False)
    config.nemesis.ipkg.updateTimeout = ConfigInteger(20, (20, 60))
    config.plugins.FadeSet = ConfigSubsection()
    config.plugins.FadeSet.fadeIn = ConfigYesNo(default = True)
    config.plugins.FadeSet.fadeOut = ConfigYesNo(default = True)
    config.plugins.FadeSet.fadeInOnZap = ConfigYesNo(default = False)
    config.plugins.FadeSet.timeout = ConfigInteger(3, (1, 10))
    config.inadyn = ConfigSubsection()
    config.inadyn.user = ConfigText(default = 'myuser', fixed_size = False)
    config.inadyn.password = ConfigText(default = 'mypassword', fixed_size = False)
    config.inadyn.alias = ConfigText(default = 'mydomain.com', fixed_size = False)
    config.inadyn.period = ConfigNumber(default = 60)
    config.inadyn.system = ConfigSelection(default = 'dyndns@dyndns.org', choices = [
        'dyndns@dyndns.org',
        'statdns@dyndns.org',
        'default@zoneedit.com',
        'default@no-ip.com',
        'custom@dyndns.org',
        'default@freedns.afraid.org'])
    config.inadyn.log = ConfigSelection(default = '/var/log', choices = [
        '/tmp',
        '/var/log',
        '/usr/log'])
    config.ipupdate = ConfigSubsection()
    config.ipupdate.user = ConfigText(default = 'myuser', fixed_size = False)
    config.ipupdate.password = ConfigText(default = 'mypassword', fixed_size = False)
    config.ipupdate.alias = ConfigText(default = 'www.mydomain.com', fixed_size = False)
    config.ipupdate.server = ConfigText(default = 'mydomain.com', fixed_size = False)
    config.ipupdate.period = ConfigNumber(default = 60)
    config.ipupdate.system = ConfigSelection(default = 'ezip', choices = [
        'ezip',
        'pgpow',
        'dhs',
        'dyndns',
        'dyndns-static',
        'ods',
        'tzo',
        'gnudip',
        'easydns',
        'justlinux',
        'dyns',
        'hn',
        'zoneedit'])
    config.ipupdate.log = ConfigSelection(default = '/var/log', choices = [
        '/tmp',
        '/var/log',
        '/usr/log'])
    config.proxy = ConfigSubsection()
    config.proxy.isactive = ConfigYesNo(default = False)
    config.proxy.server = ConfigText(default = 'myserver.mydomain.com', fixed_size = False)
    config.proxy.port = ConfigNumber(default = 8080)
    config.proxy.user = ConfigText(default = 'myuser', fixed_size = False)
    config.proxy.password = ConfigText(default = 'mypassword', fixed_size = False)
    config.nemepg = ConfigSubsection()
    config.nemepg.elemnum = ConfigNumber(default = 48)
    config.nemepg.zapdelay = ConfigSelection(default = '2', choices = [
        ('1', '1 ' + _('second')),
        ('2', '2 ' + _('seconds')),
        ('3', '3 ' + _('seconds')),
        ('4', '4 ' + _('seconds')),
        ('5', '5 ' + _('seconds')),
        ('6', '6 ' + _('seconds')),
        ('7', '7 ' + _('seconds')),
        ('8', '8 ' + _('seconds')),
        ('9', '9 ' + _('seconds')),
        ('10', '10 ' + _('seconds')),
        ('11', '11 ' + _('seconds')),
        ('12', '12 ' + _('seconds')),
        ('13', '13 ' + _('seconds')),
        ('14', '14 ' + _('seconds')),
        ('15', '15 ' + _('seconds'))])
    config.nemepg.downskyit = ConfigYesNo(default = True)
    config.nemepg.skyitch = ConfigSelection(default = '0e31:00820000:16a8:fbff:1:0', choices = [
        ('0e31:00820000:16a8:fbff:1:0', 'Marcopolo'),
        ('0e33:00820000:16a8:fbff:1:0', 'Fox +1'),
        ('0e30:00820000:16a8:fbff:1:0', 'Nuvolari')])
    config.nemepg.downskyuk = ConfigYesNo(default = False)
    config.nemepg.skyukch = ConfigSelection(default = '0fd1:011a0000:07d4:0002:2:0', choices = [
        ('0fd1:011a0000:07d4:0002:2:0', 'Hip Hop'),
        ('0fd0:011a0000:07d4:0002:2:0', 'The Alternative-GER'),
        ('0fd2:011a0000:07d4:0002:2:0', 'Rewind (80s-90s)')])
    config.nemepg.clearcache = ConfigYesNo(default = True)
    config.nemepg.clearbackup = ConfigYesNo(default = False)
    config.nemepg.enatimer = ConfigEnableDisable(default = True)

