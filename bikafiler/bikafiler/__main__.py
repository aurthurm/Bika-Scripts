from pathlib import Path
from time import strftime
import os, requests, json
import distutils.dir_util
import api 
import merger
from tkinter import *
from tkinter import filedialog
import pandas as pd
from json2csv import json_to_csv
import getpass
from progressbar.progressbar.bar import (Bar)
from time import ctime, strftime

#Clear screen
#clear = lambda: os.system('cls')
def clear():
    os.system('cls' if os.name=='nt' else 'clear')

# Paths to file type locations
json_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\json\\' )
merged_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\merged\\' )
csv_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\csv\\')

def main(username, password, api_url, page_nr, iterations, json_file, file_name, review_state, data, to_reduce):
	# intiate data pulling
	api.pull_data(username, password, api_url, page_nr, iterations, json_file, file_name, review_state, data, to_reduce)

def user_info():
	# Get user logon information and api
	print("\nPlease provide your Bika Credentials\n")
	username = str(input('Enter your Username:'))
	password = getpass.getpass('Enter Your Password:')
	your_api = input('Enter your API {e.g 19.0.9.8 } :')	
	return (username, password, your_api)

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

	main(username, password, api_url, page_nr, iterations, json_file, file_name, review_state, data="Clients", to_reduce="no")

	clients_file = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'clients')) + '\\' + file_name + '.csv'
	clients_raw = pd.read_csv(clients_file)
	clients_filtred = merger.Clients_filter(clients_raw)
	clients_final = merger.clients_renamer(clients_filtred)
	clients_final.drop_duplicates(subset=['Client UID'] , keep='first', inplace=True)
	clients_final.to_csv(clients_file, sep=',', encoding='utf-8',header=True, index=False)

def pull_data_singles(username, password, api_url, page_nr, iterations, json_file_path, file_name, review_state, data, to_reduce):
	# login to the Bika Lims API and pull data, save json file and convert it to csv using json2csv

	#print('\nStart Time')
	start_time = ctime()
	#print(start_time)

	print('\nWait while we process the data for you ....\n')
	bar = Bar('Processing', max=iterations)
	counter = 0
	file_name += '_'
	for i in range(iterations + 1):
		api_url+=str(page_nr)
		api_data = requests.get(api_url, auth=(username, password ))
		api_data = json.loads(api_data.text)
		
		json_file = str( str(json_file_path) + '\\' + file_name + ' - ' + strftime("%a %d %b %Y - %H%M%S") + '.json' )
		api.init( json_file_path, Path(json_file))

		api.list_concat(api_data['objects'], Path(json_file))
		file_name += str(counter)
		api.to_cvs(Path(json_file), file_name, review_state, data, to_reduce, printing=False)

	    # Remove previous concatenation before new concatenation : str(i)
		if page_nr < 10:                         
			api_url=api_url[:-1]
		elif page_nr >= 10 and page_nr < 100:
			api_url=api_url[:-2]
		else:
			api_url=api_url[:-3]

		if counter < 10:                         
			file_name=file_name[:-1]
		elif counter >= 10 and page_nr < 100:
			file_name=file_name[:-2]
		else:
			file_name=file_name[:-3]

		page_nr+=1 # increamenting the loop
		counter+=1
		bar.next()

	bar.finish()	
	print('\n=====   DONE!  =====\n')
	print('Start Time: {}.\nEnd Time: {}.\n'.format(start_time,ctime()))

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

