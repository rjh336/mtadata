import os
import gtfs_realtime_pb2 as gtfs
import nyct_subway
import pandas as pd

# 'feed_list' will hold all FeedMessages from ./gtfs
# I downloaded one day's worth of MTA RT data to ./gtfs from:
# http://data.mytransit.nyc/subway_time/2016/2016-09/ 
feed_list = []

# unpack protobufs into FeedMessages
for fn in os.listdir('./gtfs'):
	path = os.path.join('./gtfs',fn)
	if os.path.isfile(path):
	    f = open(path, 'r')
	    feed = gtfs.FeedMessage()
	    feed.ParseFromString(f.read())
	    feed_list.append(feed)

# will hold a bunch of dataframes
df_list = []

for feed in feed_list:
	# 'rowlist' will hold a bunch of dicts representing rows in a given dataframe
	# A row will represent an arrival at a given stop for a given train
	rowlist = []
	for i, val in enumerate(feed.entity):
		row = {}
		if feed.entity[i].HasField('trip_update'):
			trip_update = feed.entity[i].trip_update
			if trip_update.trip.HasField('route_id'):
				row['train_id'] = trip_update.trip.route_id
			if trip_update.trip.Extensions[nyct_subway.nyct_trip_descriptor].HasField('direction'):	
				row['direction'] = trip_update.trip.Extensions[nyct_subway.nyct_trip_descriptor].direction
			if trip_update.trip.Extensions[nyct_subway.nyct_trip_descriptor].HasField('train_id'):	
				row['trip_type'] = trip_update.trip.Extensions[nyct_subway.nyct_trip_descriptor].train_id[0]
			for stop_time in trip_update.stop_time_update:
				row['stop_id'] = stop_time.stop_id
				row['arrival_time'] = stop_time.arrival.time 
				row['depart_time'] = stop_time.departure.time
				rowlist.append(row)
	# for a given FeedMessage, store all rows in a dataframe
	data = pd.DataFrame(rowlist)
	# add the resulting dataframe to our list
	df_list.append(data)
# concatenate entire df_list into one big dataframe
subway_data = pd.concat(df_list)