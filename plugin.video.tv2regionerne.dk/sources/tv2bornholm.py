import os
import re

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import danishaddons
import danishaddons.web
import sources

SLUG = 'tv2bornholm'

ARCHIVE_URL = 'http://www.tv2bornholm.dk/moduler/nyheder/showregvideo.asp'
RTMP_URL = 'rtmp://itv05.digizuite.dk/TV2Bornholm/inst/%s'

def showClips(date=None):
    baseUrl = ARCHIVE_URL
    dateSlug = None
    if date is not None:
        dateSlug = date.replace('/', '')
        parts = date.split('/')
        baseUrl += '?dato=%02d-%02d-%s' % (int(parts[0]), int(parts[1]), parts[2])

    print dateSlug
    print baseUrl

    html = danishaddons.web.downloadAndCacheUrl(baseUrl, os.path.join(
            danishaddons.ADDON_DATA_PATH, '%s_%s.html' % (SLUG, dateSlug)), 60)
    icon = danishaddon.ADDON_PATH + "/resources/logos/tv2bornholm.png"

    for m in re.finditer('<input type="hidden" id="TCin_[0-9]+" name="TCin_[0-9]+" value="([^"]+)" /><input type="hidden" id="varighed_[0-9]+" name="varighed_[0-9]+" value="([^"]+)" /><input type="hidden" id="filnavn_[0-9]+" name="filnavn_[0-9]+" value="([^"]+)" /><a class=programtitel href="\?([^"]+)".*?<b>(.*?)</b>.*?<td valign=top class=programtekst>(.*?)</td>', html, re.DOTALL):
        start = m.group(1)
        duration = m.group(2)
        filename = m.group(3)
        params = m.group(4) # dato=10-01-2011&videoid=11170
        label = m.group(5)
        description = m.group(6)

        item = xbmcgui.ListItem(label, iconImage=icon)
        item.setInfo('video', infoLabels = {
            'title' : label,
            'plot' : description
        })

        #url = danishaddons.ADDON_PATH + '?slug=%s&%s' % (SLUG, params)
        url = RTMP_URL % filename
        print url
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, False)

    sources.addChooseDateItem(SLUG)
    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)


def playClip(url):
    html = danishaddons.web.downloadUrl(url)

    m = re.search("TV2RegionFlowplayer\('(.*?)'.*?start : ([0-9]+),", html, re.DOTALL)
    if m is not None:
        # New style player
        file = m.group(1)
        start = m.group(2)
        clipUrl = RTMP_URL % (file, SPEED)

    else:
        # Old style player
        m = re.search("videoPlayer\(\{.*?url : '(.*?)'", html, re.DOTALL)
        clipUrl = m.group(1)
        start = 0

    player = xbmc.Player()
    player.play(clipUrl)
    if int(start) > 0:
        player.seekTime(int(start))


def invoke(params):
    if params.has_key('date'):
        sources.chooseDate(showClips)
    elif params.has_key('url'):
        playClip(params['url'])
    else:
        showClips()

