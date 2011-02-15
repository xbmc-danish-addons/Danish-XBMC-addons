#!/usr/bin/python
import os
import zipfile
import xml.etree.ElementTree

__author__ = 'tommy'

DIST_FOLDER = 'dist'

class Zipper:
    def __init__(self):
        if not os.path.exists(DIST_FOLDER):
            os.makedirs(DIST_FOLDER)
        addons = os.listdir('.')

        for addon in addons:
            addon_xml = os.path.join(addon, 'addon.xml')
            if not os.path.isdir(addon) or not os.path.exists(addon_xml):
                continue

            version = self._parse_version(addon_xml)
            filename = os.path.join(DIST_FOLDER, "%s-%s.zip" % (addon, version))

            self._zip_addon(addon, filename)

    def _parse_version(self, addon_xml):
        doc = xml.etree.ElementTree.parse(addon_xml)
        return doc.find('.').attrib['version']

    def _zip_addon(self, source, destination):
        print "Creating zip: %s" % destination
        zip = zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED)
        self._add_recursive(zip, source)
        zip.close()

    def _add_recursive(self, zip, folder):
        zip.write(folder)
        items = os.listdir(folder)
        for item in items:
            item = os.path.join(folder, item)


            if item[-4:] == '.pyc' or item[-6:] == 'target':
                continue

            if os.path.isdir(item):
                self._add_recursive(zip, item)
            else:
                zip.write(item)


    
if __name__ == '__main__':
    Zipper()
