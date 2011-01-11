import os
import re

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import danishaddons
import danishaddons.web
import sources

SLUG = 'tv2syd'

BASE_URL = 'http://www.tvsyd.dk%s'
ARCHIVE_URL = BASE_URL % '/arkiv/'
VIDEO_URL = BASE_URL % '/embed/%s'

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

    for m in re.finditer('<a href="\?video_id=[0-9]+"><img src="(.*?)" alt=".*?" /></a>.*?<h1 class="headline"><a href="\?video_id=([0-9]+)">(.*?)</a></h1>.*?<a href=".*?">(.*?)</a>', html, re.DOTALL):
        icon = m.group(1)
        icon = icon.split('_')[0] + '.jpg'
        print icon
        videoId = m.group(2)
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

    m = re.search("(http://.*?\.mp4)", html,)
    if m is not None:
        # New style player
        clipUrl = m.group(1)

    else:
        # Old style player
        m = re.search('<embed.*?src="(.*?)"', html)
        clipUrl = BASE_URL + m.group(1)

    player = xbmc.Player()
    player.play(clipUrl)



def invoke(params):
    if params.has_key('date'):
        sources.chooseDate(showClips)
    elif params.has_key('video_id'):
        playClip(params['video_id'])
    else:
        showClips()

