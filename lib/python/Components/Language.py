import gettext

from Tools.Directories import SCOPE_LANGUAGE, resolveFilename, fileExists

import language_cache

class Language:
	def __init__(self):
		gettext.install('enigma2', resolveFilename(SCOPE_LANGUAGE, ""), unicode=0, codeset="utf-8")
		self.activeLanguage = 0
		self.lang = {}
		self.langlist = []
		# FIXME make list dynamically
		# name, iso-639 language, iso-3166 country. Please don't mix language&country!
		# also, see "precalcLanguageList" below on how to re-create the language cache after you added a language
		language_path = "/usr/share/enigma2/po/%s/LC_MESSAGES/enigma2.mo"
		if fileExists(language_path % "en"):
			self.addLanguage(_("English"), "en", "EN")
		if fileExists(language_path % "de"):
			self.addLanguage(_("German"), "de", "DE")
		if fileExists(language_path % "ar"):
			self.addLanguage(_("Arabic"), "ar", "AE")
		if fileExists(language_path % "ca"):
			self.addLanguage(_("Catalan"), "ca", "AD")
		if fileExists(language_path % "hr"):
			self.addLanguage(_("Croatian"), "hr", "HR")
		if fileExists(language_path % "cs"):
			self.addLanguage(_("Czech"), "cs", "CZ")
		if fileExists(language_path % "da"):
			self.addLanguage(_("Danish"), "da", "DK")
		if fileExists(language_path % "nl"):
			self.addLanguage(_("Dutch"), "nl", "NL")
		if fileExists(language_path % "et"):
			self.addLanguage(_("Estonian"), "et", "EE")
		if fileExists(language_path % "fi"):
			self.addLanguage(_("Finnish"), "fi", "FI")
		if fileExists(language_path % "fr"):
			self.addLanguage(_("French"), "fr", "FR")
		if fileExists(language_path % "el"):
			self.addLanguage(_("Greek"), "el", "GR")
		if fileExists(language_path % "hu"):
			self.addLanguage(_("Hungarian"), "hu", "HU")
		if fileExists(language_path % "lt"):
			self.addLanguage(_("Lithuanian"), "lt", "LT")
		if fileExists(language_path % "lv"):
			self.addLanguage(_("Latvian"), "lv", "LV")
		if fileExists(language_path % "is"):
			self.addLanguage(_("Icelandic"), "is", "IS")
		if fileExists(language_path % "it"):
			self.addLanguage(_("Italian"), "it", "IT")
		if fileExists(language_path % "no"):
			self.addLanguage(_("Norwegian"), "no", "NO")
		if fileExists(language_path % "pl"):
			self.addLanguage(_("Polish"), "pl", "PL")
		if fileExists(language_path % "pt"):
			self.addLanguage(_("Portuguese"), "pt", "PT")
		if fileExists(language_path % "ru"):
			self.addLanguage(_("Russian"), "ru", "RU")
		if fileExists(language_path % "sr"):
			self.addLanguage(_("Serbian"), "sr", "YU")
		if fileExists(language_path % "sk"):
			self.addLanguage(_("Slovakian"), "sk", "SK")
		if fileExists(language_path % "sl"):
			self.addLanguage(_("Slovenian"), "sl", "SI")
		if fileExists(language_path % "es"):
			self.addLanguage(_("Spanish"), "es", "ES")
		if fileExists(language_path % "sv"):
			self.addLanguage(_("Swedish"), "sv", "SE")
		if fileExists(language_path % "tr"):
			self.addLanguage(_("Turkish"), "tr", "TR")
		if fileExists(language_path % "uk"):
			self.addLanguage(_("Ukrainian"), "uk", "UA")
		if fileExists(language_path % "fy"):
			self.addLanguage(_("Frisian"), "fy", "x-FY") # there is no separate country for frisian

		self.callbacks = []

	def addLanguage(self, name, lang, country):
		try:
			self.lang[str(lang + "_" + country)] = ((_(name), lang, country))
			self.langlist.append(str(lang + "_" + country))
		except:
			print "Language " + str(name) + " not found"

	def activateLanguage(self, index):
		try:
			lang = self.lang[index]
			print "Activating language " + lang[0]
			gettext.translation('enigma2', resolveFilename(SCOPE_LANGUAGE, ""), languages=[lang[1]]).install()
			self.activeLanguage = index
			for x in self.callbacks:
				x()
		except:
			print "Selected language does not exist!"
			lang = self.lang["en_EN"]
			print "Activating default language " + lang[0]
			gettext.translation('enigma2', resolveFilename(SCOPE_LANGUAGE, ""), languages=[lang[1]]).install()
			self.activeLanguage = "en_EN"
			for x in self.callbacks:
				x()

	def activateLanguageIndex(self, index):
		if index < len(self.langlist):
			self.activateLanguage(self.langlist[index])

	def getLanguageList(self):
		return [ (x, self.lang[x]) for x in self.langlist ]

	def getActiveLanguage(self):
		return self.activeLanguage
	
	def getActiveLanguageIndex(self):
		idx = 0
		for x in self.langlist:
			if x == self.activeLanguage:
				return idx
			idx += 1
		return 0

	def getLanguage(self):
		try:
			return str(self.lang[self.activeLanguage][1]) + "_" + str(self.lang[self.activeLanguage][2])
		except:
			return 'en_EN'

	def addCallback(self, callback):
		self.callbacks.append(callback)

	def precalcLanguageList(self):
		# excuse me for those T1, T2 hacks please. The goal was to keep the language_cache.py as small as possible, *and* 
		# don't duplicate these strings.
		T1 = _("Please use the UP and DOWN keys to select your language. Afterwards press the OK button.")
		T2 = _("Language selection")
		l = open("language_cache.py", "w")
		print >>l, "# -*- coding: UTF-8 -*-"
		print >>l, "LANG_TEXT = {"
		for language in self.langlist:
			self.activateLanguage(language)
			print >>l, '"%s": {' % language
			for name, lang, country in self.lang.values():
				print >>l, '\t"%s_%s": "%s",' % (lang, country, _(name))

			print >>l, '\t"T1": "%s",' % (_(T1))
			print >>l, '\t"T2": "%s",' % (_(T2))
			print >>l, '},'
		print >>l, "}"

language = Language()
