"""This module illustrates how to query GooglePlaces API from a list of text info in input and save the result in a .csv file"""
__autor__ = "Maria Claudia Bodino"


import pandas as pd
import requests
import logging
import time
import sys
import argparse
import os

#LOGGER
logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)
# create console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def get_google_results(place, api_key):
	"""
	Return Places results from Google places API.
	
	@param key: String API key 
	@param inputtype: textquery
	@param fields: formatted_address,geometry/location,name,id,place_id
	@param language: it
	"""
	# Set up your Geocoding url
	geocode_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input={}".format(place)
	
	geocode_url = geocode_url + "&inputtype=textquery"
	geocode_url = geocode_url + "&fields=formatted_address,geometry/location,name,id,place_id"
	geocode_url = geocode_url + "&language=it"
	geocode_url = geocode_url + "&key={}".format(api_key)
	
	# Ping google for the reuslts:
	results = requests.get(geocode_url)
	
	results = results.json()
	if len(results['candidates']) == 0:
		logger.debug("No Google places info for ", )
		output = {
			"formatted_address" : "NaN",
			"lat": "NaN",
			"lon": "NaN",
			"name": "NaN",
			"google_place_id": "NaN",
			}
	else: 
		answer = results['candidates'][0]
		output = {
			"formatted_address" : answer.get('formatted_address'),
			"lat": answer.get('geometry').get('location').get('lat'),
			"lon": answer.get('geometry').get('location').get('lng'),
			"name": answer.get('name'),
			"google_place_id": answer.get("place_id"),
			}
		
	# Append some other details:    
	output['input_string'] = place
	return output

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
			description='Get google places')
	parser.add_argument('--inputfile',
			help='the file that contains a newline separated names of companies',
			type=str,
			required=True)
	parser.add_argument('--outputfile',
			help='the folder where to save the output',
			type=str,
			required=True)
	parser.add_argument('--outputpath',
            help='the folder where to save the output',
            required=True)
	parser.add_argument('--inputpath',
            help='the folder where to read the input',
            required=True)
	parser.add_argument('--column',
            help='the column name to read the text input',
            required=True)
	parser.add_argument('--api_key',
			help='the API key',
			type=str,
			required=True)
	args = parser.parse_args()

	# Assign args to variables
	input_file = os.path.join(args.inputpath, args.inputfile)
	output_file = os.path.join(args.outputpath, args.outputfile)
   
    # Read the data
	logger.debug("Read original csv")
	data = pd.read_csv(input_file, encoding='utf8')
	# Make a big list of all of the addresses to be processed.
	places = data[args.column].tolist()

	# Create a list to hold results
	results = []
	
	# Go through each place in turn
	for place in places:
		print (place)
		geocode_result = get_google_results(place, args.api_key)
		results.append(geocode_result)         
	
	# All done
	logger.info("Finished geocoding all places")
	# Save results to output_file
	pd.DataFrame(results).to_csv(output_file, encoding='utf8')
	logger.info("Saved to final csv")