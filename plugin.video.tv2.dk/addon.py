# coding = 'utf-8'
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, urllib2, re, os, time, simplejson
from cgi import parse_qs
from htmlentitydefs import name2codepoint as n2cp

__addon__ = xbmcaddon.Addon(id='plugin.video.tv2.dk')
__path__ = sys.argv[0]
__handle__ = int(sys.argv[1])
params = parse_qs(sys.argv[2][1:])

__key2title__ = {
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
SCRIPT_DATA_PATH = xbmc.translatePath(__addon__.getAddonInfo("Profile"))

def showOverview():
	json = loadJson()
	icon = os.path.join(os.getcwd(), 'icon.png')

	for key in json.keys():
		if(__key2title__.has_key(key)):
			item = xbmcgui.ListItem(__key2title__[key], iconImage = icon)
		else:
			item = xbmcgui.ListItem(key, iconImage = icon)
			
		url = __path__ + '?key=' + key
		xbmcplugin.addDirectoryItem(__handle__, url, item, True)

	xbmcplugin.setContent(__handle__, 'tvshows')
	xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(__handle__)


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
		url = __path__ + '?id=' + str(e['id'])

		xbmcplugin.addDirectoryItem(__handle__, url, item)

	xbmcplugin.setContent(__handle__, 'episodes')
	xbmcplugin.endOfDirectory(__handle__)


def playVideo(id):
		url = urllib2.urlopen('http://common.tv2.dk/flashplayer/playlistSimple.xml.php/clip-' + id + '.xml')
		playlist = url.read()
		url.close()

		m = re.search('video="([^"]+)"', playlist)

		xbmc.Player().play(m.group(1))

def loadJson():
	json_path = os.path.join(SCRIPT_DATA_PATH, 'video.js')
	try:
		date = os.path.getmtime( json_path )
	except:
		date = 0

	# cache for one hour
	refresh = ( ( time.time() - ( 60 * 60 ) ) >= date )
	if(refresh):
		url = urllib2.urlopen(BASE_URL)
		json = url.read()
		url.close()
		
		# get json part of js file
		m = re.search('data = ({.*)}', json, re.DOTALL)
		# fixup json parsing with simplejson, ie. replace ' with "
		json = re.sub(r'\'([\w-]+)\':', r'"\1":', m.group(1))

		f = open(json_path, 'w')
		f.write(json)
		f.close()

	else:
		f = open(json_path, 'r')
		json = f.read()
		f.close()

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



if (not os.path.isdir(os.path.dirname(SCRIPT_DATA_PATH))):
	os.makedirs(os.path.dirname(SCRIPT_DATA_PATH))

if(params.has_key('key')):
	showCategory(params['key'][0])
elif(params.has_key('id')):
	playVideo(params['id'][0])
else:
	showOverview()

