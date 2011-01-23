import os
import random

import xbmc
import xbmcgui

from player import TenSecondPlayer
from db import Database
import question

__author__ = 'twinther'

class QuizGui(xbmcgui.WindowXML):
    def __init__(self, xmlFilename, scriptPath):
        xbmcgui.WindowXML.__init__(self, xmlFilename, scriptPath)

    def onInit(self):
        print "onInit"

        self.correctAnswer = None
        self.database = Database()
        self.player = TenSecondPlayer()

        self.score = {'correct' : 0, 'wrong' : 0}
        self.thumbnails = [None, None, None, None]

        self._update_score()
        self._setup_question()


    def onAction(self, action):
        if action.getId() == 9 or action.getId() == 10:
            if self.player.isPlaying():
                self.player.stop()
            self.close()

        print action.getId()


    def onClick(self, controlId):
        print controlId

        if controlId >= 4000 or controlId <= 4003:
            if self.correctAnswer == (controlId - 4000):
                self.score['correct'] += 1
            else:
                self.score['wrong'] += 1
            self._update_score()

            if self.player.isPlaying():
                self.player.stop()
            self._setup_question()


    def onFocus(self, controlId):
        print controlId

        self._update_thumb()

    def _setup_question(self):
        #q = question.WhatYearWasMovieReleasedQuestion(self.database)
        q = question.getRandomQuestion()(self.database)
        self.getControl(4300).setLabel(q.getQuestion())
        self.answers = q.getAnswers()
        self.correctAnswer = self.answers.index(q.getCorrectAnswer())

        for idx, answer in enumerate(self.answers):
            control = self.getControl(4000 + idx)
            control.setLabel(answer['title'])

            if answer['videoFile'][0:8] == 'stack://':
                commaPos = answer['videoFile'].find(' , ')
                thumbFile = xbmc.getCacheThumbName(answer['videoFile'][8:commaPos].strip())
                print "thumbFile '%s'" % thumbFile
            else:
                thumbFile = xbmc.getCacheThumbName(answer['videoFile'])
            self.thumbnails[idx] = xbmc.translatePath('special://profile/Thumbnails/Video/%s/%s' % (thumbFile[0], thumbFile))

        self._update_thumb()

        self.getControl(4400).setVisible(False)
        if q.getVideoFile() is not None and os.path.exists(q.getVideoFile()):
            #self.player.playWindowed(q.getVideoFile())
            pass

        elif q.getPhotoFile() is not None:
            print "photo %s" % q.getPhotoFile()
            self.getControl(4400).setVisible(True)
            self.getControl(4400).setImage(q.getPhotoFile())


    def _update_score(self):
        self.getControl(4101).setLabel(str(self.score['correct']))
        self.getControl(4103).setLabel(str(self.score['wrong']))

    def _update_thumb(self):
        controlId = self.getFocusId()
        if controlId >= 4000 or controlId <= 4003:
            try:
                thumbFile = self.thumbnails[controlId - 4000]
                #if os.path.exists(thumbFile):
                #    self.getControl(4200).setImage(thumbFile)
            except AttributeError:
                pass
