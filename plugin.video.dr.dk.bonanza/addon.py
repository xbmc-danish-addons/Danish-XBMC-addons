# coding=utf-8
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, urllib2, re, os, time, simplejson

from danishaddons import *

BASE_URL = 'http://www.dr.dk/Bonanza/'

def search():
	keyboard = xbmc.Keyboard('', msg(30001))
	keyboard.doModal()
	if (keyboard.isConfirmed()):
		html = web.downloadAndCacheUrl('http://www.dr.dk/bonanza/search.htm?&type=video&limit=120&needle=' + keyboard.getText().replace(' ', '+'),
			os.path.join(ADDON_DATA_PATH, 'search.html'), 0) # don't cache search results
		addContent(html)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		xbmcplugin.setContent(ADDON_HANDLE, 'episodes')


def showCategories():
	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')

	html = web.downloadAndCacheUrl(BASE_URL, os.path.join(ADDON_DATA_PATH, 'categories.html'), 24 * 60)
	icon = os.path.join(os.getcwd(), 'icon.png')

	item = xbmcgui.ListItem(msg(30001), iconImage = icon)
	xbmcplugin.addDirectoryItem(ADDON_HANDLE, ADDON_PATH + '?mode=search', item, True)
	item = xbmcgui.ListItem(msg(30002), iconImage = icon)
	xbmcplugin.addDirectoryItem(ADDON_HANDLE, ADDON_PATH + '?mode=recommend', item, True)

	for m in re.finditer('<a href="(/Bonanza/kategori/.*\.htm)">(.*)</a>', html):
		path = m.group(1)
		title = m.group(2)

		item = xbmcgui.ListItem(title, iconImage = icon)
		item.setInfo(type = 'video', infoLabels = {
			'title' : title
		})
		url = ADDON_PATH + '?mode=subcat&url=http://www.dr.dk' + path + '&title=' + title
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def showRecommendations():
	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')

	html = web.downloadAndCacheUrl(BASE_URL, os.path.join(ADDON_DATA_PATH, 'recommendations.html'), 24 * 60)

	# remove anything but 'Redaktionens favoritter'
	html = html[html.find('<span class="tabTitle">Redaktionens favoritter</span>'):]
	addSubCategories(html)
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def showSubCategories(url, title):
	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')

	html = web.downloadAndCacheUrl(url.replace(' ', '+'), os.path.join(ADDON_DATA_PATH, 'category-' + title + '.html'), 24 * 60)

	# remove 'Redaktionens favoritter' as they are located on every page
	html = html[:html.find('<span class="tabTitle">Redaktionens favoritter</span>')]

	addSubCategories(html)
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def showContent(url, title):
	html = web.downloadAndCacheUrl(url, os.path.join(ADDON_DATA_PATH, 'content-' + title + '.html'), 60)	
	addContent(html)

	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	xbmcplugin.setContent(ADDON_HANDLE, 'episodes')



def addSubCategories(html):
	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')

	for m in re.finditer('<a href="(http://www\.dr\.dk/bonanza/serie/[^\.]+\.htm)"[^>]+>..<img src="(http://downol\.dr\.dk/download/bonanza/collectionThumbs/[^"]+)"[^>]+>..<b>([^<]+)</b>..<span>([^<]+)</span>..</a>', html, re.DOTALL):
		url = m.group(1)
		image = m.group(2)
		title = m.group(3)
		description = m.group(4)

		item = xbmcgui.ListItem(title, iconImage = image)
		item.setInfo(type = 'video', infoLabels = {
			'title' : title,
			'plot' : description
		})
		url = ADDON_PATH + '?mode=content&url=' + url + '&title=' + title
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)


def addContent(html):
	for m in re.finditer('newPlaylist\(([^"]+)"', html):
		raw = m.group(1)[:-2].replace('&quot;', '"')
		json = simplejson.loads(raw)

		infoLabels = {}
		if(json['Title'] != None):
			infoLabels['title'] = json['Title']
		if(json['Description'] != None):
			infoLabels['plot'] = json['Description']
		if(json['Colophon'] != None):
			infoLabels['writer'] = json['Colophon']
		if(json['Actors'] != None):
			infoLabels['cast'] = json['Actors']
		if(json['Rating'] != None):
			infoLabels['rating'] = json['Rating']
		if(json['FirstPublished'] != None):
			infoLabels['year'] = int(json['FirstPublished'][:4])
		if(json['Duration'] != None):
			infoLabels['duration'] = info.secondsToDuration(int(json['Duration']) / 1000)

		item = xbmcgui.ListItem(json['Title'], iconImage = findFileLocation(json, 'Thumb'))
		item.setInfo('video', infoLabels)

		rtmp_url = findFileLocation(json, 'VideoHigh')
		if(rtmp_url == None):
			rtmp_url = findFileLocation(json, 'VideoMid')
		if(rtmp_url == None):
			rtmp_url = findFileLocation(json, 'VideoLow')

		# patch rtmp_url to work with mplayer
		rtmp_url = rtmp_url.replace('rtmp://vod.dr.dk/', 'rtmp://vod.dr.dk/bonanza/')
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, rtmp_url, item, False)



def findFileLocation(json, type):
	for file in json['Files']:
		if(file['Type'] == type):
			return file['Location']
	return None	


if(ADDON_PARAMS.has_key('mode') and ADDON_PARAMS['mode'] == 'subcat'):
	showSubCategories(ADDON_PARAMS['url'], ADDON_PARAMS['title'])
elif(ADDON_PARAMS.has_key('mode') and ADDON_PARAMS['mode'] == 'content'):
	showContent(ADDON_PARAMS['url'], ADDON_PARAMS['title'])
elif(ADDON_PARAMS.has_key('mode') and ADDON_PARAMS['mode'] == 'search'):
	search()
elif(ADDON_PARAMS.has_key('mode') and ADDON_PARAMS['mode'] == 'recommend'):
	showRecommendations()
else:
	showCategories()

