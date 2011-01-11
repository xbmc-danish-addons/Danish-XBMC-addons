import datetime
import os
import re

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import danishaddons
import danishaddons.web

#http://front.xstream.dk/tvmv/index/get-list?period=20110101-20110102
import sources

SLUG = 'tv2midtvest'

BASE_URL = 'http://front.xstream.dk%s'
ARCHIVE_URL = BASE_URL % '/tvmv/index/get-list?period=%s-%s'
VIDEO_URL = BASE_URL % '/tvmv/feed/video/?platform=web&id=%s'
IMAGE_URL = BASE_URL % '/tvmv/image/splash/?id=%s&format=4&v=0'

def showClips(date=None):
    """

        data - format is dd/mm/yyyy fx. 01/01/2011
    """

    if date is None:
        today = datetime.datetime.today()
        tomorrow = today + datetime.timedelta(1)

    else:
        parts = date.split('/')
        today = datetime.datetime(int(parts[2]), int(parts[1]), int(parts[0]))
        tomorrow = today + datetime.timedelta(1)

    dateSlug = "%s-%s" % (today.strftime('%Y%m%d'), tomorrow.strftime('%Y%m%d'))
    baseUrl = ARCHIVE_URL % (today.strftime('%Y%m%d'), tomorrow.strftime('%Y%m%d'))

    print dateSlug
    print baseUrl

    html = danishaddons.web.downloadAndCacheUrl(baseUrl, os.path.join(
            danishaddons.ADDON_DATA_PATH, '%s_%s.html' % (SLUG, dateSlug)), 60)
    #icon = os.getcwd() + "/resources/logos/%s.png" % SLUG

    for m in re.finditer('data-id="([0-9]+)"><img src="(.*?)".*?></a>.*?<div class="details">.*?<a.*?>(.*?)</a>', html, re.DOTALL):
        videoId = m.group(1)
        icon = IMAGE_URL % videoId
        print icon
        label = m.group(3)
        item = xbmcgui.ListItem(label, iconImage=icon)
        item.setInfo('video', {
            'title' : label
        })

        url = danishaddons.ADDON_PATH + '?slug=%s&video_id=%s' % (SLUG, videoId)
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, False)

    sources.addChooseDateItem(SLUG)
    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)


def playClip(videoId):
    html = danishaddons.web.downloadUrl(VIDEO_URL % videoId)

    m = re.search('<[^>]+url="(rtmp://[^"]+1400kbit_128kbit_AFR_640x360_mp4.mp4)"[^>]+xt:start_time="([0-9]+)"', html)
    clipUrl = m.group(1)
    clipUrl = clipUrl.replace('/tvmv/', '/tvmv/tvmv/')
    start = m.group(2)

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

