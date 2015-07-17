from Screens.Screen import Screen
from Components.Label import Label, MultiColorLabel
from Components.Pixmap import Pixmap
from Components.ServiceEventTracker import ServiceEventTracker
from Components.config import config
from enigma import eTimer, eEnv, iServiceInformation, iPlayableService, eDVBFrontendParametersSatellite, eDVBFrontendParametersCable, eDVBFrontendParametersTerrestrial
from nemesisTool import nemesisTool, parse_ecm
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename
import os
import re
t = nemesisTool()

class nemesisEI(Screen):
    __module__ = __name__
    
    def readEcmFile(self):
        emuActive = t.readEmuActive()
        return t.readEcmInfoFile(emuActive)

    
    def readEmuName(self):
        emuActive = t.readEmuActive()
        return t.readEmuName(emuActive)

    
    def readCsName(self):
        csActive = t.readSrvActive()
        return t.readSrvName(csActive)

    
    def showEmuName(self):
        self['emuname'].setText(self.readEmuName())
        csName = self.readCsName()
        if csName != 'None':
            self['emuname'].setText(self['emuname'].getText() + ' / ' + csName)
        

    
    def __init__(self, session):
        Screen.__init__(self, session)
        self.systemCod = [
            'beta',
            'bis',
            'bul',
            'dream',
            'dre',
            'conax',
            'cw',
            'irdeto',
            'nagra',
            'nds',
            'seca',
            'via']
        self.systemState = [
            'b_fta',
            'b_card',
            'b_emu',
            'b_spider']
        self.systemCaids = {
            '06': 'irdeto',
            '01': 'seca',
            '18': 'nagra',
            '05': 'via',
            '0B': 'conax',
            '17': 'beta',
            '0D': 'cw',
            '4A': 'dream',
            '09': 'nds',
            '4AE0': 'dre',
            '4AE1': 'dre',
            '55': 'bul',
            '26': 'bis' }
        for x in self.systemCod:
            self[x] = MultiColorLabel()
        for x in self.systemState:
            self[x] = Label()
        self['ecm_pict'] = Pixmap()
        self['TunerInfo'] = Label()
        self['SatInfo'] = Label()
        self['EmuInfo'] = Label()
        self['ecmtime'] = Label()
        self['netcard'] = Label()
        self['emuname'] = Label()
        self['hops'] = Label()
        self['reader'] = Label()
        self.path = 'piconSys'
        self.ecm_timer = eTimer()
        self.ecm_timer.timeout.get().append(self._nemesisEI__updateEmuInfo)
        self.ecmTimeStep = 0
        self.emm_timer = eTimer()
        self.emm_timer.timeout.get().append(self._nemesisEI__updateEMMInfo)
        self._nemesisEI__evStart()
        self._nemesisEI__event_tracker = ServiceEventTracker(screen = self, eventmap = {
            iPlayableService.evStart: self._nemesisEI__evStart,
            iPlayableService.evUpdatedInfo: self._nemesisEI__evUpdatedInfo,
            iPlayableService.evTunedIn: self._nemesisEI__evTunedIn })
        self.onHide.append(self._nemesisEI__onHide)
        self.onShow.append(self._nemesisEI__onShow)

    
    def _nemesisEI__onHide(self):
        if self.emm_timer.isActive():
            self.emm_timer.stop()
        
        if self.ecm_timer.isActive():
            self.ecm_timer.stop()
        

    
    def _nemesisEI__onShow(self):
        service = self.session.nav.getCurrentService()
        if service:
            pass
        info = service.info()
        if info is not None:
            if not self.ecm_timer.isActive():
                self.ecmTimeStep = 0
                self.ecm_timer.start(config.nemesis.ecminfodelay.value)
            
        

    
    def _nemesisEI__evStart(self):
        if self.emm_timer.isActive():
            self.emm_timer.stop()
        
        if self.ecm_timer.isActive():
            self.ecm_timer.stop()
        
        self.displayClean()

    
    def _nemesisEI__evTunedIn(self):
        service = self.session.nav.getCurrentService()
        if service:
            pass
        info = service.info()
        if info is not None:
            if not self.emm_timer.isActive():
                self.ecmTimeStep = 0
                self.emm_timer.start(config.nemesis.emminfodelay.value)
            
            if not self.ecm_timer.isActive():
                self.ecm_timer.start(config.nemesis.ecminfodelay.value)
            
        

    
    def _nemesisEI__updateEMMInfo(self):
        self.emm_timer.stop()
        service = self.session.nav.getCurrentService()
        if service:
            pass
        info = service.info()
        if info is not None:
            self.showEMM(info.getInfoObject(iServiceInformation.sCAIDs))
        

    
    def _nemesisEI__updateEmuInfo(self):
        service = self.session.nav.getCurrentService()
        if service:
            pass
        info = service.info()
        self.cleandecInfo()
        if info is not None:
            if info.getInfo(iServiceInformation.sIsCrypted):
                self.showEmuName()
                print '[self.ecmTimeStep]', self.ecmTimeStep
                if self.ecmTimeStep >= 5:
                    self.ecm_timer.changeInterval(11000)
                else:
                    self.ecmTimeStep += 1
                info = parse_ecm(self.readEcmFile())
                if info != 0:
                    caid = info[0]
                    pid = info[1]
                    provid = info[2]
                    ecmtime = info[3]
                    source = info[4]
                    addr = info[5]
                    port = info[6]
                    hops = info[7]
                    reader = info[8]
                    protocol = info[9]
                    if ecmtime > 0:
                        self['ecmtime'].setText('ECM Time: %s msec' % str(ecmtime))
                    
                    if provid != '':
                        self['EmuInfo'].setText('ProvID: %s ' % provid)
                    else:
                        self['EmuInfo'].setText('')
                    if pid != '':
                        self['EmuInfo'].setText('%sPID: %s ' % (self['EmuInfo'].getText(), pid))
                    
                    if caid != '':
                        self['EmuInfo'].setText('%sCaID: %s' % (self['EmuInfo'].getText(), caid))
                        self.showECM(caid)
                    
                    if source == 0:
                        self['EmuInfo'].setText('Decode: Unsupported!')
                        self['ecm_pict'].show()
                        self['ecm_pict'].instance.setPixmapFromFile(self.findPicon('unknown'))
                    elif source == 1:
                        self['b_emu'].show()
                        self['netcard'].setText('Decode: Internal')
                    elif source == 2:
                        if addr != '':
                            if addr.find('127.0.0.1') != -1 or addr.find('localhost') != -1:
                                self['netcard'].setText('Decode: Internal')
                                self['b_card'].show()
                            else:
                                self['b_spider'].show()
                                if config.nemesis.shownetdet.value:
                                    if port != '':
                                        self['netcard'].setText('Source: %s:%s' % (addr, port))
                                    else:
                                        self['netcard'].setText('Source: %s' % addr)
                                    if hops > 0:
                                        self['hops'].setText('Hops: %s' % str(hops))
                                    
                                    if protocol != '':
                                        self['reader'].setText('Protocol: %s ' % str(protocol))
                                    
                                    if reader != '' and protocol != '':
                                        self['reader'].setText('%sReader: %s' % (self['reader'].getText(), str(reader)))
                                    elif reader != '':
                                        self['reader'].setText('Reader: %s' % str(reader))
                                    
                                else:
                                    self['netcard'].setText('Decode: Network')
                        else:
                            self['b_spider'].show()
                            self['netcard'].setText('Decode: Network')
                    elif source == 3:
                        self['b_card'].show()
                        self['netcard'].setText('Decode: %s' % str(reader))
                    elif source == 4:
                        self['b_card'].show()
                        self['netcard'].setText('Decode: slot-1')
                    elif source == 5:
                        self['b_card'].show()
                        self['netcard'].setText('Decode: slot-2')
                    
                else:
                    self['EmuInfo'].setText('Decode: Unsupported!')
                    self['ecm_pict'].show()
                    self['ecm_pict'].instance.setPixmapFromFile(self.findPicon('unknown'))
            else:
                self['hops'].setText('')
                self['emuname'].setText('')
                self['EmuInfo'].setText('')
                self['ecmtime'].setText('')
                self['netcard'].setText('')
                self['reader'].setText('')
                self['b_fta'].show()
                self['ecm_pict'].show()
                self['ecm_pict'].instance.setPixmapFromFile(self.findPicon('fta'))
        

    
    def int2hex(self, int):
        return '%x' % int

    
    def showECM(self, caid):
        caid = caid.lower()
        if caid.__contains__('x'):
            idx = caid.index('x')
            caid = caid[idx + 1:]
            if len(caid) == 3:
                caid = '0%s' % caid
            
            caid = caid[:2]
            caid = caid.upper()
            if self.systemCaids.has_key(caid):
                system = self.systemCaids.get(caid)
                self[system].setForegroundColorNum(2)
                pngname = self.findPicon(system)
                if pngname == '':
                    pngname = self.findPicon('unknown')
                
                self['ecm_pict'].show()
                self['ecm_pict'].instance.setPixmapFromFile(pngname)
            
        

    
    def showEMM(self, caids):
        if caids:
            if len(caids) > 0:
                for caid in caids:
                    caid = self.int2hex(caid)
                    if len(caid) == 3:
                        caid = '0%s' % caid
                    
                    caid = caid[:2]
                    caid = caid.upper()
                    if self.systemCaids.has_key(caid):
                        self[self.systemCaids.get(caid)].setForegroundColorNum(1)
                        continue
                
            
        

    
    def findPicon(self, codName):
        if config.nemesis.usepiconinhdd.value:
            searchPaths = ('/media/hdd/%s/', eEnv.resolve('${datadir}/%s/'), '/media/usb/%s/', '/media/cf/%s/')
        else:
            searchPaths = (eEnv.resolve('${datadir}/%s/'), '/media/usb/%s/', '/media/cf/%s/')
        for path in searchPaths:
            pngname = path % self.path + codName + '.png'
            if fileExists(pngname):
                return pngname
        return ''

    
    def cleandecInfo(self):
        self['b_fta'].hide()
        self['b_card'].hide()
        self['b_emu'].hide()
        self['b_spider'].hide()

    
    def displayClean(self):
        self['ecm_pict'].hide()
        self['hops'].setText('')
        self['reader'].setText('')
        self['emuname'].setText('')
        self['EmuInfo'].setText('')
        self['ecmtime'].setText('')
        self['netcard'].setText('')
        for x in self.systemState:
            self[x].hide()
        for x in self.systemCod:
            self[x].setForegroundColorNum(0)

    
    def _nemesisEI__evUpdatedInfo(self):
        self['TunerInfo'].setText('')
        self['SatInfo'].setText('')
        service = self.session.nav.getCurrentService()
        frontendInfo = service.frontendInfo()
        if frontendInfo:
            pass
        frontendData = frontendInfo.getAll(True)
        if frontendData is not None:
            tuner_type = frontendData.get('tuner_type', 'None')
            sr = str(int(frontendData.get('symbol_rate', 0) / 1000))
            freq = str(int(frontendData.get('frequency', 0) / 1000))
            if tuner_type == 'DVB-S' or tuner_type == 'DVB-S2':
                
                try:
                    orb = {
                        3590: 'Thor/Intelsat (1.0\xc2\xb0W)',
                        3560: 'Amos 2/3 (4.0\xc2\xb0W)',
                        3550: 'Atlantic Bird 3 (5.0\xc2\xb0W)',
                        3530: 'Nilesat/Atlantic Bird (7.0\xc2\xb0W)',
                        3520: 'Atlantic Bird 2 (8.0\xc2\xb0W)',
                        3475: 'Atlantic Bird 1 (12.5\xc2\xb0W)',
                        3460: 'Express A4 (14.0\xc2\xb0W)',
                        3450: 'Telstar 12 (15.0\xc2\xb0W)',
                        3420: 'Intelsat 901 (18.0\xc2\xb0W)',
                        3380: 'Nss 7 (22.0\xc2\xb0W)',
                        3355: 'Intelsat 905 (24.5\xc2\xb0W)',
                        3325: 'Intelsat 907 (27.5\xc2\xb0W)',
                        3300: 'Hispasat 1C/1D (30.0\xc2\xb0W)',
                        3170: 'Intelsat 11 (43.0\xc2\xb0W)',
                        3150: 'Intelsat 14 (IS-14) (45.0\xc2\xb0W)',
                        3070: 'Intelsat 707 (53.0\xc2\xb0W)',
                        3045: 'Intelsat 805 (55.5\xc2\xb0W)',
                        3020: 'Intelsat 9 (58.0\xc2\xb0W)',
                        2990: 'Amazonas (61.0\xc2\xb0W)',
                        2900: 'Star One C2 (70.0\xc2\xb0W)',
                        2875: 'Nimiq 5 (72.7\xc2\xb0W)',
                        2780: 'NIMIQ 4 (82.0\xc2\xb0W)',
                        2690: 'NIMIQ 1 (91.0\xc2\xb0W)',
                        3592: 'Thor/Intelsat (0.8\xc2\xb0W)',
                        2985: 'EchoStar 12/15 (61.5\xc2\xb0W)',
                        2830: 'Echostar 4/8 (77.0\xc2\xb0W)',
                        2500: 'Echostar 10/11 (110.0\xc2\xb0W)',
                        2502: 'Echostar 10/11 (110.0\xc2\xb0W)',
                        2410: 'Echostar/Anik F3 (119.0\xc2\xb0W)',
                        2391: 'Galaxy 23 (121.0\xc2\xb0W)',
                        2390: 'Echostar 9 (121.0\xc2\xb0W)',
                        2412: 'DirectTV 7S (119.0\xc2\xb0W)',
                        2310: 'Galaxy 27 (129.0\xc2\xb0W)',
                        2311: 'Ciel 2 (129.0\xc2\xb0W)',
                        2120: 'Echostar 2 (148.0\xc2\xb0W)',
                        1100: 'BSAT 2A (110.0\xc2\xb0E)',
                        1101: 'N-Sat 110 (110.0\xc2\xb0E)',
                        1131: 'KoreaSat 5 (113.0\xc2\xb0E)',
                        1440: 'SuperBird C2 (144.0\xc2\xb0E)',
                        1006: 'AsiaSat 5 (100.5\xc2\xb0E)',
                        1056: 'Asiasat 3S (105.5\xc2\xb0E)',
                        1082: 'NSS 11 (108.2\xc2\xb0E)',
                        881: 'ST1 (88.0\xc2\xb0E)',
                        917: 'Measat 3 (91.5\xc2\xb0E)',
                        950: 'Insat 4B (95.0\xc2\xb0E)',
                        951: 'NSS 6 (95.0\xc2\xb0E)',
                        765: 'Apstar 2R (76.5\xc2\xb0E)',
                        785: 'ThaiCom 5 (78.5\xc2\xb0E)',
                        800: 'Express (80.0\xc2\xb0E)',
                        830: 'Insat 4A (83.0\xc2\xb0E)',
                        850: 'Intelsat 15 (85.2\xc2\xb0E)',
                        750: 'Abs 1 (75.0\xc2\xb0E)',
                        720: 'Intelsat (72.0\xc2\xb0E)',
                        705: 'Eutelsat W5 (70.5\xc2\xb0E)',
                        685: 'Intelsat 7/10 (68.5\xc2\xb0E)',
                        620: 'Intelsat 902 (62.0\xc2\xb0E)',
                        600: 'Intelsat 904 (60.0\xc2\xb0E)',
                        570: 'Nss 12 (57.0\xc2\xb0E)',
                        530: 'Express AM22 (53.0\xc2\xb0E)',
                        482: 'Eutelsat W48 (48.2\xc2\xb0E)',
                        450: 'Intelsat 12 (45.0\xc2\xb0E)',
                        420: 'Turksat 2A/3A (42.0\xc2\xb0E)',
                        400: 'Express AM1 (40.0\xc2\xb0E)',
                        390: 'Hellas Sat 2 (39.0\xc2\xb0E)',
                        380: 'Paksat 1 (38.0\xc2\xb0E)',
                        360: 'Eutelsat W4/W7 (36.0\xc2\xb0E)',
                        335: 'Astra 1M (33.5\xc2\xb0E)',
                        330: 'Eurobird 3 (33.0\xc2\xb0E)',
                        328: 'Galaxy 11 (32.8\xc2\xb0E)',
                        315: 'Astra 1G (31.5\xc2\xb0E)',
                        310: 'Turksat (31.0\xc2\xb0E)',
                        305: 'Arabsat 5A (30.5\xc2\xb0E)',
                        285: 'Eurobird/Astra (28.5\xc2\xb0E)',
                        284: 'Eurobird/Astra (28.2\xc2\xb0E)',
                        282: 'Eurobird/Astra (28.2\xc2\xb0E)',
                        1220: 'AsiaSat 4 (122.0\xc2\xb0E)',
                        1380: 'Telstar 18 (138.0\xc2\xb0E)',
                        260: 'Badr 6 (26.0\xc2\xb0E)',
                        255: 'Eurobird 2 (25.5\xc2\xb0E)',
                        232: 'Astra 3A/3B (23.5\xc2\xb0E)',
                        235: 'Astra 3A/3B (23.5\xc2\xb0E)',
                        215: 'Eutelsat W6 (21.5\xc2\xb0E)',
                        216: 'Eutelsat W6 (21.6\xc2\xb0E)',
                        210: 'AfriStar 1 (21.0\xc2\xb0E)',
                        192: 'Astra 1M/1H/1L/1KR (19.2\xc2\xb0E)',
                        160: 'Eutelsat W2M/16A/Sesat (16.0\xc2\xb0E)',
                        130: 'Hot Bird 6/8/9 (13.0\xc2\xb0E)',
                        100: 'Eutelsat W2A (10.0\xc2\xb0E)',
                        90: 'Eurobird 9A (9.0\xc2\xb0E)',
                        70: 'Eutelsat W3A (7.0\xc2\xb0E)',
                        50: 'Sirius 4 (5.0\xc2\xb0E)',
                        48: 'Astra 4A (4.8\xc2\xb0E)',
                        40: 'Eurobird 4A (4.0\xc2\xb0E)',
                        30: 'Telecom 2 (3.0\xc2\xb0E)',
                        852: 'Intelsat 15 (85.2\xc2\xb0E)',
                        660: 'Intelsat 17 (66.0\xc2\xb0E)',
                        3490: 'Express AM44 (11.0\xc2\xb0W)' }[frontendData.get('orbital_position', 'None')]
                except:
                    orb = 'Unsupported SAT: %s' % str([
                        frontendData.get('orbital_position', 'None')])

                pol = {
                    eDVBFrontendParametersSatellite.Polarisation_Horizontal: 'H',
                    eDVBFrontendParametersSatellite.Polarisation_Vertical: 'V',
                    eDVBFrontendParametersSatellite.Polarisation_CircularLeft: 'CL',
                    eDVBFrontendParametersSatellite.Polarisation_CircularRight: 'CR' }[frontendData.get('polarization', eDVBFrontendParametersSatellite.Polarisation_Horizontal)]
                fec = {
                    eDVBFrontendParametersSatellite.FEC_None: 'None',
                    eDVBFrontendParametersSatellite.FEC_Auto: 'Auto',
                    eDVBFrontendParametersSatellite.FEC_1_2: '1/2',
                    eDVBFrontendParametersSatellite.FEC_2_3: '2/3',
                    eDVBFrontendParametersSatellite.FEC_3_4: '3/4',
                    eDVBFrontendParametersSatellite.FEC_5_6: '5/6',
                    eDVBFrontendParametersSatellite.FEC_7_8: '7/8',
                    eDVBFrontendParametersSatellite.FEC_3_5: '3/5',
                    eDVBFrontendParametersSatellite.FEC_4_5: '4/5',
                    eDVBFrontendParametersSatellite.FEC_8_9: '8/9',
                    eDVBFrontendParametersSatellite.FEC_9_10: '9/10' }[frontendData.get('fec_inner', eDVBFrontendParametersSatellite.FEC_Auto)]
                self['TunerInfo'].setText('Freq: ' + freq + ' MHz, Pol: ' + pol + ', Fec: ' + fec + ', SR: ' + sr)
                self['SatInfo'].setText('Satellite: ' + orb)
            elif tuner_type == 'DVB-C':
                fec = {
                    eDVBFrontendParametersCable.FEC_None: 'None',
                    eDVBFrontendParametersCable.FEC_Auto: 'Auto',
                    eDVBFrontendParametersCable.FEC_1_2: '1/2',
                    eDVBFrontendParametersCable.FEC_2_3: '2/3',
                    eDVBFrontendParametersCable.FEC_3_4: '3/4',
                    eDVBFrontendParametersCable.FEC_5_6: '5/6',
                    eDVBFrontendParametersCable.FEC_7_8: '7/8',
                    eDVBFrontendParametersCable.FEC_8_9: '8/9' }[frontendData.get('fec_inner', eDVBFrontendParametersCable.FEC_Auto)]
                self['TunerInfo'].setText('Freq: ' + freq + ' MHz, Fec: ' + fec + ', SR: ' + sr)
            elif tuner_type == 'DVB-T':
                pol = {
                    eDVBFrontendParametersTerrestrial.Modulation_Auto: 'Auto',
                    eDVBFrontendParametersTerrestrial.Modulation_QPSK: 'QPSK',
                    eDVBFrontendParametersTerrestrial.Modulation_QAM16: 'QAM16',
                    eDVBFrontendParametersTerrestrial.Modulation_QAM64: 'QAM64' }[frontendData.get('constellation', eDVBFrontendParametersTerrestrial.Modulation_Auto)]
                fec = {
                    eDVBFrontendParametersTerrestrial.FEC_Auto: 'Auto',
                    eDVBFrontendParametersTerrestrial.FEC_1_2: '1/2',
                    eDVBFrontendParametersTerrestrial.FEC_2_3: '2/3',
                    eDVBFrontendParametersTerrestrial.FEC_3_4: '3/4',
                    eDVBFrontendParametersTerrestrial.FEC_5_6: '5/6',
                    eDVBFrontendParametersTerrestrial.FEC_7_8: '7/8' }[frontendData.get('code_rate_lp', eDVBFrontendParametersTerrestrial.FEC_Auto)]
                self['TunerInfo'].setText('Freq: ' + freq + ' MHz, Fec: ' + fec + ', SR: ' + sr)
                self['SatInfo'].setText('Constellation: ' + pol)
            else:
                self['TunerInfo'].setText('Freq: ' + freq + ' MHz, SR: ' + sr)
        


