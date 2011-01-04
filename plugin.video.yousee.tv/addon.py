import os
import sys
import urllib
import urllib2
import cookielib

import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from elementtree import ElementTree
import danishaddons
import danishaddons.web

URL = 'http://yousee.tv/feeds/player/livetv/%s/'
FANART = os.getcwd() + '/fanart.jpg'

class YouseeTv:
    def __init__(self):
        self.cookieJar = cookielib.LWPCookieJar()
        self.cookieFile = os.path.join(danishaddons.ADDON_DATA_PATH, 'cookies.lwp')
        if os.path.isfile(self.cookieFile):
            self.cookieJar.load(self.cookieFile)

        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
        urllib2.install_opener(opener)

        if danishaddons.ADDON.getSetting('username') == '' or danishaddons.ADDON.getSetting('password') == '':
            xbmcgui.Dialog().ok(danishaddons.msg(30001), danishaddons.msg(30002), danishaddons.msg(30003))
            danishaddons.ADDON.openSettings()

    def showChannels(self):
        doc = self.loadDocForChannel()
        if doc is None:
            return

        for channel in doc.findall('channels/channel'):
            name = channel.findtext('name')
            logoLarge = channel.findtext('logo_large')

            item = xbmcgui.ListItem(name, iconImage = logoLarge)
            item.setProperty('Fanart_Image', FANART)
            url = danishaddons.ADDON_PATH + '?xml=' + channel.findtext('xml').replace(' ', '%20')
            xbmcplugin.addDirectoryItem(danishaddons.ADDON_HANDLE, url, item)

        xbmcplugin.endOfDirectory(danishaddons.ADDON_HANDLE)

    def playChannel(self, xmlUrl):
        xml = danishaddons.web.downloadUrl(xmlUrl)
        doc = ElementTree.fromstring(xml)

        if danishaddons.ADDON.getSetting('quality') == '1200':
            streamIdx = 1
        else:
            streamIdx = 0
        
        stream = doc.findall('server/streams/stream/name')[streamIdx].text
        swfUrl = "http://yousee.tv/design/swf/YouSeeVideoPlayer_beta.swf"
        pageUrl = "http://yousee.tv/livetv/"
        tcUrl = "rtmpe://live.fmis.yousee.tv/live"
        conn = 'S:serverurl:%s' % tcUrl

        rtmpUrl = 'rtmpe://live.fmis.yousee.tv/live/%s swfUrl=%s swfVfy=1 pageUrl=%s tcUrl=%s conn=%s' % (stream, swfUrl, pageUrl, tcUrl, conn)
        print "Attempting to play url: %s" % rtmpUrl

        item = xbmcgui.ListItem(doc.findtext('channelname'), thumbnailImage = doc.findtext('channellogo'))
        item.setProperty("IsLive", "true")
        xbmc.Player().play(rtmpUrl, item)

    def login(self):
        username = danishaddons.ADDON.getSetting('username')
        password = danishaddons.ADDON.getSetting('password')

        postData = urllib.urlencode({'username' : username, 'password' : password, 'remember' : 0})
        req = urllib2.Request('http://yousee.tv/sso/login', postData)
        res = urllib2.urlopen(req)
        self.cookieJar.save(self.cookieFile)

        # 1 means logged in ok
        return res.read() == '1'
    
    def loadDocForChannel(self, slug = 'dr1'):
        loggedIn = False
        for cookie in self.cookieJar:
            if cookie.name == 'encyspro':
                loggedIn = True
                break

        if not loggedIn and not self.login():
            xbmcgui.Dialog().ok(danishaddons.msg(30010), danishaddons.msg(30011))
            return None

        xml = danishaddons.web.downloadUrl(URL % slug)
        doc = ElementTree.fromstring(xml)
        return doc


if __name__ == '__main__':
    danishaddons.init(sys.argv)

    ytv = YouseeTv()
    if danishaddons.ADDON_PARAMS.has_key('xml'):
        ytv.playChannel(danishaddons.ADDON_PARAMS['xml'])
    else:
        ytv.showChannels()

