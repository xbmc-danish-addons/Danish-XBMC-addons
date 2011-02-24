__author__ = 'twi'

def lock():
    pass

def unlock():
    pass

class WindowXML():
    def __init__(self, xmlFilename, scriptPath, defaultSkin = 'Default', forceFallback = False):
        pass

    def close(self):
        pass

    def getControl(self, controlId):
        return Control(0, 0, 100, 100, 'Dummy Control')

    def doModal(self):
        pass

    def getFocusId(self):
        pass

    def setFocusId(self, controlId):
        pass

class WindowXMLDialog(WindowXML):
    def __init__(self, xmlFilename, scriptPath, defaultSkin = 'Default', forceFallback = False):
        pass

class Control():
    def __init__(self, x, y, width, height, label, focusTexture = None, noFocusTexture = None,
                 textOffsetX = None, textOffsetY = None, alignment = None, font = None, textColor = None,
                 disabledColor = None, angle = None, shadowColor = None, focusedColor = None):
        pass

    def setLabel(self, label = None, font = None, textColor = None, disabledColor = None, shadowColor = None, focusedColor = None):
        pass

class Dialog():
    def __init__(self):
        pass

    def ok(self, line1 = None, line2 = None, line3 = None):
        pass


class DialogProgress():
    def __init__(self):
        pass

    def create(self, title):
        return DialogProgress()

    def update(handle, progress, line1 = None, line2 = None, line3 = None):
        pass

    def close(self):
        pass

    def iscanceled(self):
        return False


class ListItem():
    def __init__(self, title = None, iconImage = None, thumbnailImage = None, path = None):
        self.title = title
        self.iconImage = iconImage
        self.url = path

    def setInfo(self, type, infoLabels):
        pass

    def setLabel2(self, label2):
        self.label2 = label2

    def setProperty(self, property, value):
        pass

    def addContextMenuItems(self, script, args = None):
        pass