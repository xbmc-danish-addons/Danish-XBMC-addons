import os
import sys
import unittest

sys.path.append("../script.module.danishaddons/")
sys.path.append("../script.module.danishaddons/xbmcstubs/")

import xbmc
import xbmcplugin
import danishaddons

import sources.tv2midtvest

class TestTV2MidtVest(unittest.TestCase):

    def setUp(self):
        danishaddons.init([os.getcwd(), '12345', ''])
        xbmcplugin.items = list()

    def testShowPrograms(self):
        sources.tv2midtvest.showClips()


if __name__ == '__main__':
    unittest.main()
