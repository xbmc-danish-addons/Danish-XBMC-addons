import os
import re

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import danishaddons
import danishaddons.web
import sources

SLUG = 'tv2lorry'

BASE_URL = 'http://www.tv2lorry.dk%s'
ARCHIVE_URL = BASE_URL % '/arkiv/'
VIDEO_URL = ARCHIVE_URL + '?video_id=%s'

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
    #icon = danishaddons.ADDON_PATH + "/resources/logos/%s.png" % SLUG

    for m in re.finditer('<a href="\?video_id=([0-9]+)">.*?<img src="(.*?)" class="tv2region-.*?<h1 class="headline"><a href="\?video_id=[0-9]+">(.*?)</a></h1>.*?<p class="synopsis">.*?<a href="\?video_id=[0-9]+">(.*?)</a>', html, re.DOTALL):
        videoId = m.group(1)
        icon = m.group(2)
        if icon[0:7] != 'http://':
            icon = BASE_URL % icon
        icon = icon.replace('70x40', '256x146')
        print icon
        label = m.group(3)
        description = m.group(4)
        item = xbmcgui.ListItem(label, iconImage=icon)
        item.setInfo('video', {
            'title' : label,
            'plot' : description
        })

        url = danishaddons.ADDON_PATH + '?slug=%s&video_id=%s' % (SLUG, videoId)
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, False)

    sources.addChooseDateItem(SLUG)
    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)


def playClip(videoId):
    html = danishaddons.web.downloadUrl(VIDEO_URL % videoId)

    m = re.search("playVideo\('([^']+)', ([0-9]+),", html)
    if m is not None:
        # New style player
        file = m.group(1)
        start = m.group(2)
        clipUrl = RTMP_URL % (file, SPEED)

    else:
        # Old style player
        m = re.search("launch_player\('(.*?)'", html)
        start = 0
        clipUrl = m.group(1)

    player = xbmc.Player()
    player.play(clipUrl)
    if int(start) > 0:
        player.seekTime(int(start))



def invoke(params):
    if params.has_key('date'):
        sources.chooseDate(showClips)
    elif params.has_key('video_id'):
        playClip(params['video_id'])
    else:
        showClips()

