# coding = 'utf-8'
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib, urllib2, re, os, time, simplejson

from danishaddons import *

KEY_TO_TITLE = {
	'beep' : 'Beep - Gadgets',
	'sport' : 'Sporten',
	'station2' : 'Station 2',
	'zulu' : 'Zulu',
	'tour2009' : 'Tour de France 2009',
	'mogensen-kristiansen' : 'Mogensen & Kristiansen',
	'news-finans' : 'News Finansmagasinet',
	'nyheder' : 'Nyhederne',
	'most-viewed' : 'Mest sete',
	'go' : 'Go\' Morgen / Aften',
	'programmer' : 'Programmer',
	'finans' : 'Finans',
	'musik' : 'VIP Musik',
	'latest' : 'Nyeste'
}

BASE_URL = 'http://video.tv2.dk/js/video-list.js.php/index.js'

def showOverview():
	json = loadJson()
	icon = os.path.join(os.getcwd(), 'icon.png')

	for key in json.keys():
		if(KEY_TO_TITLE.has_key(key)):
			item = xbmcgui.ListItem(KEY_TO_TITLE[key], iconImage = icon)
		else:
			item = xbmcgui.ListItem(key, iconImage = icon)
			
		url = ADDON_PATH + '?key=' + key
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def showCategory(key):
	json = loadJson()
	
	for e in json[key]:
		infoLabels = {}
		if(e['headline'] != None):
			infoLabels['title'] = web.decodeHtmlEntities(e['headline'])
		if(e['descr'] != None):
			infoLabels['plot'] = web.decodeHtmlEntities(e['descr'])
		if(e['date'] != None):
			infoLabels['year'] = int(e['date'][6:])
			infoLabels['date'] = e['date'].replace('-', '.')
		if(e['duration'] != None):
			infoLabels['duration'] = e['duration'][1:9]

		item = xbmcgui.ListItem(infoLabels['title'], iconImage = e['img'])
		item.setInfo('video', infoLabels)
		item.setProperty('IsPlayable', 'true')
		url = ADDON_PATH + '?id=' + str(e['id'])

		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item)

	xbmcplugin.setContent(ADDON_HANDLE, 'episodes')
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def playVideo(id):
		# retrieve masquarade playlist
		url = urllib2.urlopen('http://common.tv2.dk/flashplayer/playlistSimple.xml.php/clip-' + id + '.xml')
		playlist = url.read()
		url.close()
		m = re.search('video="([^"]+)" materialId="([^"]+)"', playlist)
		
		# retrive crossdomain to setup next request for geocheck
		url = urllib2.urlopen('http://common-dyn.tv2.dk/crossdomain.xml')
		url.read()
		url.close()

		# retrieve real playlist
		url = urllib2.urlopen('http://common-dyn.tv2.dk/flashplayer/geocheck.php?id=' + m.group(2) + '&file=' + m.group(1))
		playlist = url.read()
		url.close()

		item = xbmcgui.ListItem(path = playlist)
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, item)

def loadJson():
	json_path = os.path.join(ADDON_DATA_PATH, 'video.js')
	json = web.downloadAndCacheUrl(BASE_URL, json_path, 60)
		
	# get json part of js file
	m = re.search('data = ({.*)}', json, re.DOTALL)
	# fixup json parsing with simplejson, ie. replace ' with "
	json = re.sub(r'\'([\w-]+)\':', r'"\1":', m.group(1))

	return simplejson.loads(json)


if(ADDON_PARAMS.has_key('key')):
	showCategory(ADDON_PARAMS['key'])
elif(ADDON_PARAMS.has_key('id')):
	playVideo(ADDON_PARAMS['id'])
else:
	showOverview()

