# coding=utf-8
import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import urllib2,re,os
from cgi import parse_qs

__path__ = sys.argv[0]
__handle__ = int(sys.argv[1])

BASE_URL = 'http://onside.dk'


def CATEGORIES(): 
	xbmcplugin.setContent(__handle__, 'tvshows')
        req = urllib2.Request(BASE_URL+'/onsidetv')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
	
        match=re.compile('class="right_aligned_date"><a href="(.*?)" class="video_archive_link">(.*?)</a>', re.DOTALL).findall(link)

        for url, name in match:
		addDir(name.replace('Mere ', ''), BASE_URL + url, "subcat", "")
	xbmcplugin.addSortMethod(__handle__, xbmcplugin.SORT_METHOD_TITLE)
	xbmcplugin.endOfDirectory(__handle__)
                                       
                    
def PROGRAMLIST(url):
	xbmcplugin.setContent(__handle__, 'tvshows')
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        match=re.compile('class="item(?: item_first)?">.*?<a href="(.*?)".*?<img src="(.*?)".*?class="video-title">(.*?)</div>',re.DOTALL).findall(link)
	
        for url, image, title in match:
		addDir(title, BASE_URL + url,'playfile', image)
	nextlink = re.search('class="next" href="(.*?)"',link,re.DOTALL)
	if nextlink:
		addDir('Næste side >>', BASE_URL + nextlink.group(1), "subcat", "")
	xbmcplugin.endOfDirectory(__handle__)

def PLAYPROGRAM(url):
	xbmc.output(url)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
	videoresult = re.search('onside_video_player" href="(.*?)".*?src="(.*?)"',link,re.DOTALL)
	videoinfo = re.search('video_title">(.*?)</div>.*?video_description">(?:<p>)?(.*?)</',link,re.DOTALL)
	item = xbmcgui.ListItem(videoinfo.group(1), iconImage=videoresult.group(2), thumbnailImage=videoresult.group(2))
	item.setInfo('video', infoLabels={'title': videoinfo.group(1),'plot': videoinfo.group(2)})
	xbmc.output(videoresult.group(1))
	xbmc.Player().play(videoresult.group(1),item)

def addDir(name,url,mode,iconimage):
	item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
	item.setInfo(type = 'Video', infoLabels = {'Title' : name })
	ok=xbmcplugin.addDirectoryItem(__handle__, __path__ + '?mode='+mode+'&url='+ url + '&title=' + name, item, True)
        return ok   


params = parse_qs(sys.argv[2][1:])
if(params.has_key('mode') and params['mode'][0] == 'subcat'):
	PROGRAMLIST(params['url'][0])
elif(params.has_key('mode') and params['mode'][0] == 'playfile'):
	PLAYPROGRAM(params['url'][0])
else:
	CATEGORIES()
