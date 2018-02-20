# Upon First time use get user API adress and save it
import os, json, distutils.dir_util
from pathlib import Path
from . import api

def configure(config_file):	
	while True:
		station_api = input('\nPlease provide your Bika API (e.g 10.0.0.184 )>>')
		if not station_api:
			print('\API cannot e empty!!')
			continue
		else:
			print('\nYou have provided ' + station_api + ' as your Bika API. Is it Correct?')
			_note = 'Press (Enter) or ( y then Enter ) if corrent or any character if wrong >>'
			_response = input(_note)
			if not ((_response.lower() == 'y') or (_response.strip() == '')):
				continue
			else:
				#save user api
				print('!!! Thanks !!! ')

				configurations = {
				 "data":[
				         {"API":station_api}
				        ]
				}	

				with open(config_file, 'w') as outfile:
					json.dump(configurations, outfile, sort_keys = True, indent = 4, ensure_ascii = False,  separators=(',', ':'))

				break

def config_data_check():
	# Check if client file is availabe
	# if available continue else create one
	config_file_path = Path( str(os.path.expanduser('~')) + '\\Documents\\Bika LIMS\\.Configs\\' )
	config_file = Path( str(config_file_path) + '\\' + 'config.json' )

	if config_file_path.is_dir():
		if not config_file.is_file():
			print("\nHelp us cofigure this api to suit your station! This is a one time setup")
			api.init(config_file_path, config_file)
			configure(config_file)
		else:
			# if config file is found , then check is there are any configurations present
			with open(config_file) as data:
				contents = json.load(data)
			#GET THE API VALUE
			stored_api = contents["data"][0]["API"]
			#CHECK IF stored_api IS NOT EMPTY
			if not stored_api.strip():
				print("\nHelp us cofigure this api to suit your station! This is a one time setup")
				configure(config_file)
			pass
	else:
		print("\nHelp us cofigure this api to suit your station! This is a one time setup")
		api.create_dir(config_file_path)
		api.init(config_file_path, config_file)
		configure(config_file)


