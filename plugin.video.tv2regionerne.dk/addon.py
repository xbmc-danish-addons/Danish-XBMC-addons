# coding=utf-8
import os
import sys

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import danishaddons
import danishaddons.web

import sources.tv2nord
import sources.tv2syd
import sources.tv2fyn
import sources.tv2oj
import sources.tv2lorry
import sources.tv2midtvest
import sources.tv2east
import sources.tv2bornholm

REGIONS = [
    {'name' : 'TV Syd', 'slug' : sources.tv2syd.SLUG},
    {'name' : 'TV2/Fyn', 'slug' : sources.tv2fyn.SLUG},
    {'name' : 'TV2/Øst', 'slug' : sources.tv2east.SLUG},
    {'name' : 'TV2/Nord', 'slug' : sources.tv2nord.SLUG},
    {'name' : 'TV2/Lorry', 'slug' : sources.tv2lorry.SLUG},
    {'name' : 'TV2/Midt-Vest', 'slug' : sources.tv2midtvest.SLUG},
    {'name' : 'TV2/Østjylland', 'slug' : sources.tv2oj.SLUG},

# todo tv2bornholm bruger rtmp over ssl
#    {'name' : 'TV2/Bornholm', 'slug' : sources.tv2bornholm.SLUG},
]

def showRegions():
    for r in REGIONS:
        if r['slug'] is not None:
            icon = os.getcwd() + "/resources/logos/%s.png" % r['slug']
            item = xbmcgui.ListItem(r['name'], iconImage = icon)
            url = danishaddons.ADDON_PATH + '?slug=' + r['slug']
            xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(danishaddons.ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)


if __name__ == '__main__':
    danishaddons.init(sys.argv)

    if danishaddons.ADDON_PARAMS.has_key('slug'):
        slug = danishaddons.ADDON_PARAMS['slug']

        if slug == sources.tv2nord.SLUG:
            sources.tv2nord.invoke(danishaddons.ADDON_PARAMS)
        elif slug == sources.tv2syd.SLUG:
            sources.tv2syd.invoke(danishaddons.ADDON_PARAMS)
        elif slug == sources.tv2fyn.SLUG:
            sources.tv2fyn.invoke(danishaddons.ADDON_PARAMS)
        elif slug == sources.tv2oj.SLUG:
            sources.tv2oj.invoke(danishaddons.ADDON_PARAMS)
        elif slug == sources.tv2lorry.SLUG:
            sources.tv2lorry.invoke(danishaddons.ADDON_PARAMS)
        elif slug == sources.tv2midtvest.SLUG:
            sources.tv2midtvest.invoke(danishaddons.ADDON_PARAMS)
        elif slug == sources.tv2east.SLUG:
            sources.tv2east.invoke(danishaddons.ADDON_PARAMS)
        elif slug == sources.tv2bornholm.SLUG:
            sources.tv2bornholm.invoke(danishaddons.ADDON_PARAMS)
    else:
        showRegions()

