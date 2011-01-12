import os
import sys

import xbmc
import xbmcgui
import xbmcplugin

import danishaddons
import danishaddons.web

from elementtree import ElementTree

BASE_URL = 'http://www.vegaplayer.dk/%s'
CONCERTS_URL = BASE_URL % 'concerts.jsp'
CONCERT_URL = BASE_URL % 'concert.jsp?id=%s'
RTMP_URL = 'rtmp://vegasrv1.dedicated.cohaesio.net/vod/vod/%s'

def listConcerts():
    concertsXml = danishaddons.web.downloadAndCacheUrl(CONCERTS_URL,
            os.path.join(danishaddons.ADDON_DATA_PATH, 'concerts.xml'), 24 * 60)
    doc = ElementTree.fromstring(concertsXml)

    for concert in doc.findall('concert'):
        infoLabels = {
            'plotoutline': concert.findtext('venue'),
            'date' : concert.findtext('date'),
            'year' : int(concert.findtext('date')[-4:]),
            'title' : concert.findtext('name') + ' - ' + concert.findtext('date')
        }

        iconImage = BASE_URL % concert.findtext('teaserimage')
        item = xbmcgui.ListItem(infoLabels['title'], iconImage=iconImage)
        item.setProperty('Fanart_Image', iconImage)
        item.setInfo('video', infoLabels)
        url = danishaddons.ADDON_PATH + '?uuid=' + concert.attrib.get('id')
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, isFolder=True)

    xbmcplugin.addSortMethod(danishaddons.ADDON_HANDLE, xbmcplugin.SORT_METHOD_TITLE)
    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)


def listConcert(uuid):
    concertXml = danishaddons.web.downloadAndCacheUrl(CONCERT_URL % uuid,
            os.path.join(danishaddons.ADDON_DATA_PATH, 'concert_%s.xml' % uuid), 24 * 60)
    doc = ElementTree.fromstring(concertXml)

    iconImage = BASE_URL % doc.findtext('concert/teaserimage')
    description = doc.findtext('concert/name') + ' - ' + (doc.findtext('concert/venue') + ' - ' + doc.findtext('concert/date'))
    artistPrefix = doc.findtext('concert/name') + ' - %s'
    startTimes = list()
    for track in doc.findall('tracks/track'):
        startTimes.append(int(track.attrib.get('startms')) / 1000)
    startTimes.append(startTimes[len(startTimes)-1])

    idx = 0
    for track in doc.findall('tracks/track'):
        startSeconds = int(track.attrib.get('startms')) / 1000
        durationSeconds = startTimes[idx + 1] - startSeconds

        infoLabels = {
            'title' : artistPrefix % track.findtext('name'),
            'duration' : str(durationSeconds / 60),
            'plotoutline' : description
        }

        item = xbmcgui.ListItem(infoLabels['title'], iconImage=iconImage)
        item.setProperty('Fanart_Image', iconImage)
        item.setInfo('video', infoLabels)
        url = danishaddons.ADDON_PATH + '?uuid=%s&start=%d' % (uuid, startSeconds)
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item)

        idx += 1

    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)


def playVideo(uuid, startSeconds):
    concertXml = danishaddons.web.downloadAndCacheUrl(CONCERT_URL % uuid,
            os.path.join(danishaddons.ADDON_DATA_PATH, 'concert_%s.xml' % uuid), 24 * 60)
    doc = ElementTree.fromstring(concertXml)

    description = doc.findtext('concert/name') + ' - ' + (doc.findtext('concert/venue') + ' - ' + doc.findtext('concert/date'))
    url = RTMP_URL % doc.findtext('concert/stream')[4:]

    iconImage = BASE_URL % doc.findtext('concert/teaserimage')
    item = xbmcgui.ListItem(description, thumbnailImage = iconImage)

    player = xbmc.Player()
    player.play(url, item)

    startTime = int(startSeconds)
    if startTime > 0:
        for i in range(5):
            if player.isPlaying():
                player.seekTime(startTime)
                break
            xbmc.sleep(1000)

if __name__ == '__main__':
    danishaddons.init(sys.argv)

    if danishaddons.ADDON_PARAMS.has_key('start'):
        playVideo(danishaddons.ADDON_PARAMS['uuid'], danishaddons.ADDON_PARAMS['start'])

    elif danishaddons.ADDON_PARAMS.has_key('uuid'):
        listConcert(danishaddons.ADDON_PARAMS['uuid'])

    else:
        listConcerts()

