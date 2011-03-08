# coding = 'utf-8'
import re
import sys
import simplejson
import os

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import danishaddons
import danishaddons.web

KEY_TO_TITLE = {
    'beep' : 'Beep - Gadgets',
    'sport' : 'Sporten',
    'station2' : 'Station 2',
    'zulu' : 'Zulu',
    'tour2009' : 'Tour de France 2009',
    'mogensen-kristiansen' : 'Mogensen & Kristiansen',
    'news-finans' : 'News Finansmagasinet',
    'nyheder' : 'Nyhederne',
    'most-viewed' : 'Mest sete',
    'go' : 'Go\' Morgen / Aften',
    'programmer' : 'Programmer',
    'finans' : 'Finans',
    'musik' : 'VIP Musik',
    'latest' : 'Nyeste'
}

BASE_URL = 'http://video.tv2.dk/js/video-list.js.php/index.js'

def showOverview():
    json = loadJson()
    icon = os.path.join(danishaddons.ADDON_PATH, 'icon.png')

    for key in json.keys():
        if KEY_TO_TITLE.has_key(key):
            item = xbmcgui.ListItem(KEY_TO_TITLE[key], iconImage = icon)
        else:
            item = xbmcgui.ListItem(key, iconImage = icon)

        url = danishaddons.ADDON_PATH + '?key=' + key
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, True)

    xbmcplugin.setContent(danishaddons.ADDON_HANDLE, 'tvshows')
    xbmcplugin.addSortMethod(danishaddons.ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)


def showCategory(key):
    json = loadJson()

    for e in json[key]:
        infoLabels = dict()
        if e['headline'] is not None:
            infoLabels['title'] = danishaddons.web.decodeHtmlEntities(e['headline'])
        if e['descr'] is not None:
            infoLabels['plot'] = danishaddons.web.decodeHtmlEntities(e['descr'])
        if e['date'] is not None:
            infoLabels['year'] = int(e['date'][6:])
            infoLabels['date'] = e['date'].replace('-', '.')
        if e['duration'] is not None:
            infoLabels['duration'] = e['duration'][1:9]

        item = xbmcgui.ListItem(infoLabels['title'], iconImage = e['img'])
        item.setInfo('video', infoLabels)
        item.setProperty('IsPlayable', 'true')
        url = danishaddons.ADDON_PATH + '?id=' + str(e['id'])

        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item)

    xbmcplugin.setContent(danishaddons.ADDON_HANDLE, 'episodes')
    xbmcplugin.addSortMethod(danishaddons.ADDON_HANDLE, xbmcplugin.SORT_METHOD_DATE)
    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)


def playVideo(id):
        # retrieve masquarade playlist
        playlist = danishaddons.web.downloadUrl('http://common.tv2.dk/flashplayer/playlistSimple.xml.php/clip-' + id + '.xml')
        m = re.search('video="([^"]+)" materialId="([^"]+)"', playlist)

        # retrive crossdomain to setup next request for geocheck
        danishaddons.web.downloadUrl('http://common-dyn.tv2.dk/crossdomain.xml')

        # retrieve real playlist
        playlist = danishaddons.web.downloadUrl('http://common-dyn.tv2.dk/flashplayer/geocheck.php?id=' + m.group(2) + '&file=' + m.group(1))

        item = xbmcgui.ListItem(path = playlist)
        xbmcplugin.setResolvedUrl(danishaddons.ADDON_HANDLE, True, item)

def loadJson():
    json_path = os.path.join(danishaddons.ADDON_DATA_PATH, 'video.js')
    json = danishaddons.web.downloadAndCacheUrl(BASE_URL, json_path, 60)

    # get json part of js file
    m = re.search('data = (\{.*)\}', json, re.DOTALL)
    # fixup json parsing with simplejson, ie. replace ' with "
    json = re.sub(r'\'([\w-]+)\':', r'"\1":', m.group(1))

    return simplejson.loads(json)


if __name__ == '__main__':
    danishaddons.init(sys.argv)

    if danishaddons.ADDON_PARAMS.has_key('key'):
        showCategory(danishaddons.ADDON_PARAMS['key'])
    elif danishaddons.ADDON_PARAMS.has_key('id'):
        playVideo(danishaddons.ADDON_PARAMS['id'])
    else:
        showOverview()

