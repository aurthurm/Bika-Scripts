# Developer: Aurthur Musendame

import pandas as pd
import datetime as dt
import numpy as np
import os
from pathlib import Path
from time import ctime, strftime

def merger_init(patients, analysis, merged_save_name):

    merged_all = merger(patients, analysis)

    filtered = data_filter(merged_all)

    renamed = renamer(filtered)

    shortened_dates(renamed)

 #   remove_dublicates(renamed)

    get_ages(renamed)

    print('\nCreating Age Ranges [ 14 <= | > 14 ] ... .... ... .... ...')
    renamed['Age Ranges'] = renamed['Age'].apply(age_ranges)

    copier(renamed)

    print('\nmaking numeric... .... ... .... ...')
    renamed['Results'] = renamed['Results'].apply(make_numeric)

    renamed['Results'] = renamed['Results'].astype(float).apply(np.int64)

   # result_numeriser(renamed)

    result_ranges(renamed)

    sanitizer(renamed)

    save_merged(renamed, merged_save_name)

 
#patients = patients.rename(columns={'UID': 'Patient_uid'})
def merger(patients, analysis):
    print('\nMerging Patients and Analysis Data ... .... ... .... ...')
    return pd.merge(left=patients,right=analysis, left_on='UID', right_on='Patient_uid')

def data_filter(unfiltered):
    print('\nFitering Columns [ Droping Useless Cols ]... .... ... .... ...')
    return unfiltered[
        [
            "Client",
            "PatientUID",
            "Patient_uid",
            "BirthDate",
            "Firstname",
            "ConsentSMS",
            "Gender",
            "Analyses_0_getRequestID",
            "ClientPatientID_x",
            "Analyses_0_Result",
            "Analyses_0_review_state",
            "RejectionReasons_0_checkbox",
            "RejectionReasons_0_checkbox_other",
            "RejectionReasons_0_other",
            "Surname",
            "Analyses_0_Unit",
            "creation_date_y",
            "Analyses_0_ResultCaptureDate",
            "DateReceived",
            "DateSampled",
            "DatePublished",
            "Creator_x",
            "SampleType",
            "getSampleID",

        ]
    ]

def renamer(funny_names):
    print('\nReNaming File Headers... .... ... .... ...')
    return funny_names.rename(
        columns={
            "Patient_uid" : "Unique Identidier",
            "BirthDate" : "Date of Birth",
            "Analyses_0_getRequestID" : "Request ID",
            "ClientPatientID_x" : "Client Patient ID",
            "Analyses_0_Result" : "Results",
            "Analyses_0_review_state" : "Review State",
            "Analyses_0_DateAnalysisPublished" : "Date Published",
            "Analyses_0_Unit" : "Unit",
            "creation_date_y" : "Date of Creation",
            "Analyses_0_ResultCaptureDate" : "Date Result Captured",
            "Creator_x" : "Analyses Creator",
            "SampleType" : "Sample Type",
            "getSampleID" : "Sample ID"
        }
    )

def shortened_dates(unshortened):

    def date_shortener( x ):   
        p = str(x)
        z = p[0:10]
        return z

    print('\nModifying Dates ... .... ... .... ...')
    unshortened['Date Result Captured'] = unshortened['Date Result Captured'].apply(date_shortener)
    unshortened['Date of Birth']= unshortened['Date of Birth'].apply(date_shortener)
    unshortened['Date of Creation']= unshortened['Date of Creation'].apply(date_shortener)
    unshortened['DateReceived']= unshortened['DateReceived'].apply(date_shortener)
    unshortened['DateSampled']= unshortened['DateSampled'].apply(date_shortener)
 

def remove_dublicates(dublicated):
    print("\nRemoving Dublicates ... ... ... ... ... ")
    dublicated.drop_duplicates(subset=['Unique Identidier'] , keep='first', inplace=True)

def get_ages(no_ages):
    def get_year( x ):   
        p = str(x)
        z = p[0:4]
        return z

    print('\nCaculating Ages ... .... ... .... ...')    
    no_ages['Year of Birth']= no_ages['Date of Birth']
    no_ages['Year of Birth']= no_ages['Year of Birth'].apply(get_year)
    this_year = str(pd.to_datetime(dt.datetime.today().strftime('%m-%d-%Y')).strftime('%Y'))
    no_ages['Age'] = int(this_year) - no_ages['Year of Birth'].astype(int)
    
def age_ranges(x):
    if x <= 14:
        z = "<= 14"
    else:
        z = "> 14"
    return z

def result_numeriser(unnumerised):    
    print('\nNumerising Results ... .... ... .... ...')
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

# redefining the numeriser
def copier(to_copy):
    print('\nCopying successfull .. ... ....')
    to_copy['Patient Results'] = to_copy['Results']

def make_numeric(x):
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
    print('\nCreating Result Categories [ TND, Failed, < 1000 , >= 1000 ] ... .... ... .... ...')
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

def save_merged(merged_data, merged_save_name):
    csv_save = os.path.abspath(os.path.join( str(os.path.expanduser('~')) , 'Documents/Bika Lims/', 'merged')) + '\\' + merged_save_name + ' - ' + strftime("%a %d %b %Y - %H%M") + '.csv'
    merged_data.to_csv(csv_save, index=False)
    print('\n\nYour data has been successfully Merged. \nWe have saved it for you in:\n' + csv_save)

def sanitizer(unsanitized):
    # deletion of unwanted columns
    print("\nSanitisation ... ... ...\n")
    #unsanitized.drop('Results', axis=1, inplace = True)
    cols = ['Results']
    unsanitized.drop(cols, axis=1, inplace = True)