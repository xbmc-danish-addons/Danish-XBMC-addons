import os
import re

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import danishaddons
import danishaddons.web
import sources

SLUG = 'tv2oj'

ARCHIVE_URL = 'http://tv2oj.fynskemedier.dk/arkiv/'
RTMP_URL = 'rtmp://80.63.11.91:80/vod/vod/mp4:%s_%d.mp4'
SPEED = 2000 #300, 1000, 2000

def showClips(date=None):
    baseUrl = ARCHIVE_URL
    dateSlug = None
    if date is not None:
        dateSlug = date.replace('/', '')
        parts = date.split('/')
        baseUrl += parts[2] + '/' + parts[1] + '/' + parts[0] + '/'

    print dateSlug
    print baseUrl

    html = danishaddons.web.downloadAndCacheUrl(baseUrl, os.path.join(
            danishaddons.ADDON_DATA_PATH, '%s_%s.html' % (SLUG, dateSlug)), 60)
    icon = os.getcwd() + "/resources/logos/tv2oj.png"

    for m in re.finditer('<a href="(%s.*?)">(.*?)</a>' % ARCHIVE_URL, html):
        clipUrl = m.group(1)
        label = m.group(2)
        item = xbmcgui.ListItem(label, iconImage=icon)

        url = danishaddons.ADDON_PATH + '?slug=%s&url=%s' % (SLUG, clipUrl)
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

