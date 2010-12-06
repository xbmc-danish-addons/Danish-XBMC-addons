import os
import re
import string

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from danishaddons import *

URL = 'http://www.dr.dk/pirattv/'

def showPrograms():
	piratHtml = web.downloadAndCacheUrl(URL + 'programmer/?q=pirat', os.path.join(ADDON_DATA_PATH, 'pirat.html'), 60)
	arkivHtml = web.downloadAndCacheUrl(URL + 'programmer/?q=arkiv', os.path.join(ADDON_DATA_PATH, 'arkiv.html'), 60)

	html = piratHtml + arkivHtml

	for m in re.finditer('<h3>.*?<a href="/pirattv/programmer/(.*?)".*?title=".*?">(.*?)</a>.*?</h3>.*?<a href="(.*?)" rel="thumbnail">.*?</a>.*?<p>(.*?)</p>', html, re.DOTALL):
		slug = m.group(1)
		title = string.capwords(web.decodeHtmlEntities(unicode(m.group(2), 'UTF-8')))
		icon = m.group(3)
		description = m.group(4)

		item = xbmcgui.ListItem(title, iconImage = icon)
		item.setInfo(type = 'video', infoLabels = {
			'title' : title,
			'plot' : description
		})
		url = ADDON_PATH + '?slug=' + slug
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def showClips(slug, page = None):
	url = URL + 'programmer/' + slug
	if(page != None):
		url += '/side-%s/?' % page
	print url
	html = web.downloadAndCacheUrl(url, os.path.join(ADDON_DATA_PATH, '%s-%s.html' % (slug, page)), 60)

	for m in re.finditer('<h3>.*?<a href="/pirattv/programmer/(.*?)/(side-.*?/)?(.*?)" title="(.*?)">.*?</a>.*?<a href="(.*?)" rel="thumbnail">.*?<p>(.*?)</p>.*?<span class="rating">(.*?)</span>.*?<span class="duration">(.*?)</span>', html, re.DOTALL):
		slug = m.group(1)
		clipSlug = m.group(3)
		title = m.group(4)
		icon = m.group(5)
		description = m.group(6)
		rating = m.group(7)
		duration = m.group(8)

		infoLabels = {}
		infoLabels['title'] = string.capwords(web.decodeHtmlEntities(unicode(title, 'UTF-8')))
		infoLabels['plot'] = web.decodeHtmlEntities(unicode(description, 'UTF-8'))
		infoLabels['rating'] = int(rating) * 2
		infoLabels['duration'] = info.secondsToDuration(int(duration))

		item = xbmcgui.ListItem(infoLabels['title'], iconImage = icon)
		item.setInfo('video', infoLabels)
		item.setProperty('IsPlayable', 'true')

		url = ADDON_PATH + '?slug=%s&clip=%s' % (slug, clipSlug)
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, False)

	m = re.search('<li class="next"><a href=".*?/side-(.*?)/', html)
	if(m != None):
		item = xbmcgui.ListItem('Flere...')
		url = ADDON_PATH + '?slug=%s&page=%s' % (slug, m.group(1))
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playClip(slug, clipSlug):
	html = web.downloadAndCacheUrl(URL + 'programmer/' + slug + '/' + clipSlug, os.path.join(ADDON_DATA_PATH, '%s-%s.html' % (slug, clipSlug)), 60)

	m = re.search("mediaFile: '(rtmp://.*?/)(.*?/)(.*?)'", html)
	url = m.group(1) + m.group(2) + m.group(2) + m.group(3)

	print url
	
	item = xbmcgui.ListItem(path = url)
	xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, item)


if(ADDON_PARAMS.has_key('slug') and ADDON_PARAMS.has_key('clip')):
	playClip(ADDON_PARAMS['slug'], ADDON_PARAMS['clip'])
if(ADDON_PARAMS.has_key('slug')):
	if(ADDON_PARAMS.has_key('page')):
		showClips(ADDON_PARAMS['slug'], ADDON_PARAMS['page'])
	else:
		showClips(ADDON_PARAMS['slug'])
else:
	showPrograms()

