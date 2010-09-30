import os
import time
import urllib2

def downloadAndCacheUrl(url, cacheFile, cacheMinutes):
	try:
		cachedOn = os.path.getmtime(cacheFile)
	except:
		cachedOn = 0

	if(time.time() - cacheMinutes * 60 >= cachedOn):
		# Cache expired or miss
		u = urllib2.urlopen(url)
		content = u.read()
		u.close()
	
		f = open(cacheFile, 'w')
		f.write(content)
		f.close()

	else:
		f = open(cacheFile)
		content = f.read()
		f.close()

	return content



