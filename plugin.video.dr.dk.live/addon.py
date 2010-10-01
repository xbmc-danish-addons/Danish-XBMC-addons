import os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from danishaddons import *

CHANNELS = [
	{'name' : 'DR1', 'url' : 'rtmp://rtmplive.dr.dk/live/livedr01astream3'},
	{'name' : 'DR2', 'url' : 'rtmp://rtmplive.dr.dk/live/livedr02astream3'},
	{'name' : 'DR Update', 'url' : 'rtmp://rtmplive.dr.dk/live/livedr03astream3'},
	{'name' : 'DR K', 'url' : 'rtmp://rtmplive.dr.dk/live/livedr04astream3'},
	{'name' : 'DR Ramasjang', 'url' : 'rtmp://rtmplive.dr.dk/live/livedr05astream3'}
]

def showChannels():

	for idx, c in enumerate(CHANNELS):
		icon = os.getcwd() + "/resources/logos/" + c['name'].replace(" ", "_") + ".png"

		item = xbmcgui.ListItem(c['name'], iconImage = icon)
		url = ADDON_PATH + '?idx=' + str(idx)
		xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playChannel(idx):
	c = CHANNELS[int(idx)]
	item = xbmcgui.ListItem(c['name'])
	item.setProperty("IsLive", "true")
	xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(c['url'], item)


if(ADDON_PARAMS.has_key('idx')):
	playChannel(ADDON_PARAMS['idx'])
else:
	showChannels()

