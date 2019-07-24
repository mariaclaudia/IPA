"""
Python script for batch geocoding of addresses using Nomination API.

Maria Claudia Bodino
8th August 2018
"""

import pandas as pd
import requests
import logging
import time

logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

#------------------ CONFIGURATION -------------------------------
# Backoff time sets how many minutes to wait between pings
BACKOFF_TIME = 1
# Set your output file name here.
output_filename = 'places.csv'
# Set your input file here
input_filename = "toprocess.csv"
# Specify the column name in your input data that contains addresses here
address_column_name = "place"
# Return Full Google Results? If True, full JSON results from Google are included in output
RETURN_FULL_RESULTS = False



#------------------ DATA LOADING --------------------------------

# Read the data to a Pandas Dataframe
data = pd.read_csv(input_filename, encoding='utf8')

if address_column_name not in data.columns:
	raise ValueError("Missing Address column in input data")

# Form a list of addresses for geocoding:
# Make a big list of all of the addresses to be processed.
addresses = data[address_column_name].tolist()


#------------------	FUNCTION DEFINITIONS ------------------------

def get_nominatim_results(address):
	"""
	Get geocode results from Nominatin Maps Geocoding API.
	
	https://nominatim.openstreetmap.org/search/Speleovivarium%20Trieste?format=json&addressdetails=1
	https://nominatim.openstreetmap.org/search/135%20pilkington%20avenue,%20birmingham?format=json&addressdetails=1
	"""
	
	# Set up your Geocoding url
	geocode_url = " https://nominatim.openstreetmap.org/search/{}".format(address)
	geocode_url = geocode_url + "?format=json&addressdetails=1"
	# Ping google for the reuslts:
	results = requests.get(geocode_url)
	# Results will be in JSON format - convert to dict using requests functionality
	results = results.json()
	
	# if there's no results or an error, return empty results.
	if len(results) == 0:
		output = {
			"formatted_address" : "NaN",
			"lat": "NaN",
			"lon": "NaN",
			"name": "NaN",
			"osm_place_id": "NaN",
		}
	else:	
		answer = results[0]
		full_name = str.split(answer.get('display_name'),",")
		name =full_name[0]
		formatted_address =','.join(full_name[1:])
		output = {
			"formatted_address" : formatted_address,
			"lat": answer.get('lat'),
			"lon": answer.get('lon'),
			"name": name,
			"osm_place_id": answer.get('osm_id'),
		}
		
	# Append some other details:	
	output['input_string'] = place
	return output

# Read the data to a Pandas Dataframe
logger.debug("Read original csv")

data = pd.read_csv(input_filename, encoding='utf8')
# Make a big list of all of the addresses to be processed.
places = data[address_column_name].tolist()
# Form a list of places for geocoding:
#------------------ PROCESSING LOOP -----------------------------
# Create a list to hold results
results = []
# Go through each place in turn
for place in places:
	print (place)
	geocode_result = get_nominatim_results(place)
	results.append(geocode_result)
	time.sleep(BACKOFF_TIME) # sleep for 1 minute		   
	
# All done
logger.info("Finished geocoding all places")
# Write the full results to csv using the pandas library.
pd.DataFrame(results).to_csv(output_filename, encoding='utf8')
logger.info("Saved to final csv")