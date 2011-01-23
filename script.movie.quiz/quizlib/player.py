import random

__author__ = 'tommy'

import xbmc

class TenSecondPlayer(xbmc.Player):
    def __init__(self):
        xbmc.Player.__init__(self)

    def playWindowed(self, file):
        print "!!!!!!!!!!!!! PlayWindowed"
        self.play(item = file, windowed = True)

        retries = 0
        while not self.isPlaying() and retries < 8:
            xbmc.sleep(250)
            retries += 1
            print "retries %d" % retries

        totalTime = self.getTotalTime()
        # find start time, ignore first and last 10% of movie
        startTime = random.randint(int(totalTime * 0.1), int(totalTime * 0.9))
        endTime = startTime + 10

        
        print "Playback playback from: %d to %d" % (startTime, endTime)
        self.seekTime(startTime)

        while self.isPlaying() and self.getTime() < endTime:
            xbmc.sleep(1000)

        if self.isPlaying():
            self.stop()

        retries = 0
        while self.isPlaying() and retires < 8:
            xbmc.sleep(250)
            retries += 1
            print "retries %d" % retries

        print "playWindowed end"

    def onPlayBackStarted(self):
        print "!!!!!!!!!!!!PlayBack Started"

    def onPlayBackEnded(self):
        print "!!!!!!!!!!!!PlayBack Ended"

    def onPlayBackStopped(self):
        print "!!!!!!!!!!!!PlayBack Stopped"

    def onPlayBackPaused(self):
        print "!!!!!!!!!!!!PlayBack Paused"

    def onPlayBackResumed(self):
        print "!!!!!!!!!!!!PlayBack Resumed"

