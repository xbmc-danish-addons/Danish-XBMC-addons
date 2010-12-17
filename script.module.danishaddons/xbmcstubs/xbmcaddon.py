__author__ = 'twi'

import tempfile
import os

class Addon:
    def __init__(self, id):
        self.id = id

    def getAddonInfo(self, id):
        if(id.lower() == 'profile'): # Profile path
            dir = os.path.join(tempfile.gettempdir(), self.id)
            if(not os.path.isdir(dir)):
                os.makedirs(dir)
            return dir

    def getLocalizedString(self, id):
        return "localizedString_%d" % id

  