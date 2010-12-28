import os
import re
import sys

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import danishaddons
import danishaddons.web

BASE_URL = 'http://www.dr.dk/netradio/wmp.asp'

def showChannels():
    html = danishaddons.web.downloadAndCacheUrl(BASE_URL, os.path.join(danishaddons.ADDON_DATA_PATH, 'channels.html'), 24 * 60)
    icon = os.path.join(os.getcwd(), 'icon.png')

    for m in re.finditer('<td nowrap="nowrap">(.*?)</td>.*?\n.*?<a href="([^"]+)">%s</a>' % getQuality(), html):
        name = danishaddons.web.decodeHtmlEntities(m.group(1))
        asxUrl = m.group(2)

        item = xbmcgui.ListItem(name, iconImage = icon)
        item.setProperty('IsPlayable', 'true')
        item.setInfo(type = 'audio', infoLabels = {
            'title' : name
        })
        url = danishaddons.ADDON_PATH + '?url=' + asxUrl
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item)

    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)

def playStream(url):
    playlist = danishaddons.web.downloadUrl(url)
    m = re.search('<TITLE>(.*?)</TITLE>.*?<Ref href="(.*?)"/>', playlist, re.DOTALL)
    
    title = m.group(1)
    streamUrl = m.group(2)

    item = xbmcgui.ListItem(path = streamUrl)
    item.setInfo('music', {
        'artist' : 'DR',
        'title' : title
    })
    xbmcplugin.setResolvedUrl(danishaddons.ADDON_HANDLE, True, item)


def getQuality():
    quality = danishaddons.ADDON.getSetting('quality')
    if quality == 'High':
        return 'H\&oslash;j'
    elif quality == 'Medium':
        return 'Mellem'
    else:
        return 'Lav'

if __name__ == '__main__':
    danishaddons.init(sys.argv)

    if danishaddons.ADDON_PARAMS.has_key('url'):
        playStream(danishaddons.ADDON_PARAMS['url'])
    else:
        showChannels()

