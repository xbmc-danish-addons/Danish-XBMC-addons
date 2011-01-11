import os
import re

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import danishaddons
import danishaddons.web
import sources

SLUG = 'tv2fyn'

BASE_URL = 'http://www.tv2fyn.dk%s'
ARCHIVE_URL = BASE_URL % '/arkiv/'
VIDEO_URL = ARCHIVE_URL + '?video_id=%s'

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
    #icon = os.getcwd() + "/resources/logos/%s.png" % SLUG

    for m in re.finditer('<a href="\?video_id=([0-9]+)">.*?<img src="(http://.*?)".*?<h1 class="headline">(.*?)</h1>.*?<p.*?>(.*?)</p>', html, re.DOTALL):
        videoId = m.group(1)
        icon = m.group(2)
        icon = icon.split('_')[0] + '.jpg'
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

    m = re.search("(http://.*?\.m4v)", html)
    if m is not None:
        # New style player
        clipUrl = m.group(1)

    else:
        # Old style player
        m = re.search("launch_player\('(.*?)'", html)
        clipUrl = m.group(1)

    player = xbmc.Player()
    player.play(clipUrl)



def invoke(params):
    if params.has_key('date'):
        sources.chooseDate(showClips)
    elif params.has_key('video_id'):
        playClip(params['video_id'])
    else:
        showClips()

