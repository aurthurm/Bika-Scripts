# Deveoped by Aurthur Musendame

import requests
import json
import os
from time import ctime, strftime
from json2csv import json_to_csv
from pathlib import Path
import distutils.dir_util

def init( json_file_path, json_file):
	# the initialisation function creates 
	# 1. folders necessary for the api
	# 2. create empty initiatorjson files 

	if json_file_path.is_dir():
	    if not json_file.is_file():
	    	with open(json_file, "w") as f:
	    		f.write("[]")
	    	f.close()
	    	print('Created the file ' + str(json_file))
	else:
	    distutils.dir_util.mkpath(str(json_file_path))
	    print('Created the folder ' + str(json_file_path))
	    if not json_file.is_file():
	    	json_file = str(json_file)
	    	with open(json_file, "w") as f:
	    		f.write("[]")
	    	f.close()
	    	print('Created the file ' + json_file)


	csv_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\csv\\' )
	if not csv_file_path.is_dir():
	    distutils.dir_util.mkpath(str(csv_file_path))
	    print('Created the folder ' + str(csv_file_path))

	client_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\clients\\' )
	if not client_file_path.is_dir():
	    distutils.dir_util.mkpath(str(client_file_path))
	    print('Created the folder ' + str(client_file_path))


def pull_data(username, password, api_url, page_nr, iterations, json_file, file_name, review_state):
	# login to the Bika Lims API and pull data, save json file and convert it to csv using json2csv

	print('\nStart Time')
	start_time = ctime()
	print(start_time)

	while page_nr < iterations:

		api_url+=str(page_nr)

		api_data = requests.get(api_url, auth=(username, password ))

		api_data = json.loads(api_data.text)

		success_check(api_data)

		list_concat(api_data['objects'], json_file)

		file_count(page_nr)

	    # Remove previous concatenation before new concatenation : str(i)

		if page_nr < 10:                         
			api_url=api_url[:-1]
		elif page_nr >= 10 and page_nr < 100:
			api_url=api_url[:-2]
		else:                               # hightly unlikey that the case will get this option if page_size=200 / > per cycle :: leave it there just in case you are pulling gigantic data
			api_url=api_url[:-3] 

		# check if data pulling has finished and tell us about it
		if page_nr == (iterations - 1):  # last iteration = iterations - 1 :: you can change acording to how your code is structured e.g if i == 49: => produce same result for iteration = 50
			
			to_cvs(json_file, file_name, review_state)
			
			print('\n')
			print('=============================================')
			print('=====               FINISHED            =====')
			print('=============================================')

			print('Start Time')
			print(start_time)

			print('End Time')
			end_time = ctime()
			print(end_time)
			print('\n')

		page_nr+=1 # increamenting the loop

def success_check(api_data):
	# Check for Errors and progress and provide feed back
	print ('Successfull ? ' + str(api_data['success']))
	print ('Last Object number: ' + str(api_data['last_object_nr']))
	print ('Total Objects: ' + str(api_data['total_objects']))

def list_concat(input_data, json_file):
	# Merge or concatenate pulled json files into a single file
    with open(json_file) as data_file:    
        data = json.load(data_file)

    combined_list = data + input_data

    with open(json_file, 'w') as outfile:
        json.dump(combined_list, outfile, sort_keys = True, indent = 4, ensure_ascii = False,  separators=(',', ':'))  # lets make the json file sexy human readable

def file_count(page_nr):
	# get the number or json files that have been merged into a sigle file
	file_count = page_nr + 1

	print ('\nwritten ' + str(file_count) + ' files \nTime: ')

	time_saved = ctime()
	print (time_saved) 
	print('\n')


def to_cvs(json_file, file_name, review_state):
	# convert json file to csv file
	if review_state == "none":
		csv_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'csv')) + '\\' + file_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.csv'
	elif review_state == "none_client":
		csv_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'clients')) + '\\' + file_name + '.csv' 
	else:
		csv_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'csv')) + '\\' + file_name + '_' + review_state + ' - ' + strftime("%a %d %b %Y - %H%M") + '.csv'
		
	json_to_csv( json_file, csv_file)
	print('\n\nYour data has been successfully saved as\n' + csv_file)



