__author__ = 'twi'

items = list()
verbose = False

def setContent(handle, type):
    pass

def setPluginCategory(handle, category):
    pass

def addDirectoryItem(handle, url, item, isDirectory):
    item.url = url
    items.append(item)
    if(verbose):
        print "ListItem: %s" % item.title
        print "\turl: %s" % item.url

def endOfDirectory(handle):
    pass


  