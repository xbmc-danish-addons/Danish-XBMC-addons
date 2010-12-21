import re
import pickle
import os
import sys

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

import feedparser
import danishaddons
import danishaddons.web

BASE_URL = 'http://www.dr.dk/podcast/Video'
FEED_URL_TEMPLATE = 'http://vpodcast.dr.dk/feeds/%s.xml'

def showOverview():
    xbmcplugin.setContent(danishaddons.ADDON_HANDLE, 'tvshows')

    html_path = os.path.join(danishaddons.ADDON_DATA_PATH, 'video.html')
    html = danishaddons.web.downloadAndCacheUrl(BASE_URL, html_path, 24 * 60)

    dialog = xbmcgui.DialogProgress()
    dialog.create(danishaddons.msg(30001))

    feed_count = html.count(FEED_URL_TEMPLATE[:15])
    feed_idx = 0
    for m in re.finditer(FEED_URL_TEMPLATE % '(.*)\\', html):
        feed_idx+=1
        key = m.group(1)
        details = getFeedDetails(key)

        iconImage = None
        if(details.has_key('image_path')):
            iconImage = details['image_path']

        item = xbmcgui.ListItem(details['title'], iconImage = iconImage)
        item.setInfo(type = 'video', infoLabels = {
            'title' : details['title'],
            'plot' : details['description']
        })
        url = danishaddons.ADDON_PATH + '?key=' + key
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, True)

        dialog.update((feed_idx * 100 / feed_count), details['title'])
        if(dialog.iscanceled()):
            break

    dialog.close()
    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)

def showFeed(key):
    d = feedparser.parse(FEED_URL_TEMPLATE % key)
    details = getFeedDetails(key)

    for e in d.entries:
        item = xbmcgui.ListItem(e.title, iconImage = details['image_path'])
        try:
            description = e.description
        except AttributeError:
            description = 'No description'

        infoLabels = {
            'tvshowtitle' : d.channel.title,
            'title' : e.title,
            'plot' : description,
            'duration' : e.itunes_duration,
            'director' : e.author,
            'writer' : e.author
        }
        if(e.updated_parsed is not None):
            infoLabels['aired'] = parsePubDate(e.updated_parsed)
            infoLabels['year'] = e.updated_parsed[0]

        item.setLabel2(description)
        item.setInfo('video', infoLabels)
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, e.enclosures[0].href, item, False)

    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)

    xbmcplugin.setContent(danishaddons.ADDON_HANDLE, 'episodes')
    xbmcplugin.setPluginCategory(danishaddons.ADDON_HANDLE, d.channel.title)

def getFeedDetails(key):
    details_path = os.path.join(danishaddons.ADDON_DATA_PATH, key + '.pickle')
    details = {}

    if(not os.path.exists(details_path)):
        d = feedparser.parse(FEED_URL_TEMPLATE % key)

        details['title'] = d.feed.title
        details['description'] = d.feed.subtitle
        if d.channel.image is not None:
            details['image_path'] = d.channel.image.href

        f = open(details_path, 'wb')
        pickle.dump(details, f)
        f.close()
    else:
        f = open(details_path, 'rb')
        details = pickle.load(f)
        f.close()

    return details

def parsePubDate(pubDate):
    return '%d-%d-%d' % (pubDate[0], pubDate[1], pubDate[2])


if(__name__ == '__main__'):
    danishaddons.init(sys.argv)

    if(danishaddons.ADDON_PARAMS.has_key('key')):
        showFeed(danishaddons.ADDON_PARAMS['key'])
    else:
        showOverview()

