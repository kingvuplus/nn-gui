from Renderer import Renderer
from enigma import eLabel
from Components.VariableText import VariableText

class NemesisEmptyEpg(VariableText, Renderer):
    
    def __init__(self):
        Renderer.__init__(self)
        VariableText.__init__(self)

    GUI_WIDGET = eLabel
    
    def connect(self, source):
        Renderer.connect(self, source)
        self.changed((self.CHANGED_DEFAULT,))

    
    def changed(self, what):
        if what[0] == self.CHANGED_CLEAR:
            self.text = ''
        else:
            self.text = self.source.text
            if len(self.text) > 25:
                self.text = self.text[:29] + '...'
            elif self.text == '':
                self.text = 'No EPG data available'
            


