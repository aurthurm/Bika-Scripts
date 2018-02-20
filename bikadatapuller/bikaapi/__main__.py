from pathlib import Path
from time import strftime
import os, requests, json
import distutils.dir_util
from . import api, merger, config
from tkinter import *
from tkinter import filedialog
import pandas as pd
from .json2csv import json_to_csv
import getpass

def main():
	#Clear screen
	#clear = lambda: os.system('cls')
	def clear():
	    os.system('cls' if os.name=='nt' else 'clear')

	def page_number():
		print('\nRequired is a page number to sart pulling your data from\nBy default the counting of pages start from zero')
		try:
			initial_number = int(input('Provide Start Page Number and Press the Return Key [Enter] >>'))
		except ValueError: # SynatxError is left empty
			initial_number = None
		
		if initial_number == None:
			print('Since you did not set an initial page number, counting of pages will start from zero')
			initial_number = 0

		return initial_number

	def page_sizer(message):
		try:
			_size = input(message)
		except ValueError: # SynatxError is left empty
			_size = None
		
		if _size == None:
			print('Since you did not set an initial page number, counting of pages will start from zero')
			_size = 0

		return _size

	def iterationz(message):
		try:
			_iterations = int(input(message))
		except ValueError: # SynatxError is left empty
			_iterations = None
		
		if _iterations == None:
			print('Since you did not set an initial page number, counting of pages will start from zero')
			_iterations = 0

		return _iterations

	def begin(username, password, api_url, page_nr, iterations, json_file, file_name, review_state):
		# intiate data pulling
		api.pull_data(username, password, api_url, page_nr, iterations, json_file, file_name, review_state)

	def user_info():
		# Get user logon information and api
		print("\nPlease provide your Bika Credentials\n")
		while True:
			username = input('Enter your Username:')
			if not username:
				print('\nUsername cannot e empty!!')
				continue
			else:
				break	
		password = getpass.getpass('Enter Your Password:')
		return (username, password)

	def tk_init():
		# Initialise Tkinter
		root = Tk()
		root.withdraw()

	def get_clients(username, password):
		# Pull and Update Clients if need arise. This will update new provinces and Distric if any
		file_name = 'Clients'
		review_state = "none_client"
		json_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\json\\' )
		json_file = Path( str(json_file_path) + '\\' + file_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.json' )

		api.init( json_file_path, json_file)

		#for update: idealy make a small data pull and get last object number for cliets to determine the required number of api requests
		page_size = '500'
		iterations = int('5')
		api_url =  "http://" + str(your_api) + "/@@API/read?portal_type=Client&page_size=" + str(page_size) + "&page_nr="
		page_nr = 0      

		begin(username, password, api_url, page_nr, iterations, json_file, file_name, review_state)

		clients_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'clients')) + '\\' + file_name + '.csv'
		clients_raw = pd.read_csv(clients_file)
		clients_filtred = merger.Clients_filter(clients_raw)
		clients_final = merger.clients_renamer(clients_filtred)
		clients_final.drop_duplicates(subset=['Client UID'] , keep='first', inplace=True)
		clients_final.to_csv(clients_file, sep=',', encoding='utf-8',header=True, index=False)

	def client_data_check():
		# Check if client file is availabe
		# if available continue else create one
		client_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\clients\\' )
		client_file = Path( str(client_file_path) + '\\' + 'Clients.csv' )

		if client_file_path.is_dir():
			if not client_file.is_file():
				print("It seems you have not created a clients data File yet!\nSit tight as we make it avilable for you\nMerging will commence afer this process\nIt should take less that 2 minutes in normal circumstances")			
				get_clients(username, password)
			else:
				print("Client File exits\nProceeding with merging\n")
				pass
		else:
			# if not client_file.is_file():
			print("It seems you have not created a clients data File yet!\nSit tight as we make it avilable for you\nMerging will commence afer this process\nIt should take less that 2 minutes in normal circumstances")
			api.create_dir(client_file_path)
			get_clients(username, password)

	def analysis_categories(username, password):
		clear()
		print('From the data categories listed below, what category do you want? \n')
		print('[1] : Analysis Results \n[2] : Patients \n[3] : Both  \n[4] : Return to main Menu\n')
		while True:
			try:
				user_choice = int(input('Make your choice (1/2/3) and Press the Return Key [Enter] >>'))
			except ValueError:
				user_choice = None

			if (user_choice == None) or (user_choice == 0) or (user_choice > 4):
				print('Please Enter a valid option!')
				continue
			else:
				break

		if user_choice == 1:
			# user_choice = Analysis Results				

			while True:
				file_name = input('Give a Name to the File for saving {e.g Analysis} >>')
				if not file_name:
					print('\nThis Field is required. Please provide a filename')
					continue
				else:
					break	

			clear()
			print("Data can be in any of the following firts 3 Review States\n")
			print("[1] : Published\n[2] : Verified\n[3] : To be Verified\n[4] : Return to previous Menu (Categories)\n[5] : Return to main Menu\n")				
			
			while True:
				try:
					data_type = int(input('Make your choice (1/2/3) and Press the Return Key [Enter] >>'))
				except ValueError:
					data_type = None;

				if (data_type == None) or (data_type == 0) or (data_type > 5):
					print('Please Enter a valid option!')
					continue
				else:
					break	

			if data_type == 1:
				review_state = "published"
			elif data_type == 2:
				review_state = "verified"
			elif data_type == 3:
				review_state = "to_be_verified"
			elif data_type == 4:
				analysis_categories(username, password)
			else:
				user_options(username, password)

			json_file = Path( str(json_file_path) + '\\' + file_name + '_' + review_state + ' - ' + strftime("%a %d %b %Y - %H%M") + '.json' )

			api.init( json_file_path, json_file)

			#user_info()
			page_size = page_sizer('Enter page size {e.g 5000 } :')
			iterations = iterationz('Enter number of cycles or iterations {e.g 5000 }:')
			api_url = "http://" + str(your_api) + "/@@API/read?catalog_name=bika_catalog_analysisrequest_listing&review_state=" + str(review_state) + "&sort_order=descending&page_size=" + str(page_size) + "&page_nr="

			page_nr = page_number()   

			begin(username, password, api_url, page_nr, iterations, json_file, file_name, review_state)
			
			# Return user back to options before exit
			user_options(username, password)

		elif user_choice == 2:
			# user_choice = Patients
			while True:
				file_name = input('Enter File save name {e.g Patients } :')	
				if not file_name:
					print('\nThis Field is required. Please provide a filename')
					continue
				else:
					break	

			# If user mistakenly takes an wrong option let thenm return
			if file_name == 'return':
				user_options(username, password)

			review_state = "none"

			json_file = Path( str(json_file_path) + '\\' + file_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.json' )

			api.init( json_file_path, json_file)

			#user_info()
			page_size = page_sizer('Enter page size {e.g 5000 }:')
			iterations = iterationz('Enter number of cycles or iterations {e.g 2 }:')
			api_url =  "http://" + str(your_api) + "/@@API/read?catalog_name=bikahealth_catalog_patient_listing&sort_order=descending&page_size=" + str(page_size) + "&page_nr="
			
			page_nr = page_number()

			begin(username, password, api_url, page_nr, iterations, json_file, file_name, review_state)
			
			# Return user back to options before exit
			user_options(username, password)

		elif user_choice == 3:					
			# user_choice = Both
			print('\nPatient Data Information')
			while True:
				patients_file_name = input('Enter Patients File save name {e.g Patients } :')
				if not patients_file_name:
					print('\nThis Field is required. Please provide the patient filename')
					continue
				else:
					break	

			patient_json_file = Path( str(json_file_path) + '\\' + patients_file_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.json' )
			patients_page_size = page_sizer('Enter Patients page size {e.g 5000 }:')
			patients_iterations = iterationz('Enter number of Patient cycles or iterations {e.g 2 }:')
			patient_url =  "http://" + str(your_api) + "/@@API/read?catalog_name=bikahealth_catalog_patient_listing&sort_order=descending&page_size=" + str(patients_page_size) + "&page_nr="

			print('\nAnalysis Data Information')
			while True:
				analysis_file_name = input('Enter Analysis File save name {e.g Analysis } :')
				if not analysis_file_name:
					print('\nThis Field is required. Please provide the analysis filename')
					continue
				else:
					break	

			patients_review_state = "none"

			print("Data can be in any of the following firts 3 Review States\n")
			print("[1] : Published\n[2] : Verified\n[3] : To be Verified\n[4] : Return to previous Menu (Categories)\n[5] : Return to main Menu\n")
			
			while True:
				try:
					data_type = int(input('Make your choice (1/2/3) and Press the Return Key [Enter] >>'))
				except ValueError:
					data_type = None;

				if (data_type == None) or (data_type == 0) or (data_type > 5):
					print('Please Enter a valid option!')
					continue
				else:
					break	

			if data_type == 1:
				review_state = "published"
			elif data_type == 2:
				review_state = "verified"
			elif data_type == 3:
				review_state = "to_be_verified"
			elif data_type == 4:
				analysis_categories(username, password)
			else:
				user_options(username, password)

			analysis_review_state = review_state
			analysis_json_file = Path( str(json_file_path) + '\\' + analysis_file_name + '_' + analysis_review_state + ' - ' + strftime("%a %d %b %Y - %H%M") + '.json' )
			analysis_page_size = page_sizer('Enter Analysis page size {e.g 5000 }:')
			analysis_iterations = iterationz('Enter number of Analysis cycles or iterations {e.g 2 }:')

			api.init( json_file_path, patient_json_file)
			api.init( json_file_path, analysis_json_file)

			analysis_url = "http://" + str(your_api) + "/@@API/read?catalog_name=bika_catalog_analysisrequest_listing&review_state=" + str(analysis_review_state) + "&sort_order=descending&page_size=" + str(analysis_page_size) + "&page_nr="

			# Assumption is that if user is pulling both patients and analysis, then all have to gegin from page number 0 else get individual data pulls with specific page numbers to begin from
			page_nr = 0   

			print('\nPatient Data Processing')
			begin(username, password, patient_url, page_nr, patients_iterations, patient_json_file, patients_file_name, patients_review_state)
			print('\nAnalysis Data Processing')
			begin(username, password, analysis_url, page_nr, analysis_iterations, analysis_json_file, analysis_file_name, analysis_review_state)
			#break

			# Return user back to options before exit
			user_options(username, password)

		elif user_choice == 4:
			clear()
			# Return user back to options before exit
			user_options(username, password)

	def user_options(username, password):
		# Ask user some questions on what they want to do and initiate the api
		print('\n')
		print('What do you want to do? Provided below is a list of alternatives to get you started! :)\n')
		print('[1] : Pull New Data from API \n[2] : Merge Patients and Analysis Data  \n[3] : Convert JSON File types to CSV Files\n[4] : Update Clients [Provinces/Districts]\n[5] : Quit\n')

		while True:
			try:
				do_choice = int(input('Make your choice (1/2/3/4/5) and Press the Return Key [Enter] >>'))
			except ValueError:
				data_type = None;

			if (do_choice == None) or (do_choice == 0) or (do_choice > 5):
				print('Please Enter a valid option!')
				continue
			else:
				break	

		if do_choice == 1:
			# Get new datasets from the API
			clear()
			analysis_categories(username, password)

		elif do_choice == 2:
			clear()
			# Merge Patiets and Analyses Data Files
			client_data_check()

			if not merged_file_path.is_dir():
			    os.makedirs(merged_file_path)

			tk_init()

			while True:
				merged_save_name = input('Provide a Name for Saving Merged Data:')
				if not merged_save_name:
					print('\nThis Field is required. Please provide the analysis filename')
					continue
				else:
					break	

			patients_file =  filedialog.askopenfilename(
			    initialdir = csv_file_path,
			    title = "Select Patients csv File",
			    filetypes = (
			        ("csv files","*.csv"),
			        ("all files","*.*")
			    )
			)

			analysis_file =  filedialog.askopenfilename(
			    initialdir = csv_file_path,
			    title = "Select Analysis csv File",
			    filetypes = (
			        ("csv files","*.csv"),
			        ("all files","*.*")
			    )
			)

			patients = pd.read_csv(patients_file, low_memory=False)
			analysis = pd.read_csv(analysis_file, low_memory=False)
			merger.merger_init(patients, analysis, merged_save_name)
			#break
			# Return user back to options before exit
			user_options(username, password)

		elif do_choice == 3:
			# Convert Json to CSV file
			# Consider a mutifile selection
			clear()
			print('JSON to CSV Converter\n')
			tk_init()

			while True:
				file_name = input('Enter File Save name:')
				if not file_name:
					print('\nThis Field is required. Please provide a filename')
					continue
				else:
					break	

			selected_json_file =  filedialog.askopenfilename(
			    initialdir = json_file_path,
			    title = "Select the JSON File",
			    filetypes = (
			        ("json files","*.json"),
			        ("text files","*.txt"),
			        ("all files","*.*")
			    )
			)

			csv_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'csv')) + '\\' + file_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.csv'
			print('\n... ... Converting')
			json_to_csv( selected_json_file, csv_file)
			print('\nYour csv file has been successfully saved in\n' + csv_file)
			#break
			# Return user back to options before exit
			user_options(username, password)

		elif do_choice == 4:
			clear()
			print('Cliets File Updater\n')
			# Update Clients
			api.create_dir(Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\clients\\' ))
			get_clients(username, password)
			# Return user back to options before exit
			user_options(username, password)

		elif do_choice == 5:
			print('Hope you had an amazing experience, we hope to see you again.\nLet us know is there is anything you wish it could de added in this script\nwe are proud to enhance your experience and see you smile :) Aurthur')
			clear()
			exit()

	# Paths to file type locations
	json_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\json\\' )
	merged_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\merged\\' )
	csv_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\csv\\')

	# Lets start	
	# initial configurations if not already set and register apu_url
	config.config_data_check()

	with open(Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\.Configs\\config.json' )) as data:
		contents = json.load(data)
	data.close()	
	your_api = contents["data"][0]["API"]	

	clear()
	while True:

		# Check login detais. if correct continur else ask user to input again
		username, password = user_info()
		print("\nWait while we check if your logon details are correct ...\n")
		login_url = "http://" + str(your_api) + "/@@API/read?portal_type=Client&page_size=5"

		try:
		    response = requests.get(login_url, auth=(username, password))
		except requests.exceptions.RequestException as e:
			# API provided is incorrect
		    #print(e)
		    print("Your API : {} is not correct: TRY AGAIN (:".format(your_api))
		    continue
		else:
		    response_data = json.loads(response.text)
		    if response_data['total_objects'] == 0:
		    	# Either password or username is incorrect since for a wworking database there should be at least something :)) I hope.
		    	# Not the best way of checking logon success but it suffices the purpose
		    	print("Either your username or password is incorrect: TRY AGAIN !!!!! (:")
		    	continue
		    else:
		    	# login successfull
		        print("Success!! \nWelcome {}! \nLets get to work, Shall we:)".format(username))
		        break

	user_options(username, password)