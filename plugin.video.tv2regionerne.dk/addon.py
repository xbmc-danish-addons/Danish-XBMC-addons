# coding=utf-8
import os, re, urllib, urllib2, datetime
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from danishaddons import *

REGIONS = [
	{'name' : 'TV Syd', 'id' : '1'},
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

	xbmcplugin.endOfDirectory(ADDON_HANDLE)


def showDatesFromLastWeek(idx):
	r = REGIONS[int(idx)]

	today = datetime.date.today()
	for i in range(7):
		d = today - datetime.timedelta(i)
		item = xbmcgui.ListItem(d.strftime('%A, den %d. %B %Y'))

		url = ADDON_PATH + '?date=' + d.strftime('%Y%m%d') + '&idx=' + idx
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

#	item = xbmcgui.ListItem('Tidligere dato')
#	url = ADDON_PATH + '?choose=date&idx=' + idx
#	xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)
	
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def chooseDate(idx):
	r = REGIONS[int(idx)]

	dialog = xbmcgui.Dialog()
	d = dialog.numeric(1, 'Indtast dato')

	if(d != None):
		parts = d.split('/')
		date = datetime.date(int(parts[2]), int(parts[1]), int(parts[0]))
		loadClipsForDate(date, idx)

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

#	lastFocus = re.search('id="__LASTFOCUS" value="([^"]*)"', initialState).group(1)
	viewState = re.search('id="__VIEWSTATE" value="([^"]*)"', initialState).group(1)
	eventValidation = re.search('id="__EVENTVALIDATION" value="([^"]*)"', initialState).group(1)

	data = {
		'__EVENTTARGET' : 'calSearch',
		'__EVENTARGUMENT' : dateId,
		'__VIEWSTATE' : viewState,
		'__EVENTVALIDATION' : eventValidation,
		'rbAdvSearch' : '0'
	}

	# Retrieve actual page
	req = urllib2.Request('http://www.tv2regionerne.dk/search.aspx?r=%s' % r['id'], urllib.urlencode(data))
	url = urllib2.urlopen(req)
	html = url.read()
	url.close()

	for m in re.finditer('player.aspx\?id=([0-9]+)[^>]+>([^<]+)</a>.*?\(([0-9:]+)\).*?class="beskrivelse"[^>]+>([^<]+)</td>', html, re.DOTALL):
		id = m.group(1)
		title = m.group(2)
		duration = m.group(3)
		description = m.group(4)

		item = xbmcgui.ListItem(title)
		item.setInfo(type = 'video', infoLabels = {
			'title' : title,
			'duration' : duration,
			'plot' : description
		})
		url = ADDON_PATH + '?id=' + str(id)
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item)
	
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

if(ADDON_PARAMS.has_key('choose') and ADDON_PARAMS.has_key('idx')):
	chooseDate(ADDON_PARAMS['idx'])
elif(ADDON_PARAMS.has_key('date') and ADDON_PARAMS.has_key('idx')):
	showClips(ADDON_PARAMS['date'], ADDON_PARAMS['idx'])
elif(ADDON_PARAMS.has_key('id')):
	playClip(ADDON_PARAMS['id'])
elif(ADDON_PARAMS.has_key('idx')):
	showDatesFromLastWeek(ADDON_PARAMS['idx'])
else:
	showRegions()

print sys.argv
