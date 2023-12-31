#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Aug 22 2023
Stumps-related helper functions
"""

import csv
import numpy as np
import pandas as pd
import utils.stumps as stumps


LTOUR_feature_list = ['concurrent_MME', 'concurrent_methadone_MME', 'num_prescribers',\
'num_pharmacies', 'consecutive_days', 'concurrent_benzo',\
'quantity', 'Codeine', 'Hydrocodone', 'Oxycodone', 'Morphine', 'HMFO',\
'Medicaid', 'CommercialIns', 'Medicare', 'CashCredit',  'MilitaryIns', 'WorkersComp', 'Other', 'IndianNation',\
'num_prior_presc', 'avgDays', 'diff_MME', 'diff_quantity', 'diff_days',\
'switch_drug', 'switch_payment', 'ever_switch_drug', 'ever_switch_payment']

stumps_feature_list = ['concurrent_MME', 'concurrent_methadone_MME', 'num_prescribers',\
'num_pharmacies', 'consecutive_days', 'concurrent_benzo',\
'quantity', 'num_prior_presc', 'avgDays', 'diff_MME', 'diff_quantity', 'diff_days']


def create_stumps(year, feature_list=LTOUR_feature_list, stumps_feature_list=stumps_feature_list, datadir='/mnt/phd/jihu/opioid/Data/'):
        
    FULL = pd.read_csv(f'{datadir}FULL_{str(year)}_LONGTERM_INPUT_UPTOFIRST.csv', delimiter = ",",\
    dtype={'concurrent_MME': float, 'concurrent_methadone_MME': float, 'num_prescribers': int,\
    'num_pharmacies': int, 'concurrent_benzo': int, 'consecutive_days': int}).fillna(0)

    FULL.rename(columns={'num_presc':'num_prior_presc', 'quantity_diff': 'diff_quantity', 'MME_diff': 'diff_MME', 'days_diff': 'diff_days'}, inplace=True)
    FULL = FULL[feature_list]

    cutoffs = []
    for column_name in FULL.columns:
        if column_name == 'concurrent_MME' or column_name == 'concurrent_methadone_MME':
            cutoffs.append([10, 15, 20, 25, 30, 35, 40, 45, 50, 75, 100, 200, 300])
        elif column_name == 'num_prescribers' or column_name == 'num_pharmacies':
            cutoffs.append([n for n in range(2, 11)])
        elif column_name == 'concurrent_benzo':
            cutoffs.append([1])
        elif column_name == 'consecutive_days':
            cutoffs.append([1, 3, 5, 7, 10, 14, 21, 25, 30, 60, 90])
        elif column_name == 'quantity':
            cutoffs.append([10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200, 300])
        elif column_name == 'num_prior_presc':
            cutoffs.append([2]) # prior prescription or not
        elif column_name == 'avgDays':
            cutoffs.append([3, 5, 7, 10, 14, 21, 25, 30, 60])
        elif column_name == 'diff_MME' or column_name == 'diff_quantity' or column_name == 'diff_days':
            cutoffs.append([1])
        else:
            pass


    ## Divide into 20 folds
    N = 20
    FULL_splited = np.array_split(FULL, N)
    for i in range(N):

        FULL_fold = FULL_splited[i]        

        x = FULL_fold[stumps_feature_list]
        x_stumps = stumps.create_stumps(x.values, x.columns, cutoffs)

        x_rest = FULL_fold[FULL_fold.columns.drop(stumps_feature_list)]
        
        new_data = pd.concat([x_stumps.reset_index(drop=True), x_rest.reset_index(drop=True)], axis = 1)
        new_data.to_csv(f'{datadir}FULL_{str(year)}_STUMPS_UPTOFIRST{str(i)}.csv', header=True, index=False)
    
    print("Done!\n")
    
    return     



# ========================================================================================

    

def create_intervals(year, scenario='flexible', feature_list=LTOUR_feature_list, datadir='/mnt/phd/jihu/opioid/Data/'):
    
    '''
    Create intervals stumps for the dataset
    For this we also need to edit stumps.create_stumps as well
    
    Parameters
    ----------
    year
    scenario: basic feature (flexible) / full
    '''

    FULL = pd.read_csv(f'{datadir}FULL_{str(year)}_LONGTERM_INPUT.csv', delimiter = ",", 
                        dtype={'concurrent_MME': float, 'concurrent_methadone_MME': float,
                              'num_prescribers': int, 'num_pharmacies': int,
                              'concurrent_benzo': int, 'consecutive_days': int}).fillna(0)
    FULL = FULL[FULL.columns.drop(list(FULL.filter(regex='alert')))]
    FULL = FULL.drop(columns = ['drug_payment'])
    
    
    if scenario == 'flexible':
        x_all = FULL[['concurrent_MME', 'concurrent_methadone_MME', 'num_prescribers',
                      'num_pharmacies', 'concurrent_benzo', 'consecutive_days']]
        
        cutoffs_i = []
        for column_name in ['concurrent_MME', 'concurrent_methadone_MME', 'consecutive_days']:
            if column_name == 'num_prescribers' or column_name == 'num_pharmacies':
                cutoffs_i.append([n for n in range(0, 10)])
            elif column_name == 'concurrent_benzo':
                cutoffs_i.append([0, 1, 2, 3, 4, 5, 10])
            elif column_name == 'consecutive_days' or column_name == 'concurrent_methadone_MME':
                cutoffs_i.append([n for n in range(0, 90) if n % 10 == 0])
            else:
                cutoffs_i.append([n for n in range(0, 200) if n % 10 == 0])
        
        cutoffs_s = []
        for column_name in ['num_prescribers', 'num_pharmacies', 'concurrent_benzo']:
            if column_name == 'num_prescribers' or column_name == 'num_pharmacies':
                cutoffs_s.append([n for n in range(0, 10)])
            elif column_name == 'concurrent_benzo':
                cutoffs_s.append([0, 1, 2, 3, 4, 5, 10])
            elif column_name == 'consecutive_days' or column_name == 'concurrent_methadone_MME':
                cutoffs_s.append([n for n in range(0, 90) if n % 10 == 0])
            else:
                cutoffs_s.append([n for n in range(0, 200) if n % 10 == 0])
                
        ## Divide into 20 folds
        N = 20
        FULL_splited = np.array_split(FULL, N)
        for i in range(N):
            FULL_fold = FULL_splited[i]
            x = FULL_fold[['concurrent_MME', 'concurrent_methadone_MME', 'num_prescribers',
                          'num_pharmacies', 'concurrent_benzo', 'consecutive_days']]
            
            x_i = FULL_fold[['concurrent_MME', 'concurrent_methadone_MME', 'consecutive_days']]
            x_s = FULL_fold[['num_prescribers', 'num_pharmacies', 'concurrent_benzo']]
            
            x_intervals = stumps.create_intervals(x_i.values, x_i.columns, cutoffs_i)
            x_stumps = stumps.create_stumps(x_s.values, x_s.columns, cutoffs_s)
            
            new_data = pd.concat([x_intervals.reset_index(drop=True), x_stumps.reset_index(drop=True)], axis = 1)
            new_data.to_csv('Data/FULL_' + str(year) + scenario + '_INTERVALS' + str(i) + '.csv', header=True, index=False)  
    

    elif scenario == 'full':
        x_all = FULL[feature_list]
        
        cutoffs = []
        for column_name in x_all.columns:
            if column_name == 'num_prescribers' or column_name == 'num_pharmacies':
                cutoffs.append([n for n in range(0, 10)])
            elif column_name == 'concurrent_benzo' or column_name == 'concurrent_benzo_same' or \
                column_name == 'concurrent_benzo_diff' or column_name == 'num_presc':
                cutoffs.append([0, 1, 2, 3, 4, 5, 10])
            elif column_name == 'consecutive_days' or column_name == 'concurrent_methadone_MME' or \
                column_name == 'days_diff':
                cutoffs.append([n for n in range(0, 90) if n % 10 == 0])
            elif column_name == 'dose_diff' or column_name == 'concurrent_MME_diff':
                cutoffs.append([n for n in range(0, 100) if n % 10 == 0])
            elif column_name == 'age':
                cutoffs.append([n for n in range(20, 80) if n % 10 == 0])
            else:
                cutoffs.append([n for n in range(0, 200) if n % 10 == 0])
                
        ## Divide into 20 folds
        N = 20
        FULL_splited = np.array_split(FULL, N)
        for i in range(N):

            FULL_fold = FULL_splited[i]
            x = FULL_fold[feature_list]
            x_stumps = stumps.create_stumps(x.values, x.columns, cutoffs)
            x_rest = FULL_fold[FULL_fold.columns.drop(feature_list)]

            new_data = pd.concat([x_stumps.reset_index(drop=True), x_rest.reset_index(drop=True)], axis = 1)
            print(new_data.shape)
            new_data.to_csv('Data/FULL_' + str(year) + scenario + '_INTERVALS' + str(i) + '.csv', header=True, index=False)         
    
    else:
        print('Scenario cannot be identified')



    


