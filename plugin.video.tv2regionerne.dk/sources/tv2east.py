import os
import re

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import simplejson
import danishaddons
import danishaddons.web
import sources


SLUG = 'tv2east'
    
BASE_URL = 'http://www.tv2east.dk%s'
ARCHIVE_URL = BASE_URL % '/udsendelser/'
SHOW_URL = BASE_URL % '/tv2_reg_views_render_video?nid=%s'
CLIP_URL = BASE_URL % '/tv2reg_flowplayer_config/action-program/nid-%s'

def showPrograms(date=None):
    baseUrl = ARCHIVE_URL
    dateSlug = None
    if date is not None:
        dateSlug = date.replace('/', '')
        parts = date.split('/')
        baseUrl += '%s-%02d-%02d' % (parts[2], int(parts[1]), int(parts[0]))

    print dateSlug
    print baseUrl

    html = danishaddons.web.downloadAndCacheUrl(baseUrl, os.path.join(
            danishaddons.ADDON_DATA_PATH, '%s_%s.html' % (SLUG, dateSlug)), 60)

    for m in re.finditer('tv2RegShowVideo\(\'([0-9]+)\', \'([^\']+)\'.*?class="enspalte_view_body">([^<]+)</p>.*?<img src=\'([^\']+)\'', html, re.DOTALL):
        show_id = m.group(1)
        title = m.group(2)
        description = m.group(3)
        image = BASE_URL % m.group(4)

        item = xbmcgui.ListItem(title, iconImage=image)
        item.setInfo('video', infoLabels = {
            'title' : title,
            'plot' : description
        })
        url = danishaddons.ADDON_PATH + '?slug=%s&show_id=%s' % (SLUG, show_id)
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, True)

    sources.addChooseDateItem(SLUG)
    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)


def showClips(show_id):
    html = danishaddons.web.downloadAndCacheUrl(SHOW_URL % show_id, os.path.join(
            danishaddons.ADDON_DATA_PATH, '%s_show_%s.html' % (SLUG, show_id)), 60)

    for m in re.finditer('<img src="([^"]+)" alt="[^"]*" .*?tv2_reg_views_play_video\(\'([0-9]+)\', \'[^\']+\', \'[^\']+\', \'[^\']+\'\)">(.*?)</a>(.*?<span[^>]+>([^<]+)</span)', html, re.DOTALL): # todo figure out why ? at the end breaks python
        icon = m.group(1)
        show_id = m.group(2)
        title = m.group(3).strip()
        description = m.group(5)

        item = xbmcgui.ListItem(title, iconImage=icon)
        item.setInfo('video', infoLabels = {
            'title' : title,
            'plot' : description
        })

        url = danishaddons.ADDON_PATH + '?slug=%s&clip_id=%s' % (SLUG, show_id)
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, False)

    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)


def playClip(clip_id):
    resp =  danishaddons.web.downloadUrl(CLIP_URL % clip_id)
    resp = resp.replace('"', '\"')
    resp = resp.replace('\n', '')
    resp = re.sub("'([^']+)'", '"\\1"', resp)

    json = simplejson.loads(resp)

    path = json['clip']['url']
    start = int(json['clip']['start'])
    host = json['plugins']['cluster']['hosts'][0]

    clipUrl = host + '/simplevideostreaming/' + path

    player = xbmc.Player()
    player.play(clipUrl)
    if int(start) > 0:
        player.seekTime(int(start))


def invoke(params):
    if params.has_key('date'):
        sources.chooseDate(showPrograms)
    elif params.has_key('clip_id'):
        playClip(params['clip_id'])
    elif params.has_key('show_id'):
        showClips(params['show_id'])
    else:
        showPrograms()

