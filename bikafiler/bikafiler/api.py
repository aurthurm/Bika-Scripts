# -*- coding: utf-8 -*-
# Deveoped by Aurthur Musendame

import requests
import json
import os
import pandas as pd
from time import ctime, strftime
from json2csv import json_to_csv
from pathlib import Path
import distutils.dir_util
from progressbar.progressbar.bar import (Bar)

def create_dir(file_path):
	# Create a folder
	distutils.dir_util.mkpath(str(file_path))
	#print('Created the folder ' + str(file_path))	

def register_jsonfile(json_file):
	# Create an empty jason file
	if not json_file.is_file():
		with open(json_file, "w") as f:
			f.write("[]")
		f.close()
		#print('Created the file ' + str(json_file))	

def init( json_file_path, json_file):
	# the initialisation function creates 
	# 1. folders necessary for the api
	# 2. create empty initiatorjson files 

	if json_file_path.is_dir():
	    register_jsonfile(json_file)
	else:
	    create_dir(json_file_path)
	    register_jsonfile(json_file)

	csv_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\csv\\' )
	if not csv_file_path.is_dir():
	    create_dir(csv_file_path)

#	client_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\clients\\' )
#	if not client_file_path.is_dir():
#		create_dir(client_file_path)

def pull_data(username, password, api_url, page_nr, iterations, json_file, file_name, review_state,data, to_reduce):
	# login to the Bika Lims API and pull data, save json file and convert it to csv using json2csv

	start_time = ctime()

	print('\nWait while we process the data for you ....\n')
	bar = Bar('Processing', max=iterations)

	for i in range(int(iterations - 1)):
		api_url+=str(page_nr)
		api_data = requests.get(api_url, auth=(username, password ))
		api_data = json.loads(api_data.text)

		list_concat(api_data['objects'], json_file)

		if page_nr < 10:                         
			api_url=api_url[:-1]
		elif page_nr >= 10 and page_nr < 100:
			api_url=api_url[:-2]
		else:
			api_url=api_url[:-3] 

		if page_nr == (iterations - 1):			
			to_cvs(json_file, file_name, review_state, data, to_reduce, printing=False)

		page_nr+=1 # increamenting the loop
		bar.next()

	bar.finish()	
	print('\n=====   DONE!  =====\n')
	print('Start Time: {}.\nEnd Time: {}.\n'.format(start_time,ctime()))

def nothing():
	while page_nr < iterations:
		api_url+=str(page_nr)
		api_data = requests.get(api_url, auth=(username, password ))
		api_data = json.loads(api_data.text)
		success_check(api_data)
		list_concat(api_data['objects'], json_file)
	#	file_count(page_nr)

	    # Remove previous concatenation before new concatenation : str(i)
		if page_nr < 10:                         
			api_url=api_url[:-1]
		elif page_nr >= 10 and page_nr < 100:
			api_url=api_url[:-2]
		else:
			# hightly unlikey that the case will get this option if page_size=200 / > per cycle :: 
			# leave it there just in case you are pulling gigantic data
			api_url=api_url[:-3] 

		# check if data pulling has finished and tell us about it
		# last iteration = iterations - 1 :: you can change acording to how your 
		# code is structured e.g if i == 49: => produce same result for iteration = 50
		if page_nr == (iterations - 1):			
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

def csv_reducer(unfiltered, data):
    data = data.lower()
    if (data == "analyses") or (data == "analysis"):
        return unfiltered[
			[
				"PatientUID",
				"Patient_uid",
				"ClientPatientID",
				"Client",
				"SampleType",
				"getSampleID",
				"Analyses_0_Result",
				"Analyses_0_Unit",
				"Analyses_0_review_state",
				"DateSampled",
				"creation_date_y",
				"Creator_x",
				"DateReceived",
				"Analyses_0_ResultCaptureDate",
				"DatePublished",
			]
		]
    elif data == "patients":
        return unfiltered[
			[
				"PrimaryReferrerUID",
				"UID",
				"Firstname",
				"Surname",
				"Gender",
				"BirthDate",
				"ConsentSMS",
				"ClientPatientID",
			]
		]

def to_cvs(json_file, file_name, review_state, data, to_reduce="no", printing=False):
	# convert json file to csv file
	if review_state == "none":
		csv_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'csv')) + '\\' + file_name + '.csv'
	elif review_state == "none_client":
		csv_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'clients')) + '\\' + file_name + '.csv' 
	else:
		csv_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'csv')) + '\\' + file_name + '_' + review_state + '.csv'
		
	json_to_csv( json_file, csv_file)

	# Take the Just saved csv file and filter to reduce filesize
	if to_reduce == "reduce":		
		reduced_csv = csv_reducer(pd.read_csv(csv_file), data)
		if os.path.exists(csv_file):
			os.remove(csv_file)
		reduced_csv.to_csv(csv_file,index=False)

	if printing:
		print('\n\nYour data has been successfully saved as\n' + csv_file)



