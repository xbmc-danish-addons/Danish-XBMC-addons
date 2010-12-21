import re
import string
import os
import sys

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

import danishaddons
import danishaddons.web
import danishaddons.info

URL = 'http://www.dr.dk/pirattv/'

def showPrograms():
    piratHtml = danishaddons.web.downloadAndCacheUrl(URL + 'programmer/?q=pirat', os.path.join(danishaddons.ADDON_DATA_PATH, 'pirat.html'), 60)
    arkivHtml = danishaddons.web.downloadAndCacheUrl(URL + 'programmer/?q=arkiv', os.path.join(danishaddons.ADDON_DATA_PATH, 'arkiv.html'), 60)

    html = piratHtml + arkivHtml

    for m in re.finditer('<h3>.*?<a href="/pirattv/programmer/(.*?)".*?title=".*?">(.*?)</a>.*?</h3>.*?<a href="(.*?)" rel="thumbnail">.*?</a>.*?<p>(.*?)</p>', html, re.DOTALL):
        slug = m.group(1)
        title = string.capwords(danishaddons.web.decodeHtmlEntities(unicode(m.group(2), 'UTF-8')))
        icon = m.group(3)
        description = m.group(4)

        item = xbmcgui.ListItem(title, iconImage = icon)
        item.setInfo(type = 'video', infoLabels = {
            'title' : title,
            'plot' : description
        })
        url = danishaddons.ADDON_PATH + '?slug=' + slug
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, True)

    xbmcplugin.addSortMethod(danishaddons.ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)

def showClips(slug, page = None):
    url = URL + 'programmer/' + slug
    if(page is not None):
        url += '/side-%s/?' % page
    html = danishaddons.web.downloadAndCacheUrl(url, os.path.join(danishaddons.ADDON_DATA_PATH, '%s-%s.html' % (slug, page)), 60)

    for m in re.finditer('<h3>.*?<a href="/pirattv/programmer/(.*?)/(side-.*?/)?(.*?)" title="(.*?)">.*?</a>.*?<a href="(.*?)" rel="thumbnail">.*?<p>(.*?)</p>.*?<span class="rating">(.*?)</span>.*?<span class="duration">(.*?)</span>', html, re.DOTALL):
        slug = m.group(1)
        clipSlug = m.group(3)
        title = m.group(4)
        icon = m.group(5)
        description = m.group(6)
        rating = m.group(7)
        duration = m.group(8)

        infoLabels = dict()
        infoLabels['title'] = string.capwords(danishaddons.web.decodeHtmlEntities(unicode(title, 'UTF-8')))
        infoLabels['plot'] = danishaddons.web.decodeHtmlEntities(unicode(description, 'UTF-8'))
        infoLabels['rating'] = int(rating) * 2
        infoLabels['duration'] = danishaddons.info.secondsToDuration(int(duration))

        item = xbmcgui.ListItem(infoLabels['title'], iconImage = icon)
        item.setInfo('video', infoLabels)
        item.setProperty('IsPlayable', 'true')

        url = danishaddons.ADDON_PATH + '?slug=%s&clip=%s' % (slug, clipSlug)
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, False)

    m = re.search('<li class="next"><a href=".*?/side-(.*?)/', html)
    if(m is not None):
        item = xbmcgui.ListItem('Flere...')
        url = danishaddons.ADDON_PATH + '?slug=%s&page=%s' % (slug, m.group(1))
        xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item, True)

    xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)

def playClip(slug, clipSlug):
    html = danishaddons.web.downloadAndCacheUrl(URL + 'programmer/' + slug + '/' + clipSlug, os.path.join(
            danishaddons.ADDON_DATA_PATH, '%s-%s.html' % (slug, clipSlug)), 60)

    m = re.search("mediaFile: '(rtmp://.*?/)(.*?/)(.*?)'", html)
    url = m.group(1) + m.group(2) + m.group(2) + m.group(3)

    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(danishaddons.ADDON_HANDLE, True, item)


if __name__ == '__main__':
    danishaddons.init(sys.argv)

    if(danishaddons.ADDON_PARAMS.has_key('slug') and danishaddons.ADDON_PARAMS.has_key('clip')):
        playClip(danishaddons.ADDON_PARAMS['slug'], danishaddons.ADDON_PARAMS['clip'])
    if(danishaddons.ADDON_PARAMS.has_key('slug')):
        if(danishaddons.ADDON_PARAMS.has_key('page')):
            showClips(danishaddons.ADDON_PARAMS['slug'], danishaddons.ADDON_PARAMS['page'])
        else:
            showClips(danishaddons.ADDON_PARAMS['slug'])
    else:
        showPrograms()

