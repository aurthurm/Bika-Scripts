# -*- coding: utf-8 -*-
# Developer: Aurthur Musendame

import pandas as pd
import datetime as dt
import numpy as np
import os
from pathlib import Path
from time import ctime, strftime

def merger_init(patients, analysis, merged_save_name):
    # Main Function for 
    # 1. Merging Patient, Analysis and Client Files
    # 2. Data Cleaning
    # 3. Exploration

    merged_all = merger(patients, analysis)
    renamed = renamer(merged_all)
    shortened_dates(renamed)
    remove_dublicates(renamed)
    get_ages(renamed)
    print('... ... Creating Age Ranges [ 14 <= | > 14 ]')
    renamed['Age Ranges'] = renamed['Age'].apply(age_ranges)
    copier(renamed)
    print('... ... Making numeric')
    # result_numeriser(renamed)
    renamed['Results'] = renamed['Results'].apply(make_numeric)
    renamed['Results'] = renamed['Results'].astype(float).apply(np.int64)
    # result_ranges(renamed)
    renamed['Results Ranges'] = renamed['Results'].apply(make_result_ranges)
    print('... ... Adding clients')
    with_clients = places_creator(renamed)
    sanitizer(with_clients)
    save_merged(with_clients, merged_save_name)
 
#patients = patients.rename(columns={'UID': 'Patient_uid'})
def merger(patients, analysis):
    # Merge Patients and Analyses Files
    print('\n... ... Merging Patients and Analysis Data')
    return pd.merge(left=patients,right=analysis, left_on='UID', right_on='Patient_uid')

def renamer(funny_names):
    # Rename filtered data cloumns with unfriendly naming conventios
    print('... ... ReNaming File Headers')
    return funny_names.rename(
        columns={
            "Patient_uid" : "Patient Unique ID",
            "PrimaryReferrerUID" : "Client UID",
            "BirthDate" : "Date of Birth",
            "Analyses_0_getRequestID" : "Request ID",
            "ClientPatientID" : "Client Patient ID",
            "Analyses_0_Result" : "Results",
            "Analyses_0_review_state" : "Review State",
            "Analyses_0_DateAnalysisPublished" : "Date Published",
            "Analyses_0_Unit" : "Unit",
            "creation_date" : "Date of Creation",
            "Analyses_0_ResultCaptureDate" : "Date Result Captured",
            "Creator" : "Analyses Creator",
            "SampleType" : "Sample Type",
            "getSampleID" : "Sample ID"
        }
    )

def shortened_dates(unshortened):
    # Make dates easier to work with through removal of everything except day, month and year.
    # A better pythonic dates library should be considered that this cheat

    def date_shortener( x ):   
        # pop out or cut and remove the last 10 strings in the date
        p = str(x)
        z = p[0:10]
        return z

    print('... ... Modifying Dates')
    unshortened['Date Result Captured'] = unshortened['Date Result Captured'].apply(date_shortener)
    unshortened['Date of Birth']= unshortened['Date of Birth'].apply(date_shortener)
    unshortened['Date of Creation']= unshortened['Date of Creation'].apply(date_shortener)
    unshortened['DateReceived']= unshortened['DateReceived'].apply(date_shortener)
    unshortened['DateSampled']= unshortened['DateSampled'].apply(date_shortener)
 

def remove_dublicates(dublicated):
    # if any, remove dublicated rows
    print("... ... Removing Dublicates")
    dublicated.drop_duplicates(subset=['Patient Unique ID'] , keep='first', inplace=True)

def get_ages(no_ages):
    # Calculate Patient Age as this year minus birth date

    def get_year( x ):
        # extract year from the date
        p = str(x)
        z = p[0:4]
        return z

    print('... ... Caculating Ages')    
    no_ages['Year of Birth']= no_ages['Date of Birth']
    no_ages['Year of Birth']= no_ages['Year of Birth'].apply(get_year)
    this_year = str(pd.to_datetime(dt.datetime.today().strftime('%m-%d-%Y')).strftime('%Y'))
    no_ages['Age'] = int(this_year) - no_ages['Year of Birth'].astype(int)
    
