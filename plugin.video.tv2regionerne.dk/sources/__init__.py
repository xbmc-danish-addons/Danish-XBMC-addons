import xbmcgui
import xbmcplugin
import danishaddons

def chooseDate(callback):
    d = xbmcgui.Dialog()
    date = d.numeric(1, danishaddons.msg(30001))
    if date is not None:
        callback(date.replace(' ', ''))

def addChooseDateItem(slug):
    item = xbmcgui.ListItem(danishaddons.msg(30001))
    url = danishaddons.ADDON_PATH + '?slug=%s&date' % slug
    xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, True)

