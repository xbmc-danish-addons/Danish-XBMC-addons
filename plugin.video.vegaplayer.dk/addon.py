import sys
import urllib2
import cgi as urlparse

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from elementtree import ElementTree

BASE_URL = 'http://www.vegaplayer.dk/%s'
CONCERTS_URL = BASE_URL % 'concerts.jsp'
CONCERT_URL = BASE_URL % 'concert.jsp?id=%s'
RTMP_URL = 'rtmp://vegasrv1.dedicated.cohaesio.net/vod/vod/%s'

class VegaPlayerAddon(object):
    def listConcerts(self):
        concertsXml = self.downloadUrl(CONCERTS_URL)
        doc = ElementTree.fromstring(concertsXml)

        for concert in doc.findall('concert'):
            infoLabels = {
                'plotoutline': concert.findtext('venue'),
                'date' : concert.findtext('date'),
                'year' : int(concert.findtext('date')[-4:]),
                'title' : concert.findtext('name') + ' - ' + concert.findtext('date')
            }

            teaserImage = BASE_URL % concert.findtext('teaserimage')
            item = xbmcgui.ListItem(infoLabels['title'], iconImage=teaserImage, thumbnailImage=teaserImage)
            item.setProperty('Fanart_Image', teaserImage)
            item.setInfo('video', infoLabels)
            url = PATH + '?uuid=' + concert.attrib.get('id')
            xbmcplugin.addDirectoryItem(HANDLE, url, item, isFolder=True)

        xbmcplugin.addSortMethod(HANDLE, xbmcplugin.SORT_METHOD_TITLE)
        xbmcplugin.endOfDirectory(HANDLE)


    def listConcert(self, uuid):
        concertXml = self.downloadUrl(CONCERT_URL % uuid)
        doc = ElementTree.fromstring(concertXml)

        teaserImage = BASE_URL % doc.findtext('concert/teaserimage')
        description = doc.findtext('concert/name') + ' - ' + (doc.findtext('concert/venue') + ' - ' + doc.findtext('concert/date'))
        artistPrefix = doc.findtext('concert/name') + ' - %s'
        startTimes = list()
        for track in doc.findall('tracks/track'):
            startTimes.append(int(track.attrib.get('startms')) / 1000)
        startTimes.append(startTimes[len(startTimes)-1])

        for idx, track in enumerate(doc.findall('tracks/track')):
            startSeconds = int(track.attrib.get('startms')) / 1000
            durationSeconds = startTimes[idx + 1] - startSeconds

            infoLabels = {
                'title' : artistPrefix % track.findtext('name'),
                'duration' : str(durationSeconds),
                'plotoutline' : description
            }

            item = xbmcgui.ListItem(infoLabels['title'], iconImage=teaserImage, thumbnailImage=teaserImage)
            item.setProperty('Fanart_Image', teaserImage)
            item.setInfo('video', infoLabels)
            url = PATH + '?uuid=%s&start=%d' % (uuid, startSeconds)
            #url = RTMP_URL % doc.findtext('concert/stream')[4:].replace(' ', '%20')
            #if startSeconds > 0:
            #    url += " start=%d" % startSeconds
            xbmcplugin.addDirectoryItem(HANDLE, url, item)

        xbmcplugin.endOfDirectory(HANDLE)


    def playVideo(self, uuid, startSeconds):
        concertXml = self.downloadUrl(CONCERT_URL % uuid)
        doc = ElementTree.fromstring(concertXml)

        description = doc.findtext('concert/name') + ' - ' + (doc.findtext('concert/venue') + ' - ' + doc.findtext('concert/date'))
        url = RTMP_URL % doc.findtext('concert/stream')[4:].replace(' ', '%20')

        teaserImage = BASE_URL % doc.findtext('concert/teaserimage')
        item = xbmcgui.ListItem(description, iconImage=teaserImage, thumbnailImage=teaserImage)

        player = xbmc.Player()
        player.play(url, item)

        startTime = int(startSeconds)
        if startTime > 0:
            for i in range(5):
                if player.isPlaying():
                    player.seekTime(startTime)
                    break
                xbmc.sleep(1000)

    def downloadUrl(self, url):
        u = urllib2.urlopen(url)
        contents = u.read()
        u.close()
        return contents.replace('encoding="iso-8859-1"', 'encoding="utf-8"')

if __name__ == '__main__':
    ADDON = xbmcaddon.Addon(id = 'plugin.video.vegaplayer.dk')
    PATH = sys.argv[0]
    HANDLE = int(sys.argv[1])
    PARAMS = urlparse.parse_qs(sys.argv[2][1:])

    vp = VegaPlayerAddon()
    if PARAMS.has_key('start'):
        vp.playVideo(PARAMS['uuid'][0], PARAMS['start'][0])

    elif PARAMS.has_key('uuid'):
        vp.listConcert(PARAMS['uuid'][0])

    else:
        vp.listConcerts()

