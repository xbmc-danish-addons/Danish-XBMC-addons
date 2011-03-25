__author__ = 'twi'

items = list()
verbose = False

SORT_METHOD_LABEL = 1
SORT_METHOD_DATE = 3
SORT_METHOD_TITLE = 9

def setContent(handle, type):
    pass

def setPluginCategory(handle, category):
    pass

def addSortMethod(handle, sortMethod):
    pass

def addDirectoryItem(handle, url, item, isFolder = True):
    item.url = url
    items.append(item)
    if verbose:
        print "ListItem: %s" % item.title
        print "\turl: %s" % item.url

def endOfDirectory(handle, succeeded = True, updateLising = False, cacheToDisc = True):
    pass

def setResolvedUrl(handle, success, item):
    items.append(item)
    if verbose:
        print "ResolvedUrl: %s" % item.url
