import sys
import unittest

sys.path.append("../script.module.danishaddons/")
sys.path.append("../script.module.danishaddons/xbmcstubs/")

import xbmc
import xbmcplugin
import danishaddons
import addon

class TestDrDkPiratTv(unittest.TestCase):

    def setUp(self):
        danishaddons.init(['.', '12345', ''])
        xbmcplugin.items = list()

    def testShowPrograms(self):
        addon.showPrograms()
        self.assertNotEquals(0, len(xbmcplugin.items), msg = 'Expected at least one ListItem')

    def testShowClips(self):
        addon.showClips('pirat-tv-paa-dr2')
        self.assertNotEquals(0, len(xbmcplugin.items), msg = 'Expected at least one ListItem')


if __name__ == '__main__':
    unittest.main()
