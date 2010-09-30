import time

def secondsToDuration(input):
	hours = input / 3600
	minutes = (input % 3600) / 60
	seconds = (input % 3600) % 60 

	return "%02d:%02d:%02d" % (hours, minutes, seconds)
