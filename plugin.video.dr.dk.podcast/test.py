import os
import re
import sys
import unittest

sys.path.append("../script.module.danishaddons/")
sys.path.append("../script.module.danishaddons/xbmcstubs/")
sys.path.append("../script.module.feedparser/")

import xbmcplugin
import danishaddons
import addon

class TestDrDkPodcast(unittest.TestCase):

    def setUp(self):
        danishaddons.init([os.getcwd(), '12345', ''])
        xbmcplugin.items = list()

    def testShowOverview(self):
        addon.showOverview()

        self.assertNotEquals(0, len(xbmcplugin.items), msg = 'Expected at least one ListItem')
        self.assertNotEquals(-1, xbmcplugin.items[0].url.find('key=21_soendagrss'))

    def testShowFeed(self):
        addon.showFeed('21_soendagrss')

        self.assertNotEquals(0, len(xbmcplugin.items), msg = 'Expected at least one ListItem')
        self.assertTrue(re.match('http://vpodcast.dr.dk/.*\.mp4', xbmcplugin.items[0].url),
                        msg = "Clip URL didn't match expected format")


if __name__ == '__main__':
    unittest.main()
    