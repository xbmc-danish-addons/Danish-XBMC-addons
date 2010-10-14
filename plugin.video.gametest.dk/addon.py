import os, re
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from danishaddons import *

BASE_URL = 'http://www.gametest.dk/'
FLV_URL = BASE_URL + 'gametesttest/reviews/%s/%s.flv'
REVIEWS_URL = BASE_URL + 'index.php?anmeldelser=alle'
PAGE_URL = BASE_URL + 'index.php?page=%s'

CATEGORIES = [
	{'title' : 'Anmeldelser', 'params' : 'reviews'},
	{'title' : 'Retro', 'params' : 'retro'},
	{'title' : 'Stunts', 'params' : 'stunts'},
]

def showOverview():
	html = web.downloadAndCacheUrl(BASE_URL, os.path.join(ADDON_DATA_PATH, 'overview.html'), 24 * 60)

	m = re.search('Sendt den ([^<]+).*?<ul>(.*?)</ul>', html, re.DOTALL)
	date = m.group(1)
	title = 'Seneste udsendelse: %s' % date
	games = m.group(2)

	icon = os.path.join(os.getcwd(), 'icon.png')
	item = xbmcgui.ListItem(title, iconImage = icon)
	item.setInfo('video', {
		'title' : title,
		'plot' : 'Spil testet:' + games.replace('<li>', '').replace('</li>', '\n'),
		'date' : date.replace('-', '.')
	})
	url = FLV_URL % ('file', 'Programmet')
	xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item)

	for idx, c in enumerate(CATEGORIES):
		item = xbmcgui.ListItem(c['title'], iconImage = icon)
		url = ADDON_PATH + '?' + c['params']
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.setContent(ADDON_HANDLE, 'episodes')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def showReviews():
	html = web.downloadAndCacheUrl(REVIEWS_URL, os.path.join(ADDON_DATA_PATH, 'reviews.html'), 24 * 60)

	for m in re.finditer("index.php\?play=(.*?)&type=anmeldelse'><img src=' (.*?)'.*?anmeldelse'>(.*?)</a>.*?af: (.*?)</a>(.*?)time'>(.*?)</p>", html, re.DOTALL):
		slug = m.group(1)
		icon = m.group(2)
		title = m.group(3)
		author = m.group(4)
		rating = m.group(5).count('good.png')
		date = m.group(6)

		item = xbmcgui.ListItem(title, iconImage = BASE_URL + icon)
		item.setInfo('video', {
			'title' : title,
			'date' : date.replace('-', '.'),
			'year' : int(date[6:]),
			'credits' : author,
			'plot' : title,
			'rating' : rating
		})
		url = FLV_URL % ('file', slug)
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item)

	xbmcplugin.setContent(ADDON_HANDLE, 'episodes')
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def showPage(page):
	html = web.downloadAndCacheUrl(PAGE_URL % page, os.path.join(ADDON_DATA_PATH, '%s.html' % page), 24 * 60)

	for m in re.finditer("index.php\?play=(.*?)&type=.*?src=[ \"](.*?)[ \"](.*?<b>(.*?)</b>.*?af:.*?>(.*?)</a>)?", html, re.DOTALL):
		slug = m.group(1)
		icon = m.group(2)
		title = m.group(4)
		author = m.group(5)

		item = xbmcgui.ListItem(title, iconImage = BASE_URL + icon)
		item.setInfo('video', {
			'title' : title,
			'credits' : author,
			'plot' : title
		})

		url = FLV_URL % ('stunts', slug)
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item)

	xbmcplugin.setContent(ADDON_HANDLE, 'episodes')
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)




if(ADDON_PARAMS.has_key('reviews')):
	showReviews()
elif(ADDON_PARAMS.has_key('retro')):
	showPage('retro')
elif(ADDON_PARAMS.has_key('stunts')):
	showPage('stunts')
else:
	showOverview()