def analysis_categories(username, password, json_file_path = "None"):
	clear()
	while True:
		print('From the data categories listed below, what category do you want? \n')
		print('[1] : Analysis Results \n[2] : Patients \n[3] : Both  \n[4] : Return to main Menu\n')
		user_choice = int(input('Make your choice (1/2/3) and Press the Return Key [Enter] >>'))

		if user_choice == 1:

			file_name = input('Give a Name to the File for saving {e.g Analysis} >>')
			clear()
			print("Data can be in any of the following firts 3 Review States\n")
			print("[1] : Published\n[2] : Verified\n[3] : To be Verified\n[4] : Return to previous Menu (Categories)\n[5] : Return to main Menu\n")
			data_type = int(input('Make your choice (1/2/3) and Press the Return Key [Enter] >>'))

			if data_type == 1:
				review_state = "published"
			elif data_type == 2:
				review_state = "verified"
			elif data_type == 3:
				review_state = "to_be_verified"
			elif data_type == 4:
				analysis_categories(username, password, json_file_path)
			else:
				user_options(username, password)

			#user_info()
			page_size = input('Enter page size {e.g 5000 } :')
			iterations = int(input('Enter number of cycles or iterations {e.g 5000 }:'))
			api_url = "http://" + str(your_api) + "/@@API/read?catalog_name=bika_catalog_analysisrequest_listing&review_state=" + str(review_state) + "&sort_order=descending&page_size=" + str(page_size) + "&page_nr="
			page_nr = 0
			data = "analyses"
			to_reduce = "reduce"

			#main(username, password, api_url, page_nr, iterations, json_file, file_name, review_state)
			pull_data_singles(username, password, api_url, page_nr, iterations, json_file_path, file_name, review_state,data,to_reduce)
			
			# Return user back to options before exit
			user_options(username, password)

		elif user_choice == 2:

			file_name = input('Enter File save name {e.g Patients } :')
			# If user mistakenly takes an wrong option let thenm return
			if file_name == 'return':
				user_options(username, password)

			review_state = "none"

			#user_info()
			page_size = input('Enter page size {e.g 5000 }:')
			iterations = int(input('Enter number of cycles or iterations {e.g 2 }:'))
			api_url =  "http://" + str(your_api) + "/@@API/read?catalog_name=bikahealth_catalog_patient_listing&sort_order=descending&page_size=" + str(page_size) + "&page_nr="
			page_nr = 0
			data = "patients"
			to_reduce = "reduce"

			#main(username, password, api_url, page_nr, iterations, json_file, file_name, review_state)
			pull_data_singles(username, password, api_url, page_nr, iterations, json_file_path, file_name, review_state,data,to_reduce)
			
			# Return user back to options before exit
			user_options(username, password)

		elif user_choice == 3:	

			patients_file_name = input('Enter Patients File save name {e.g Patients } :')		
			analysis_file_name = input('Enter Analysis File save name {e.g Analysis } :')

			patients_review_state = "none"
			analysis_review_state = input('Enter Analysis review state {e.g published } :')

			#user_info()

			patients_page_size = input('Enter Patients page size {e.g 5000 }:')
			patients_iterations = int(input('Enter number of Patient cycles or iterations {e.g 2 }:'))

			analysis_page_size = input('Enter Analysis page size {e.g 5000 }:')
			analysis_iterations = int(input('Enter number of Analysis cycles or iterations {e.g 2 }:'))

			analysis_url = "http://" + str(your_api) + "/@@API/read?catalog_name=bika_catalog_analysisrequest_listing&review_state=" + str(analysis_review_state) + "&sort_order=descending&page_size=" + str(analysis_page_size) + "&page_nr="
			patient_url =  "http://" + str(your_api) + "/@@API/read?catalog_name=bikahealth_catalog_patient_listing&sort_order=descending&page_size=" + str(patients_page_size) + "&page_nr="
			page_nr = 0   

			print('Patient Data Processing')
			#main(username, password, patient_url, page_nr, patients_iterations, patient_json_file, patients_file_name, patients_review_state)
			pull_data_singles(username, password, patient_url, page_nr, patients_iterations, json_file_path, patients_file_name, patients_review_state, data="patients",to_reduce="reduce")
			print('Analysis Data Processing')
			#main(username, password, analysis_url, page_nr, analysis_iterations, analysis_json_file, analysis_file_name, analysis_review_state)
			pull_data_singles(username, password, analysis_url, page_nr, analysis_iterations, json_file_path, analysis_file_name, analysis_review_state, data="analyses",to_reduce="reduce")
			#break

			# Return user back to options before exit
			user_options(username, password)

		elif user_choice == 4:
			clear()
			# Return user back to options before exit
			user_options(username, password)

			
		else:
			Print("Please select only from the options provide\nTry Again!!! (:")
			continue

def user_options(username, password):
	# Ask user some questions on what they want to do and initiate the api
	if __name__ == "__main__":

		print('\n')

		while True:	
			print('What do you want to do? Provided below is a list of alternatives to get you started! :)\n')
			print('[1] : Pull New Data from API \n[2] : Merge Patients and Analysis Data  \n[3] : Convert JSON File types to CSV Files\n[4] : Update Clients [Provinces/Districts]\n[5] : Quit\n')
			do_choice = int(input('Make your choice (1/2/3/4/5) and Press the Return Key [Enter] >>'))

			if do_choice == 1:
				# Get new datasets from the API
				clear()
				analysis_categories(username, password, json_file_path)
				break

			elif do_choice == 2:
				clear()
				# Merge Patiets and Analyses Data Files
				client_data_check()

				if not merged_file_path.is_dir():
				    os.makedirs(merged_file_path)

				tk_init()
				merged_save_name = str(input('Provide a Name for Saving Merged Data:'))
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
				file_name = input('Enter File Save name :')
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
				get_clients(username, password)
				#break
				# Return user back to options before exit
				user_options(username, password)

			elif do_choice == 5:
				print('Hope you had an amazing experience, we hope to see you again.\nLet us know is there is anything you wish it could de added in this script\nwe are proud to enhance your experience and see you smile :) Aurthur')
				clear()
				exit()

			else:
				print("Please make your choice from the given list\nTry Again! (:")
				continue

# Lets start
while True:
	clear()
	# Check login detais. if correct continur else ask user to input again
	username, password, your_api = user_info()
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
	    	print("\nEither your username or password is incorrect: TRY AGAIN !!!!! (:\n")
	    	continue
	    else:
	    	# login successfull
	        print("Success!! \nWelcome {}! \nLets get to work, Shall we:)".format(username))
	        break

user_options(username, password)