def age_ranges(x):
    # calculate age ranges
    # will be used to create a column of age ranges for easier pivot tables
    if x <= 14:
        z = "<= 14"
    else:
        z = "> 14"
    return z

def result_numeriser(unnumerised):
    # Convert all Results with strings values to some set number 
    # This makes it easier to calculate Viral Load Results ranges
    print('... ... Numerising Results')
    unnumerised['Patient Results'] = unnumerised['Results']
    
    unnumerised['Results'] = np.where(
        unnumerised['Results'] == "Target Not Detected", 
        999999999999, 
        np.where(
            unnumerised['Results'] == "Failed", 
            0, 
            np.where(
                unnumerised['Results'] == "Invalid", 
                999999999009,                  
                np.where(
                    unnumerised['Results'] == "INVALID", 
                    999999999009,                  
                    np.where(
                        unnumerised['Results'] == "FAILED", 
                        0, 
                        unnumerised['Results']
                    )
                )
            )
        )
    )
    unnumerised['Results'] = unnumerised['Results'].astype(float).apply(np.int64)

def copier(to_copy):
    # dublicate Results and give the new column a new name
    # This will avoid erroneous result manipulation giving us another result column to mingle and fool around with
    print('... ... Copying successfull')
    to_copy['Patient Results'] = to_copy['Results']

def make_numeric(x):
    # Numeriser -> == to result_numeriser.
    # Sometimes in some computers the above numeriser doesnt work.
    # This is an alternative finction
    if x == "Target Not Detected":
        z = 999999999999
    elif x == "Failed" or x == "FAILED":
        z = 0
    elif x == "Invalid" or x == "INVALID":
        z = 999999999009
    else:
        z = x
    return z
    
def result_ranges(no_ranges):    
    # using the numerised results to create a column of result ranges
    # good for easier xtables
    print('... ... Creating Result Categories [ TND, Failed, < 1000 , >= 1000 ]')
    no_ranges['Result Range'] = np.where(
        (no_ranges['Results'] == 0),
        'FAILED',
        np.where(
            (no_ranges['Results'] <= 1000) & (no_ranges['Results'] != 0),
            '<= 1000',
            np.where(
                (no_ranges['Results'] > 1000) & (no_ranges['Results'] < 999999999009),
                '> 1000',
                np.where(
                    (no_ranges['Results'] == 999999999999),
                    'TND',
                    'Invalid' # == 999999999009
                        )
                    )
            )
    )

def make_result_ranges(x):
    # Alternative to result_ranges
    if x == 0:
        z = "FAILED"
    elif x <= 1000 and x != 0:
        z = "<= 1000"
    elif x > 1000 and x < 999999999009:
        z = "> 1000"
    elif x == 999999999999:
        z = "TND"
    else:
        z = "Invalid"
    return z

def save_merged(merged_data, merged_save_name):
    # save the merged raw data as csv
    csv_save = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'merged')) + '\\' + merged_save_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.csv'
    merged_data.to_csv(csv_save, index=False)
    print('\nYour data has been successfully Merged. \nWe have saved it for you in the location below [*link*]:\n' + csv_save)

def sanitizer(unsanitized):
    # deletion of unwanted columns
    print("... ... Sanitisation ... ... ...")
    #unsanitized.drop('Results', axis=1, inplace = True)
    cols = ['Results','Name','id']
    unsanitized.drop(cols, axis=1, inplace = True)

def places_creator(no_places):
    # After merging analysis and patients we then merge it again with cliets datain order to
    # include Province and District Information
    all_clients = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'clients')) + '\\' + 'Clients.csv'
    all_clients = pd.read_csv(all_clients)
    return pd.merge(left=all_clients,right=no_places, left_on='Client UID', right_on='Client UID')

def Clients_filter(clients_unfiltered):
    # remove columns we are not interested in from the clients file
    return clients_unfiltered[
        [
            "ClientID",
            "Name",
            "PhysicalAddress_district",
            "PhysicalAddress_state",
            "UID",
            "id",
        ]
    ]

def clients_renamer(funny_names):
    # rename those ambiguous named columns in clients file
    return funny_names.rename(
        columns={
            "PhysicalAddress_district" : "District",
            "PhysicalAddress_state" : "State",
            "UID" : "Client UID",
            "getId" : "Client ID"
        }
    )
