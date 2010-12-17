import time
import os
import sys
import unittest

sys.path.append("xbmcstubs")
sys.argv = [
    os.getcwd(), # path
    12345,      # handle
    ""         # params
]

from danishaddons import *

# contents of URL will change every second
URL = 'http://tommy.winther.nu/files/2010/12/now.php'

class TestDanishAddons(unittest.TestCase):

    def testSecondsToDuration(self):
        self.assertEquals('00:00:10', info.secondsToDuration(10))
        self.assertEquals('00:01:00', info.secondsToDuration(60))
        self.assertEquals('00:10:00', info.secondsToDuration(600))
        self.assertEquals('01:00:00', info.secondsToDuration(3600))
        self.assertEquals('03:25:45', info.secondsToDuration(12345))
        self.assertEquals('15:05:21', info.secondsToDuration(54321))

    def testDownloadUrl(self):
        first = web.downloadUrl(URL)
        time.sleep(1)
        second = web.downloadUrl(URL)

        self.assertNotEquals(first, second, msg = 'Content is not different, perhaps it is cached?')

    def testDownloadAndCacheUrl(self):
        first = web.downloadAndCacheUrl(URL, os.path.join(ADDON_DATA_PATH, 'unittestcache.tmp'), 1)
        time.sleep(1)
        second = web.downloadAndCacheUrl(URL, os.path.join(ADDON_DATA_PATH, 'unittestcache.tmp'), 1)

        self.assertEquals(first, second, msg = 'Content is different, perhaps it is not cached?')



if __name__ == '__main__':
    unittest.main()
