import os
import gtfs_realtime_pb2 as gtfs
import nyct_subway
import pandas as pd

# return list of all FeedMessages from protobufs in PATH_NAME
def grab_feeds(path_name):
	feed_list = []
	feednum = 0
	# unpack protobufs into FeedMessages
	for fn in os.listdir(path_name):
		path = os.path.join(path_name, fn)
		if os.path.isfile(path):
		    f = open(path, 'r')
		    feed = gtfs.FeedMessage()
		    feed.ParseFromString(f.read())
		    feed_list.append(feed)
		    print('GRABBING FROM FILE: '+path+', IN FEED NUMBER: '+str(feednum))
		    feednum +=1
	return feed_list


def feeds_to_rows(feed_list):
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
				if trip_update.trip.HasField('trip_id'):
					row['trip_id'] = trip_update.trip.trip_id
				if trip_update.trip.HasField('start_date'):
					row['start_date'] = trip_update.trip.start_date
				if trip_update.trip.HasField('route_id'):
					row['route_id'] = trip_update.trip.route_id
				if trip_update.trip.Extensions[nyct_subway.nyct_trip_descriptor].HasField('direction'):	
					row['nyct_direction'] = trip_update.trip.Extensions[nyct_subway.nyct_trip_descriptor].direction
				if trip_update.trip.Extensions[nyct_subway.nyct_trip_descriptor].HasField('train_id'):	
					row['nyct_train_id'] = trip_update.trip.Extensions[nyct_subway.nyct_trip_descriptor].train_id
				if trip_update.trip.Extensions[nyct_subway.nyct_trip_descriptor].HasField('is_assigned'):	
					row['nyct_is_assigned'] = trip_update.trip.Extensions[nyct_subway.nyct_trip_descriptor].is_assigned
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
	dframe = pd.concat(df_list)
	return dframe

####################################################

PATH_NAME = './downloads'
feed_list = grab_feeds(PATH_NAME)
subway_df = feeds_to_rows(feed_list)

####################################################
