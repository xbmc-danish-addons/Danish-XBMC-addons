import os
import sys

import xbmc
import xbmcaddon

import web

# Convenience methods
def msg(id):
	return ADDON.getLocalizedString(id)

def parseParams(input):
	params = {}
	for pair in input.split('&'):
		if(pair.find('=') >= 0):
			keyvalue = pair.split('=', 1)
			params[keyvalue[0]] = keyvalue[1]
		else:
			params[pair] = None

	return params

# Initialize convenience constants
ADDON_PATH = sys.argv[0]
ADDON_ID = ADDON_PATH[9:-1]
ADDON_HANDLE = int(sys.argv[1])
ADDON = xbmcaddon.Addon(id = ADDON_ID)
ADDON_DATA_PATH = xbmc.translatePath(ADDON.getAddonInfo("Profile"))
ADDON_PARAMS = parseParams(sys.argv[2][1:])

# Create addon data path
if(not os.path.isdir(os.path.dirname(ADDON_DATA_PATH))):
	os.makedirs(os.path.dirname(ADDON_DATA_PATH))
