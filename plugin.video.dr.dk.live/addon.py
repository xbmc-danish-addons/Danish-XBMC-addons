import os
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
from danishaddons import *

# High   : 1000 kb/s
# Medium :  500 kb/s
# Low    :  300 kb/s

CHANNELS = [
	# From: http://dr.dk/TV/Live/UPlayer?banner=false&deepLinking=true&useStartControls=false&width=830&height=467&disableWmode=true
	{'name' : 'DR1', 'urls' : {
			'high' : 'rtmp://rtmplive.dr.dk/live/livedr01astream3',
			'medium' : 'rtmp://rtmplive.dr.dk/live/livedr01astream2',
			'low' : 'rtmp://rtmplive.dr.dk/live/livedr01astream1'
		}
	},
	{'name' : 'DR2', 'urls' : {
			'high' : 'rtmp://rtmplive.dr.dk/live/livedr02astream3',
			'medium' : 'rtmp://rtmplive.dr.dk/live/livedr02astream2',
			'low' : 'rtmp://rtmplive.dr.dk/live/livedr02astream1'
		}
	},
	{'name' : 'DR Update', 'urls' : {
			'high' : 'rtmp://rtmplive.dr.dk/live/livedr03astream3',
			'medium' : 'rtmp://rtmplive.dr.dk/live/livedr03astream2',
			'low' : 'rtmp://rtmplive.dr.dk/live/livedr03astream1'
		}
	},
	{'name' : 'DR K', 'urls' : {
			'high' : 'rtmp://rtmplive.dr.dk/live/livedr04astream3',
			'medium' : 'rtmp://rtmplive.dr.dk/live/livedr04astream2',
			'low' : 'rtmp://rtmplive.dr.dk/live/livedr04astream1'
		}
	},
	{'name' : 'DR Ramasjang', 'urls' : {
			'high' : 'rtmp://rtmplive.dr.dk/live/livedr05astream3',
			'medium' : 'rtmp://rtmplive.dr.dk/live/livedr05astream2',
			'low' : 'rtmp://rtmplive.dr.dk/live/livedr05astream1'
		}
	},

	# From: http://www.24nordjyske.dk/webtv_high.asp
	{'name' : '24 Nordjyske', 'urls' : {
			'high' : 'mms://stream.nordjyske.dk/24nordjyske - Full Broadcast Quality',
			'medium' : 'mms://stream.nordjyske.dk/24nordjyske'
		}
	},
	# From: http://ft.arkena.tv/xml/core_player_clip_data_v2.php?wtve=187&wtvl=2&wtvk=012536940751284
	{'name' : 'Folketinget', 'urls' : {
			'high' : 'rtmp://chip.arkena.com/webtvftfl/hi1'
		}
	}
]

QUALITY = ADDON.getSetting('quality').lower()

def showChannels():

	for idx, c in enumerate(CHANNELS):
		icon = os.getcwd() + "/resources/logos/" + c['name'].replace(" ", "_") + ".png"

		if(c['urls'].has_key(QUALITY)):
			item = xbmcgui.ListItem(c['name'], iconImage = icon)
			url = ADDON_PATH + '?idx=' + str(idx)
			xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, item, True)

	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playChannel(idx):
	c = CHANNELS[int(idx)]

	if(c['urls'].has_key(QUALITY)):
		item = xbmcgui.ListItem(c['name'])
		item.setProperty("IsLive", "true")
		xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(c['urls'][QUALITY], item)
	else:
		d = xbmcgui.Dialog()
		d.ok(c['name'], 'Denne kanal kan ikke afspilles i %s kvalitet.' % QUALITY.capitalize(), 'Skift kvalitet i indstillingerne og prøv igen.')

if(ADDON_PARAMS.has_key('idx')):
	playChannel(ADDON_PARAMS['idx'])
else:
	showChannels()

