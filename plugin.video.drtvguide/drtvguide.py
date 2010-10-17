import xbmc
import xbmcgui
import xbmcplugin
import sys
import urllib
import simplejson as json
import time
import datetime
import re

from danishaddons import *

class DRTVGuide:
  def __init__(self):
    self.now = datetime.datetime.now()
    
  def CreateDirectoryItem(self, folder=False, items=None, country=None):
    self.folder = folder
    self.country = country
    countries = {'da' : ('Danish', 1),
                 'se' : ('Swedish', 2),
                 'no' : ('Norwegian', 3),
                 'fr' : ('French', 4),
                 'en' : ('English', 6),
                 'de' : ('German', 7),
                 'all' : ('All', 0),}
    if(folder and items == None):
      for country in countries.keys():
        self.listitem = xbmcgui.ListItem(label=countries[country][0])
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url=ADDON_PATH + '?country=' + country, listitem=self.listitem, isFolder=self.folder, totalItems=len(countries))
      xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
      xbmcplugin.endOfDirectory(ADDON_HANDLE)
    elif(folder):
      for item in items.keys():
        self.name = unicode(items[item][1]).encode('utf-8')
        if(':' in self.name):
          self.name = self.name.split(':')[1]
        self.source_url = items[item][3]
        self.thumbnailImage = 'DefaultFolder.png'
        self.countryCode = int(items[item][4])
        if(countries[country][1] == 0):
          self.listitem = xbmcgui.ListItem(label=self.name, thumbnailImage=(self.thumbnailImage))
          xbmcplugin.addDirectoryItem(ADDON_HANDLE, url=ADDON_PATH + '?channel=' + self.source_url, listitem=self.listitem, isFolder=self.folder, totalItems=len(items))
        elif(countries[country][1] == self.countryCode):
          self.listitem = xbmcgui.ListItem(label=self.name, thumbnailImage=(self.thumbnailImage))
          xbmcplugin.addDirectoryItem(ADDON_HANDLE, url=ADDON_PATH + '?channel=' + self.source_url, listitem=self.listitem, isFolder=self.folder, totalItems=len(items))
      xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_NONE)
      xbmcplugin.endOfDirectory(ADDON_HANDLE)
    else:
      for item in items.keys():
        self.title = unicode(items[item][0]).encode('utf-8')
        self.description = unicode(items[item][1]).encode('utf-8')
        self.m = re.search('(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', str(items[item][2]))
        self.startTime = datetime.datetime(int(self.m.group(1)), int(self.m.group(2)), int(self.m.group(3)),\
                                           int(self.m.group(4)), int(self.m.group(5)), int(self.m.group(6)))
        self.m = re.search('(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})', str(items[item][3]))
        self.endTime = datetime.datetime(int(self.m.group(1)), int(self.m.group(2)), int(self.m.group(3)),\
                                           int(self.m.group(4)), int(self.m.group(5)), int(self.m.group(6)))
        self.episode = items[item][4]
        self.genre = items[item][5]
        self.thumbnailImage = 'DefaultVideo.png'
        self.duration = self.endTime - self.startTime
        self.duration = self.duration.seconds / 60
        self.infoLabels = {'plot' : self.description,
                           'episode' : int(self.episode),
                           'season' : int(0),
                           'tvshowtitle' : self.title,
                           'genre' : self.genre,
                           'duration' : str(self.duration) + ':00',
                           'aired' : self.startTime.strftime('%H:%M') + ' - ' + self.endTime.strftime('%H:%M'),}
        if(self.startTime <= self.now <= self.endTime):
          self.listitem = xbmcgui.ListItem(label=self.startTime.strftime('%H:%M') + ' - ' + self.title, thumbnailImage=(self.thumbnailImage))
          self.listitem.setInfo(type='video', infoLabels=self.infoLabels)
          xbmcplugin.addDirectoryItem(ADDON_HANDLE, url=self.title, listitem=self.listitem, isFolder=self.folder, totalItems=len(items))
        elif(self.startTime > self.now):
          self.listitem = xbmcgui.ListItem(label=self.startTime.strftime('%H:%M') + ' - ' + self.title, thumbnailImage=(self.thumbnailImage))
          self.listitem.setInfo(type='video', infoLabels=self.infoLabels)
          xbmcplugin.addDirectoryItem(ADDON_HANDLE, url=self.title, listitem=self.listitem, isFolder=self.folder, totalItems=len(items))
      xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_NONE)
      xbmcplugin.endOfDirectory(ADDON_HANDLE)

  def getTvChannels(self):
    self.url = 'http://www.dr.dk/tjenester/programoversigt/dbservice.ashx/getChannels?type=tv'
    self.result = json.load(urllib.urlopen(self.url))['result']
    self.tvChannels = {}
    self.channelId = 0
    for channel in self.result:
      self.tvChannels[self.channelId] = [channel['dr_channel'], channel['name'], channel['channel_group'],\
                    urllib.pathname2url(channel['source_url']), channel['country_code'], channel['type']]
      self.channelId += 1
    return self.tvChannels

  def getSchedule(self, channel_source_url, broadcastDate):
    self.channel_source_url = channel_source_url
    self.broadcastDate = broadcastDate
    self.url = 'http://www.dr.dk/tjenester/programoversigt/dbservice.ashx/getSchedule?channel_source_url=' + self.channel_source_url + '&broadcastDate=' + self.broadcastDate
    self.result = json.load(urllib.urlopen(self.url))['result']
    self.scheduleList = {}
    self.scheduleId = 0
    for schedule in self.result:
      if('ppu_description' not in schedule):
        schedule['ppu_description'] = u'Ingen program beskrivelse'
      if('prd_episode_number' not in schedule):
        schedule['prd_episode_number'] = 0
      if('ppu_punchline' not in schedule):
        schedule['ppu_punchline'] = ''
      self.scheduleList[self.scheduleId] = [schedule['pro_title'], schedule['ppu_description'],\
                                            schedule['pg_start'], schedule['pg_stop'],\
                                            schedule['prd_episode_number'], schedule['ppu_punchline']]
      self.scheduleId += 1
    return self.scheduleList
    
  def getCurrentBroadcastDate(self):
    self.currentDate = datetime.datetime.today()
    self.yesterday = datetime.timedelta(days=1)
    if(self.currentDate.hour in range(6)):
      self.currentDate = self.currentDate - self.yesterday
    return self.currentDate.strftime('%Y-%m-%dT00:00:00')
    
MyGuide = DRTVGuide()
if(sys.argv[2].startswith('?country')):
  MyGuide.CreateDirectoryItem(folder=True, items=MyGuide.getTvChannels(), country=sys.argv[2][9:])
elif(sys.argv[2].startswith('?channel')):
  MyGuide.CreateDirectoryItem(folder=False, items=MyGuide.getSchedule(sys.argv[2][9:], MyGuide.getCurrentBroadcastDate()))
else:
  MyGuide.CreateDirectoryItem(folder=True, items=None)