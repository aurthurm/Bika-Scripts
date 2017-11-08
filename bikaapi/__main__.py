from pathlib import Path
from time import strftime
import os
import distutils.dir_util
import api 
import merger
from tkinter import *
from tkinter import filedialog
import pandas as pd
from json2csv import json_to_csv
import getpass



def main(username, password, api_url, page_nr, iterations, json_file, file_name, review_state):
	api.pull_data(username, password, api_url, page_nr, iterations, json_file, file_name, review_state)


if __name__ == "__main__":
	
	print('\n')
	print('What do you want to do? \n')
	print('[1] : Pull New Data from API \n[2] : Merge Patients and Analysis Data  \n[3] : Convert JSON to CSV\n[4] : Update Clients [Provinces/Districts]\n')
	do_choice = int(input('Choose either 1 or 2 or 3:'))

	if do_choice == 1:

		print('\n')
		print('Which data type do you want to pull? \n')
		print('[1] : Analysis Results \n[2] : Patients \n[3] : Both  \n')
		print('\n')
		user_choice = int(input('Choose either 1 or 2 or 3 :'))
		print('\n')

		if user_choice == 1:

			file_name = input('Enter File save name {e.g analysis or results } :')
			review_state = input('Enter page review state {e.g published } :')
			json_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\json\\' )
			json_file = Path( str(json_file_path) + '\\' + file_name + '_' + review_state + ' - ' + strftime("%a %d %b %Y - %H%M") + '.json' )

			api.init( json_file_path, json_file)

			username = str(input('Enter your Username:'))
			password = getpass.getpass('Enter Your Password:')
			your_api = input('Enter your API {e.g 19.0.9.8 } :')
			page_size = input('Enter page size {e.g 5000 } :')
			iterations = int(input('Enter number of cycles or iterations {e.g 5000 }:'))
			api_url = "http://" + str(your_api) + "/@@API/read?catalog_name=bika_catalog_analysisrequest_listing&review_state=" + str(review_state) + "&sort_order=descending&page_size=" + str(page_size) + "&page_nr="
			page_nr = 0      

			main(username, password, api_url, page_nr, iterations, json_file, file_name, review_state)

		elif user_choice == 2:

			file_name = input('Enter File save name {e.g patients } :')
			review_state = "none"
			json_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\json\\' )
			json_file = Path( str(json_file_path) + '\\' + file_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.json' )

			api.init( json_file_path, json_file)

			username = str(input('Enter your Username:'))
			password = getpass.getpass('Enter Your Password:')
			your_api = input('Enter your API {e.g 19.0.9.8 } :')
			page_size = input('Enter page size {e.g 5000 }:')
			iterations = int(input('Enter number of cycles or iterations {e.g 2 }:'))
			api_url =  "http://" + str(your_api) + "/@@API/read?catalog_name=bikahealth_catalog_patient_listing&sort_order=descending&page_size=" + str(page_size) + "&page_nr="
			page_nr = 0      

			main(username, password, api_url, page_nr, iterations, json_file, file_name, review_state)

		else:	

			patients_file_name = input('Enter Patients File save name {e.g Patients } :')		
			analysis_file_name = input('Enter Analysis File save name {e.g Analysis } :')

			patients_review_state = "none"
			analysis_review_state = input('Enter Analysis review state {e.g published } :')

			json_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\json\\' )

			patient_json_file = Path( str(json_file_path) + '\\' + patients_file_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.json' )
			analysis_json_file = Path( str(json_file_path) + '\\' + analysis_file_name + '_' + analysis_review_state + ' - ' + strftime("%a %d %b %Y - %H%M") + '.json' )

			api.init( json_file_path, patient_json_file)
			api.init( json_file_path, analysis_json_file)

			username = str(input('Enter your Username:'))
			password = getpass.getpass('Enter Your Password:')
			your_api = input('Enter your API {e.g 19.0.9.8 } :')

			patients_page_size = input('Enter Patients page size {e.g 5000 }:')
			patients_iterations = int(input('Enter number of Patient cycles or iterations {e.g 2 }:'))

			analysis_page_size = input('Enter Analysis page size {e.g 5000 }:')
			analysis_iterations = int(input('Enter number of Analysis cycles or iterations {e.g 2 }:'))

			analysis_url = "http://" + str(your_api) + "/@@API/read?catalog_name=bika_catalog_analysisrequest_listing&review_state=" + str(analysis_review_state) + "&sort_order=descending&page_size=" + str(analysis_page_size) + "&page_nr="
			patient_url =  "http://" + str(your_api) + "/@@API/read?catalog_name=bikahealth_catalog_patient_listing&sort_order=descending&page_size=" + str(patients_page_size) + "&page_nr="
			page_nr = 0   

			main(username, password, patient_url, page_nr, patients_iterations, patient_json_file, patients_file_name, patients_review_state)
			main(username, password, analysis_url, page_nr, analysis_iterations, analysis_json_file, analysis_file_name, analysis_review_state)
			
	elif do_choice == 2:

		merged_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\merged\\' )
		if not merged_path.is_dir():
		    os.makedirs(merged_path)

		root = Tk()
		root.withdraw()

		merged_save_name = str(input('Enter File Name for Saving the Merged Data:'))
		patients_file =  filedialog.askopenfilename(
		    initialdir = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\csv\\' ),
		    title = "Select Patients csv File",
		    filetypes = (
		        ("csv files","*.csv"),
		        ("all files","*.*")
		    )
		)

		analysis_file =  filedialog.askopenfilename(
		    initialdir = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\csv\\' ),
		    title = "Select Analysis csv File",
		    filetypes = (
		        ("csv files","*.csv"),
		        ("all files","*.*")
		    )
		)

		patients = pd.read_csv(patients_file, low_memory=False)

		analysis= pd.read_csv(analysis_file, low_memory=False)

		merger.merger_init(patients, analysis, merged_save_name)

	elif do_choice == 3:	
		# Consider a mutifile selecting dialog and for loop
		root = Tk()
		root.withdraw()

		file_name = input('Enter File Save name :')
		selected_json_file =  filedialog.askopenfilename(
		    initialdir = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\json\\' ),
		    title = "Select the JSON File",
		    filetypes = (
		        ("json files","*.json"),
		        ("text files","*.txt"),
		        ("all files","*.*")
		    )
		)

		csv_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'csv')) + '\\' + file_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.csv'
		
		print('\nConverting ... ... .... ...')
		json_to_csv( selected_json_file, csv_file)
		print('\nYour csv file has been successfully saved in\n' + csv_file)

	else:
		# Pull and Update Clients if need arise. This will update new provinces and Distric if any
		file_name = 'Clients'
		review_state = "none_client"
		json_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\json\\' )
		json_file = Path( str(json_file_path) + '\\' + file_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.json' )

		api.init( json_file_path, json_file)

		username = str(input('Enter your Username:'))
		password = getpass.getpass('Enter Your Password:')
		your_api = input('Enter your API {e.g 19.0.9.8 } :')
		page_size = '500'
		iterations = int('4')
		api_url =  "http://" + str(your_api) + "/@@API/read?portal_type=Client&page_size=" + str(page_size) + "&page_nr="
		page_nr = 0      

		main(username, password, api_url, page_nr, iterations, json_file, file_name, review_state)

		clients_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'clients')) + '\\' + file_name + '.csv'
		clients_raw = pd.read_csv(clients_file)
		cleints_filtred = merger.Clients_filter(clients_raw)
		clients_final = merger.clients_renamer(cleints_filtred)
		clients_final.drop_duplicates(subset=['Client UID'] , keep='first', inplace=True)
		clients_final.to_csv(clients_file, sep=',', encoding='utf-8',header=True, index=False)
