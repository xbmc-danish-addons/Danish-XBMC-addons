# coding=utf-8
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, urllib2, re, os, time, simplejson
from cgi import parse_qs

__addon__ = xbmcaddon.Addon(id='plugin.video.dr.dk.bonanza')
__language__ = __addon__.getLocalizedString
__path__ = sys.argv[0]
__handle__ = int(sys.argv[1])

BASE_URL = 'http://www.dr.dk/Bonanza/'
SCRIPT_DATA_PATH = xbmc.translatePath(__addon__.getAddonInfo("Profile"))


def search():
	keyboard = xbmc.Keyboard('', __language__(30001))
	keyboard.doModal()
	if (keyboard.isConfirmed()):
		html = urllib2.urlopen('http://www.dr.dk/bonanza/search.htm?&type=video&limit=120&needle=' + keyboard.getText().replace(' ', '+'))
		addContent(html.read())
		html.close()

		xbmcplugin.endOfDirectory(__handle__)
		xbmcplugin.setContent(__handle__, 'episodes')


def showCategories():
	xbmcplugin.setContent(__handle__, 'tvshows')

	cache_path = os.path.join(SCRIPT_DATA_PATH, 'categories.html')
	try: date = os.path.getmtime( cache_path )
	except: date = 0
	refresh = ( ( time.time() - ( 24 * 60 * 60 ) ) >= date )
	if(refresh):
		url = urllib2.urlopen(BASE_URL)
		html = url.read()
		url.close()

		f = open(cache_path, 'w')
		f.write(html)
		f.close()
	else:
		f = open(cache_path)
		html = f.read()
		f.close()

	icon = os.path.join(os.getcwd(), 'icon.png')

	item = xbmcgui.ListItem(__language__(30001), iconImage = icon)
	xbmcplugin.addDirectoryItem(__handle__, __path__ + '?mode=search', item, True)
	item = xbmcgui.ListItem(__language__(30002), iconImage = icon)
	xbmcplugin.addDirectoryItem(__handle__, __path__ + '?mode=recommend', item, True)

	for m in re.finditer('<a href="(/Bonanza/kategori/.*\.htm)">(.*)</a>', html):
		path = m.group(1)
		title = m.group(2)

		item = xbmcgui.ListItem(title, iconImage = icon)
		item.setInfo(type = 'video', infoLabels = {
			'title' : title
		})
		url = __path__ + '?mode=subcat&url=http://www.dr.dk' + path + '&title=' + title
		xbmcplugin.addDirectoryItem(__handle__, url, item, True)

	xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(__handle__)


def showRecommendations():
	xbmcplugin.setContent(__handle__, 'tvshows')

	cache_path = os.path.join(SCRIPT_DATA_PATH, 'recommendations.html')
	try: date = os.path.getmtime( cache_path )
	except: date = 0
	refresh = ( ( time.time() - ( 24 * 60 * 60 ) ) >= date )
	if(refresh):
		url = urllib2.urlopen(BASE_URL)
		html = url.read()
		url.close()

		f = open(cache_path, 'w')
		f.write(html)
		f.close()
	else:
		f = open(cache_path)
		html = f.read()
		f.close()

	# remove anything but 'Redaktionens favoritter'
	html = html[html.find('<span class="tabTitle">Redaktionens favoritter</span>'):]
	addSubCategories(html)
	xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(__handle__)


def showSubCategories(url, title):
	xbmcplugin.setContent(__handle__, 'tvshows')

	cache_path = os.path.join(SCRIPT_DATA_PATH, title + '.html')
	try: date = os.path.getmtime( cache_path )
	except: date = 0
	refresh = ( ( time.time() - ( 24 * 60 * 60 ) ) >= date )
	if(refresh):
		url = urllib2.urlopen(url.replace(' ', '+'))
		html = url.read()
		url.close()

		f = open(cache_path, 'w')
		f.write(html)
		f.close()
	else:
		f = open(cache_path)
		html = f.read()
		f.close()

	# remove 'Redaktionens favoritter' as they are located on every page
	html = html[:html.find('<span class="tabTitle">Redaktionens favoritter</span>')]

	addSubCategories(html)
	xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(__handle__)

def showContent(url, title):
	html = urllib2.urlopen(url)
	addContent(html.read())
	html.close()

	xbmcplugin.endOfDirectory(__handle__)
	xbmcplugin.setContent(__handle__, 'episodes')



def addSubCategories(html):
	xbmcplugin.setContent(__handle__, 'tvshows')

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
		url = __path__ + '?mode=content&url=' + url + '&title=' + title
		xbmcplugin.addDirectoryItem(__handle__, url, item, True)


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
			infoLabels['duration'] = int(json['Duration']) / 60000
		
		item = xbmcgui.ListItem(json['Title'], iconImage = findFileLocation(json, 'Thumb'))
		item.setInfo('video', infoLabels)

		rtmp_url = findFileLocation(json, 'VideoHigh')
		if(rtmp_url == None):
			rtmp_url = findFileLocation(json, 'VideoMid')
		if(rtmp_url == None):
			rtmp_url = findFileLocation(json, 'VideoLow')

		# patch rtmp_url to work with mplayer
		rtmp_url = rtmp_url.replace('rtmp://vod.dr.dk/', 'rtmp://vod.dr.dk/bonanza/')
		xbmcplugin.addDirectoryItem(__handle__, rtmp_url, item, False)



def findFileLocation(json, type):
	for file in json['Files']:
		if(file['Type'] == type):
			return file['Location']
	return None	



if (not os.path.isdir(os.path.dirname(SCRIPT_DATA_PATH))):
	os.makedirs(os.path.dirname(SCRIPT_DATA_PATH))

params = parse_qs(sys.argv[2][1:])
if(params.has_key('mode') and params['mode'][0] == 'subcat'):
	showSubCategories(params['url'][0], params['title'][0])
elif(params.has_key('mode') and params['mode'][0] == 'content'):
	showContent(params['url'][0], params['title'][0])
elif(params.has_key('mode') and params['mode'][0] == 'search'):
	search()
elif(params.has_key('mode') and params['mode'][0] == 'recommend'):
	showRecommendations()
else:
	showCategories()

