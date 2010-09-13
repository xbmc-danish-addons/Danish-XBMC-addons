import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import sys, os
from cgi import parse_qs

__addon__ = xbmcaddon.Addon(id='plugin.video.dr.dk.live')
__path__ = sys.argv[0]
__handle__ = int(sys.argv[1])
params = parse_qs(sys.argv[2][1:])

__channels__ = [
	{'name' : 'DR1', 'url' : 'rtmp://rtmplive.dr.dk/live/livedr01astream3'},
	{'name' : 'DR2', 'url' : 'rtmp://rtmplive.dr.dk/live/livedr02astream3'},
	{'name' : 'DR Update', 'url' : 'rtmp://rtmplive.dr.dk/live/livedr03astream3'},
	{'name' : 'DR K', 'url' : 'rtmp://rtmplive.dr.dk/live/livedr04astream3'},
	{'name' : 'DR Ramasjang', 'url' : 'rtmp://rtmplive.dr.dk/live/livedr05astream3'}
]

def showChannels():

	for idx, c in enumerate(__channels__):
		icon = os.getcwd() + "/resources/logos/" + c['name'] + ".png"

		item = xbmcgui.ListItem(c['name'], iconImage = icon)
		url = __path__ + '?idx=' + str(idx)
		xbmcplugin.addDirectoryItem(__handle__, url, item, True)

	xbmcplugin.endOfDirectory(__handle__)

def playChannel(idx):
	c = __channels__[int(idx)]
	item = xbmcgui.ListItem(c['name'])
	item.setProperty("IsLive", "true")
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(c['url'], item)


if(params.has_key('idx')):
	playChannel(params['idx'][0])
else:
	showChannels()

