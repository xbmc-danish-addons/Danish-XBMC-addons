# coding=utf-8
import os, re
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from danishaddons import *

def showCategories():
	html = web.downloadAndCacheUrl('http://www.pixel.tv/', 'programmer.html', 60)

	for m in re.finditer('<a href="/programmer/([^/]+)/" onmouseout="UnTip\(\);" onmouseover="Tip\(\'([^\']+)\'\);"><img src="([^"]+)" alt="([^"]+)">', html):
		slug = m.group(1)
		description = m.group(2).replace('<strong>', '[B]').replace('</strong>', '[/B]').replace('<br>', '\n')
		icon = 'http://www.pixel.tv%s' % m.group(3)
		title = m.group(4)

		item = xbmcgui.ListItem(title, iconImage = icon)
		item.setInfo(type = 'video', infoLabels = {
			'title' : title,
			'plot' : description
		})
		url = ADDON_PATH + '?slug=' + slug
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def showCategory(slug, page):
	if(page == None):
		html = web.downloadAndCacheUrl('http://www.pixel.tv/programmer/%s/' % slug, '%s.html' % slug, 60)
	else:
		html = web.downloadAndCacheUrl('http://www.pixel.tv/programmer/%s/%s' % (slug, page), '%s-%s.html' % (slug, page), 60)

	for m in re.finditer('<small>([^<]+)</small></td><td>.*?<a href="([^"]+)"><small>.*?</small>([^<]+)</a>', html):
		date = m.group(1)
		playlist = m.group(2)
		title = m.group(3)

		item = xbmcgui.ListItem(title)
		url = ADDON_PATH + '?playlist=' + playlist
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item)

	if(page == None):
		page = 2
	else:
		page = int(page) + 1

	if(re.search('/programmer/%s/%d' % (slug, page), html)):
		item = xbmcgui.ListItem('Ældre indslag...')
		url = ADDON_PATH + '?slug=' + slug + '&page=' + str(page)
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)
		

	xbmcplugin.setContent(ADDON_HANDLE, 'episodes')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def playClip(playlist):
	html = web.downloadAndCacheUrl('http://www.pixel.tv%s' % playlist, 'playlist.html', 0)

	m = re.search('http://www.pixel.tv/embed/js/\?file=([0-9]+)&pid=([^&]+)&width=([0-9]+)', html)
	file = m.group(1)
	pid = m.group(2)
	width = m.group(3)

	json = web.downloadAndCacheUrl('http://www.pixel.tv/playlist/?file=%s_%s_%s' % (file, width, pid), os.path.join(ADDON_DATA_PATH, 'playlist.json'), 0)

	m = re.search("baseURL: '([^']+)'", json)
	baseURL = m.group(1)
	m = re.search("'(advertisements.*?)'", json)
	advertisement = m.group(1)
	m = re.search("'(.*?\?tag=%s)'" % pid, json)
	path = m.group(1)

	playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
	playlist.clear()
	playlist.add(baseURL + '/' + advertisement)
	playlist.add(baseURL + '/' + path)

	player = xbmc.Player()
	player.play(playlist)


if(ADDON_PARAMS.has_key('slug')):
	showCategory(ADDON_PARAMS['slug'], ADDON_PARAMS.get('page'))
elif(ADDON_PARAMS.has_key('playlist')):
	playClip(ADDON_PARAMS['playlist'])
else:
	showCategories()

