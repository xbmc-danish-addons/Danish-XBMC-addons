import sys, urllib2, re, os, pickle, time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from danishaddons import *

from resources.lib.feedparser import feedparser

BASE_URL = 'http://www.dr.dk/podcast/Video'
FEED_URL_TEMPLATE = 'http://vpodcast.dr.dk/feeds/%s.xml'

def showOverview():
	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')

	html_path = os.path.join(ADDON_DATA_PATH, 'video.html')
	html = web.downloadAndCacheUrl(BASE_URL, html_path, 24 * 60)

	dialog = xbmcgui.DialogProgress()
	dialog.create(msg(30001))

	feed_count = html.count(FEED_URL_TEMPLATE[:15])
	feed_idx = 0
	for m in re.finditer(FEED_URL_TEMPLATE % '(.*)\\', html):
		feed_idx+=1
		key = m.group(1)
		details = getFeedDetails(key)

		item = xbmcgui.ListItem(details['title'], iconImage = details['image_path'])
		item.setInfo(type = 'video', infoLabels = {
			'title' : details['title'],
			'plot' : details['description']
		})
		url = ADDON_PATH + '?key=' + key
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

		dialog.update((feed_idx * 100 / feed_count), details['title'])
		if(dialog.iscanceled()):
			break

	dialog.close()
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def showFeed(key):
	d = feedparser.parse(FEED_URL_TEMPLATE % key)
	details = getFeedDetails(key)

	for e in d.entries:
		item = xbmcgui.ListItem(e.title, iconImage = details['image_path'])
		item.setLabel2(e.description)
		item.setInfo(type = 'video', infoLabels = {
			'tvshowtitle' : d.channel.title,
			'title' : e.title,
			'plot' : e.description,
			'duration' : parseDuration(e.itunes_duration),
			'aired' : parsePubDate(e.updated_parsed),
			'year' : e.updated_parsed[0],
			'director' : e.author,
			'writer' : e.author
			
		})
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, e.enclosures[0].href, item, False)

	xbmcplugin.endOfDirectory(ADDON_HANDLE)

	xbmcplugin.setContent(ADDON_HANDLE, 'episodes')
	xbmcplugin.setPluginCategory(ADDON_HANDLE, d.channel.title)

def getFeedDetails(key):
	details_path = os.path.join(ADDON_DATA_PATH, key + '.pickle')
	details = {}

	if(not os.path.exists(details_path)):
		d = feedparser.parse(FEED_URL_TEMPLATE % key)

		details['title'] = d.feed.title
		details['description'] = d.feed.subtitle
		details['image_path'] = d.channel.image.href

		f = open(details_path, 'wb')
		pickle.dump(details, f)
		f.close()
	else:
		f = open(details_path, 'rb')
		details = pickle.load(f)
		f.close()

	return details

def parseDuration(duration):
	print duration
	if(duration[:3] == '00:'):
		duration = duration[3:]
	return duration[:duration.find(':')]

def parsePubDate(pubDate):
	return '%d-%d-%d' % (pubDate[0], pubDate[1], pubDate[2])



if(ADDON_PARAMS.has_key('key')):
	showFeed(ADDON_PARAMS['key'])
else:
	showOverview()

