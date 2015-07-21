SUBDIRS = countries fonts extensions keymaps hw_info

dist_pkgdata_DATA = \
	encoding.conf \
	keymap.xml \
	menu.xml \
	prev.png \
	radio.mvi \
	black.mvi \
	rcpositions.xml \
	setup.xml \
	skin_subtitles.xml \
	startwizard.xml \
	freesat.t1 \
	freesat.t2 \
	unicable.xml \
	timezone.xml \
	keymap_neutrino.xml \
	nemesis.xml \
	skin.xml \
	skin_default.xml \
	skin_lcd.xml \
	skin_oled.xml \
	skin_sub.xml

if HAVE_TEXTLCD
dist_pkgdata_DATA += skin_text.xml
else
if HAVE_COLORLCD
dist_pkgdata_DATA += skin_display96.xml
else
dist_pkgdata_DATA += skin_display.xml
endif
endif

skin_display.xml: $(srcdir)/skin_display_default.xml
	test -f $(srcdir)/skin_display_$(BOXTYPE).xml && cp $(srcdir)/skin_display_$(BOXTYPE).xml skin_display.xml || cp $(srcdir)/skin_display_default.xml skin_display.xml
