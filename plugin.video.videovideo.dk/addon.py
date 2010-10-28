import re
import os

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from feedparser import feedparser
from danishaddons import *

SHOWS_URL = 'http://videovideo.dk/shows'
RSS_URL_TEMPLATE = 'http://videovideo.dk/show/%s/rss/720/webm'

def showOverview():
	html_path = os.path.join(ADDON_DATA_PATH, 'shows.html')
	html = web.downloadAndCacheUrl(SHOWS_URL, html_path, 24 * 60)

	for m in re.finditer('<img src="(http://gfx.videovideo.dk/[^"]+)".*?<h5>([^<]+)</h5>.*?<p>([^<]+)</p>.*?href="/show/([^"]+)"', html, re.DOTALL):
		icon = m.group(1)
		title = m.group(2)
		description = m.group(3)
		slug = m.group(4)

		item = xbmcgui.ListItem(title, iconImage = icon)
		item.setInfo(type = 'video', infoLabels = {
			'title' : title,
			'plot' : description
		})
		url = ADDON_PATH + '?slug=' + slug
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def showShow(slug):
	rss = web.downloadAndCacheUrl(RSS_URL_TEMPLATE % slug, os.path.join(ADDON_DATA_PATH, '%s.rss' % slug), 60)
	d = feedparser.parse(rss)

	for e in d.entries:
		iconPath = os.path.join(ADDON_DATA_PATH, '%s.jpg' % e.id)
		if(not(os.path.exists(iconPath))):
			cacheIcon(e.link, iconPath)

		item = xbmcgui.ListItem(e.title, iconImage = iconPath)
		try:
			description = web.decodeHtmlEntities(e.description)
			description = re.sub('<.*?>', '', description)
			description = description.replace('\t', '')
		except AttributeError:
			description = 'Ingen beskrivelse'

		infoLabels = {
			'tvshowtitle' : d.channel.title,
			'title' : e.title,
			'plot' : description,
		}
		if(e.updated_parsed != None):
			infoLabels['aired'] = parsePubDate(e.updated_parsed)
			infoLabels['date'] = parseDate(e.updated_parsed)
			infoLabels['year'] = e.updated_parsed[0]

		item.setInfo('video', infoLabels)
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, e.enclosures[0].href, item, False)

	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def parsePubDate(pubDate):
	return '%d-%d-%d' % (pubDate[0], pubDate[1], pubDate[2])

def parseDate(pubDate):
	return '%02d.%02d.%d' % (pubDate[2], pubDate[1], pubDate[0])

def cacheIcon(url, cachePath):
	html = web.downloadUrl(url)
	m = re.search('poster="(.*?)"', html)
	web.downloadAndCacheUrl(m.group(1), cachePath, 60)

if(ADDON_PARAMS.has_key('slug')):
	showShow(ADDON_PARAMS['slug'])
else:
	showOverview()

