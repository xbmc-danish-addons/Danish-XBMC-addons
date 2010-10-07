# coding=utf-8
import os, re, urllib, urllib2, datetime
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from danishaddons import *

REGIONS = [
	{'name' : 'TV Syd', 'id' : '1'},
	{'name' : 'TV2/Fyn', 'id' : '2'},
	{'name' : 'TV2/Øst', 'id' : '3'},
	{'name' : 'TV2/Nord', 'id' : '4'},
	{'name' : 'TV2/Lorry', 'id' : '5'},
	{'name' : 'TV2/Midt-Vest', 'id' : '6'},
	{'name' : 'TV2/Østjylland', 'id' : '7'},
	{'name' : 'TV2/Bornholm', 'id' : '8'},
	{'name' : 'Danmark Rundt', 'id' : '9'},
]

def showRegions():
	for idx, r in enumerate(REGIONS):
		icon = os.getcwd() + "/resources/logos/%s.png" % r['id']

		item = xbmcgui.ListItem(r['name'], iconImage = icon)
		url = ADDON_PATH + '?idx=' + str(idx)
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def showDatesFromLastWeek(idx):
	r = REGIONS[int(idx)]

	url = urllib2.urlopen('http://www.tv2regionerne.dk/search.aspx?r=%s' % r['id'])
	html = url.read()
	url.close()

	for m in re.finditer("\('calSearch','([0-9]+)'\)", html):
		date = calculateDate(m.group(1))
		item = xbmcgui.ListItem(date.strftime('%A, den %d. %B %Y'))
		item.setInfo('video', {
			'date' : date.strftime('%d.%m.%Y')
		})

		url = ADDON_PATH + '?date=' + date.strftime('%Y%m%d') + '&idx=' + idx
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.setContent(ADDON_HANDLE, 'tvshows')
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_DATE)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def showClips(dateStr, idx):
	y = int(dateStr[0:4])
	m = int(dateStr[4:6])
	d = int(dateStr[6:8])
	date = datetime.date(y, m, d)

	loadClipsForDate(date, idx)


def loadClipsForDate(date, idx):
	r = REGIONS[int(idx)]
	dateId = calculateDateId(date)

	# Find ASP.NET initial page state
	url = urllib2.urlopen('http://www.tv2regionerne.dk/search.aspx?r=%s' % r['id'])
	initialState = url.read()
	url.close()

	# Retrieve actual page
	viewState = re.search('id="__VIEWSTATE" value="([^"]*)"', initialState).group(1)
	eventValidation = re.search('id="__EVENTVALIDATION" value="([^"]*)"', initialState).group(1)

	data = {
		'__EVENTTARGET' : 'calSearch',
		'__EVENTARGUMENT' : dateId,
		'__VIEWSTATE' : viewState,
		'__EVENTVALIDATION' : eventValidation,
		'rbAdvSearch' : '0'
	}

	req = urllib2.Request('http://www.tv2regionerne.dk/search.aspx?r=%s' % r['id'], urllib.urlencode(data))
	url = urllib2.urlopen(req)
	html = url.read()
	url.close()

	for m in re.finditer('(id="udsendelse">([^<]+)</div>.*?)?player.aspx\?id=([0-9]+)[^>]+>([^<]+)</a>.*?\(([0-9:]+)\).*?class="beskrivelse"[^>]+>([^<]+)</td>', html, re.DOTALL):
		time = m.group(2)
		id = m.group(3)
		title = m.group(4)
		duration = m.group(5)
		description = m.group(6)

		if(time != None):
			title = title + ' (' + time + ')'

		item = xbmcgui.ListItem(title)
		item.setInfo(type = 'video', infoLabels = {
			'title' : title,
			'duration' : duration,
			'plot' : description
		})
		url = ADDON_PATH + '?id=' + str(id)
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item)
	
	xbmcplugin.setContent(ADDON_HANDLE, 'episodes')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def playClip(id):
	playlist = web.downloadAndCacheUrl('http://www.tv2regionerne.dk/Video.aspx?id=' + id, os.path.join(ADDON_DATA_PATH, 'clip_' + id + '.asx'), 0)

	m = re.search('<ref href="([^"]+)"', playlist, re.IGNORECASE)
	href = m.group(1)

	m = re.search('<starttime value="([^"]+)" />', playlist, re.IGNORECASE)
	starttime = m.group(1)
	parts = starttime.split(':')
	seconds = (int(parts[0]) * 3600) + (int(parts[1]) * 60) + int(parts[2])

	player = xbmc.Player()
	player.play(href)
	player.seekTime(seconds)


def calculateDateId(date):
	delta = date - datetime.date(2000, 1, 1)

	return delta.days

def calculateDate(dateId):
	return datetime.date(2000, 1, 1) + datetime.timedelta(int(dateId))


if(ADDON_PARAMS.has_key('date') and ADDON_PARAMS.has_key('idx')):
	showClips(ADDON_PARAMS['date'], ADDON_PARAMS['idx'])
elif(ADDON_PARAMS.has_key('id')):
	playClip(ADDON_PARAMS['id'])
elif(ADDON_PARAMS.has_key('idx')):
	showDatesFromLastWeek(ADDON_PARAMS['idx'])
else:
	showRegions()

