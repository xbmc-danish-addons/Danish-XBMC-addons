# coding = 'utf-8'
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib, urllib2, re, os, time, simplejson
from htmlentitydefs import name2codepoint as n2cp

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
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def showCategory(key):
	json = loadJson()
	
	for e in json[key]:
		infoLabels = {}
		if(e['headline'] != None):
			infoLabels['title'] = e['date'] + ' ' + decode_htmlentities(e['headline'])
		if(e['descr'] != None):
			infoLabels['plot'] = decode_htmlentities(e['descr'])
		if(e['date'] != None):
			infoLabels['year'] = int(e['date'][6:])
		if(e['duration'] != None):
			infoLabels['duration'] = e['duration'][1:9]

		item = xbmcgui.ListItem(infoLabels['title'], iconImage = e['img'])
		item.setInfo('video', infoLabels)
		url = ADDON_PATH + '?id=' + str(e['id'])

		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item)

	xbmcplugin.setContent(ADDON_HANDLE, 'episodes')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def playVideo(id):
		dialog = xbmcgui.DialogProgress()
		dialog.create('Et øjeblik', 'Indlæser playlist...')

		# retrieve masquarade playlist
		url = urllib2.urlopen('http://common.tv2.dk/flashplayer/playlistSimple.xml.php/clip-' + id + '.xml')
		playlist = url.read()
		url.close()
		m = re.search('video="([^"]+)" materialId="([^"]+)"', playlist)
		
		if(dialog.iscanceled()):
			dialog.close()
			return
		dialog.update(33)

		# retrive crossdomain to setup next request for geocheck
		url = urllib2.urlopen('http://common-dyn.tv2.dk/crossdomain.xml')
		url.read()
		url.close()

		if(dialog.iscanceled()):
			dialog.close()
			return
		dialog.update(66)

		# retrieve real playlist
		url = urllib2.urlopen('http://common-dyn.tv2.dk/flashplayer/geocheck.php?id=' + m.group(2) + '&file=' + m.group(1))
		playlist = url.read()
		url.close()

		if(dialog.iscanceled()):
			dialog.close()
			return
		dialog.close()

		xbmc.Player().play(playlist)

def loadJson():
	json_path = os.path.join(ADDON_DATA_PATH, 'video.js')
	json = web.downloadAndCacheUrl(BASE_URL, json_path, 60)
		
	# get json part of js file
	m = re.search('data = ({.*)}', json, re.DOTALL)
	# fixup json parsing with simplejson, ie. replace ' with "
	json = re.sub(r'\'([\w-]+)\':', r'"\1":', m.group(1))

	return simplejson.loads(json)
	
def decode_htmlentities(string):

    def substitute_entity(match):
        ent = match.group(3)
        if match.group(1) == "#":
            # decoding by number
            if match.group(2) == '':
                # number is in decimal
                return unichr(int(ent))
            elif match.group(2) == 'x':
                # number is in hex
                return unichr(int('0x'+ent, 16))
        else:
            # they were using a name
            cp = n2cp.get(ent)
            if cp: return unichr(cp)
            else: return match.group()
    
    entity_re = re.compile(r'&(#?)(x?)(\w+);')
    return entity_re.subn(substitute_entity, string)[0]


if(ADDON_PARAMS.has_key('key')):
	showCategory(ADDON_PARAMS['key'])
elif(ADDON_PARAMS.has_key('id')):
	playVideo(ADDON_PARAMS['id'])
else:
	showOverview()

