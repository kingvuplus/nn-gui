##
## Picon renderer by Gruffy .. some speedups by Ghost
##
from Components.config import config
from Renderer import Renderer
from enigma import ePixmap, eEnv, iServiceInformation, iPlayableService, iPlayableServicePtr
from Tools.Directories import fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN, resolveFilename

class Picon(Renderer):
	def __init__(self):
		Renderer.__init__(self)
		self.path = "picon"
		self.nameCache = { }
		self.pngname = ""

	def getServiceInfoValue(self, info, what, ref=None):
		v = ref and info.getInfo(ref, what) or info.getInfo(what)
		if v != iServiceInformation.resIsString:
			return "N/A"
		return ref and info.getInfoString(ref, what) or info.getInfoString(what)
	
	def applySkin(self, desktop, parent):
		attribs = [ ]
		for (attrib, value) in self.skinAttributes:
			if attrib == "path":
				self.path = value
			else:
				attribs.append((attrib,value))
		self.skinAttributes = attribs
		return Renderer.applySkin(self, desktop, parent)

	GUI_WIDGET = ePixmap

	def changed(self, what):
		if self.instance:
			pngname = ""
			if what[0] != self.CHANGED_CLEAR:
				service = self.source.service
				if isinstance(service, iPlayableServicePtr):
					info = service and service.info()
					ref = None
				else: # reference
					info = service and self.source.info
					ref = service
				if info is None:
					return ""
				if self.path == "picon":
					piconType = config.nemesis.picontype.value
				else:
					piconType = config.nemesis.piconlcdtype.value
				if  piconType == "Reference":
					sname = self.getServiceInfoValue(info, iServiceInformation.sServiceref, ref)
					# strip all after last :
					pos = sname.rfind(':')
					if pos != -1:
						sname = sname[:pos].rstrip(':').replace(':','_')
				else:
					name = ref and info.getName(ref)
					if name is None:
						name = info.getName()
					sname = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
				pngname = self.nameCache.get(sname, "")
				if pngname == "":
					pngname = self.findPicon(sname)
					if pngname != "":
						self.nameCache[sname] = pngname
			if pngname == "": # no picon for service found
				pngname = self.nameCache.get("default", "")
				if pngname == "": # no default yet in cache..
					pngname = self.findPicon("picon_default")
					if pngname == "":
						tmp = resolveFilename(SCOPE_CURRENT_SKIN, "picon_default.png")
						if fileExists(tmp):
							pngname = tmp
						else:
							pngname = resolveFilename(SCOPE_SKIN_IMAGE, "skin_default/picon_default.png")
					self.nameCache["default"] = pngname
			if self.pngname != pngname:
				self.instance.setPixmapFromFile(pngname)
				self.pngname = pngname

	def findPicon(self, serviceName):
		if config.nemesis.usepiconinhdd.value:
			searchPaths = ('/media/hdd/%s/', eEnv.resolve('${datadir}/enigma2/%s/'),'/media/cf/%s/','/media/usb/%s/')
		else:
			searchPaths = (eEnv.resolve('${datadir}/enigma2/%s/'),'/media/usb/%s/','/media/cf/%s/')

		for path in searchPaths:
			pngname = (path % self.path) + serviceName + ".png"
			if fileExists(pngname):
				return pngname
		return ""
