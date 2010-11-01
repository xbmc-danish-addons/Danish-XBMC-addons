import re
import datetime
import time
from elementtree import ElementTree

from danishaddons import *

CHANNELS_URL = 'http://yousee.tv'
PROGRAMS_URL = 'http://yousee.tv/feeds/tvguide/getprogrammes/?channel=%s'

STREAMS = {
	'dr.dk/mas/whatson/channel/DR1' : 'rtmp://rtmplive.dr.dk/live/livedr01astream3'
}

class Source:

	def __init__(self):
		self.date = datetime.datetime.today()

	def getChannelList(self):
		html = web.downloadAndCacheUrl(CHANNELS_URL, os.path.join(ADDON_DATA_PATH, 'youseetv-channels.json'), 60)
		channels = []

		for m in re.finditer('href="/livetv/([^"]+)".*?src="(http://cloud.yousee.tv/static/img/logos/large_[^"]+)" alt="(.*?)"', html):
			channels.append({
				'id' : m.group(1),
				'title' : m.group(3),
				'logo' : m.group(2)
			})
	
		return channels
	
	def getProgramList(self, channelId):
		url = PROGRAMS_URL % channelId.replace(' ', '%20')
		cachePath = os.path.join(ADDON_DATA_PATH, 'youseetv-' + channelId.replace(' ', '_')) 
		xml = web.downloadAndCacheUrl(url, cachePath, 60)
		programs = []

		doc = ElementTree.fromstring(xml)

		for program in doc.findall('programme'):
			programs.append({
				'channel_id' : channelId,
				'title' : program.find('title').text,
				'start_date' : self._parseDate(program.find('start').text),
				'end_date' : self._parseDate(program.find('end').text),
				'description' : program.find('description').text
			})

		return programs

	def getStreamURL(self, channelId):
		if(STREAMS.has_key(channelId)):
			return STREAMS[channelId]
		else:
			return None

	def _parseDate(self, dateString):
		t = time.strptime(dateString, '%Y,%m,%d,%H,%M,%S')
		return datetime.datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)

			
	
