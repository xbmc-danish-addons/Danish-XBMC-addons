import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, urllib2, re, os, pickle, time
from resources.lib.feedparser import feedparser
from cgi import parse_qs

__addon__ = xbmcaddon.Addon(id='plugin.video.dr.dk')
__language__ = __addon__.getLocalizedString
__path__ = sys.argv[0]
__handle__ = int(sys.argv[1])
params = parse_qs(sys.argv[2][1:])

BASE_URL = 'http://www.dr.dk/podcast/Video'
FEED_URL_TEMPLATE = 'http://vpodcast.dr.dk/feeds/%s.xml'
SCRIPT_DATA_PATH = xbmc.translatePath(__addon__.getAddonInfo("Profile"))

def showOverview():
	xbmcplugin.setContent(__handle__, 'tvshows')

	html_path = os.path.join(SCRIPT_DATA_PATH, 'video.html')
	try: date = os.path.getmtime( html_path )
	except: date = 0
	refresh = ( ( time.time() - ( 24 * 60 * 60 ) ) >= date )
	if(refresh):
		url = urllib2.urlopen(BASE_URL)
		html = url.read()
		url.close()

		f = open(html_path, 'w')
		f.write(html)
		f.close()

	else:
		f = open(html_path)
		html = f.read()
		f.close()

	dialog = xbmcgui.DialogProgress()
	dialog.create( __language__(30001) )


	feed_count = html.count(FEED_URL_TEMPLATE[:15])
	feed_idx = 0
	for m in re.finditer(FEED_URL_TEMPLATE % '(.*)\\', html):
		feed_idx+=1
		key = m.group(1)
		details = getFeedDetails(key)

		item = xbmcgui.ListItem(details['title'], iconImage = details['image_path'])
		item.setInfo(type = 'video', infoLabels = {
			'title' : details['title'],
			'plot' : details['description']
		})
		url = __path__ + '?key=' + key
		xbmcplugin.addDirectoryItem(__handle__, url, item, True)

		dialog.update((feed_idx * 100 / feed_count), details['title'])
		if(dialog.iscanceled()):
			break

	dialog.close()
	xbmcplugin.endOfDirectory(__handle__)

def showFeed(key):
	d = feedparser.parse(FEED_URL_TEMPLATE % key)
	details = getFeedDetails(key)

	for e in d.entries:
		item = xbmcgui.ListItem(e.title, iconImage = details['image_path'])
		item.setLabel2(e.description)
		item.setInfo(type = 'video', infoLabels = {
			'tvshowtitle' : d.channel.title,
			'title' : e.title,
			'plot' : e.description,
			'duration' : parseDuration(e.itunes_duration),
			'aired' : parsePubDate(e.updated_parsed),
			'year' : e.updated_parsed[0],
			'director' : e.author,
			'writer' : e.author
			
		})
		xbmcplugin.addDirectoryItem(__handle__, e.enclosures[0].href, item, False)

	xbmcplugin.endOfDirectory(__handle__)

	xbmcplugin.setContent(__handle__, 'episodes')
	xbmcplugin.setPluginCategory(__handle__, d.channel.title)

def getFeedDetails(key):
	details_path = os.path.join(SCRIPT_DATA_PATH, key + '.pickle')
	details = {}

	if(not os.path.exists(details_path)):
		d = feedparser.parse(FEED_URL_TEMPLATE % key)

		details['title'] = d.feed.title
		details['description'] = d.feed.subtitle
		details['image_path'] = d.channel.image.href

		f = open(details_path, 'wb')
		pickle.dump(details, f)
		f.close()
	else:
		f = open(details_path, 'rb')
		details = pickle.load(f)
		f.close()

	return details

def parseDuration(duration):
	print duration
	if(duration[:3] == '00:'):
		duration = duration[3:]
	return duration[:duration.find(':')]

def parsePubDate(pubDate):
	return '%d-%d-%d' % (pubDate[0], pubDate[1], pubDate[2])



if (not os.path.isdir(os.path.dirname(SCRIPT_DATA_PATH))):
	os.makedirs(os.path.dirname(SCRIPT_DATA_PATH))

if(params.has_key('key')):
	showFeed(params['key'][0])
else:
	showOverview()

