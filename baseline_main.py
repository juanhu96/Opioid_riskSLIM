#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 14:57:11 2022

@author: jingyuanhu
"""

import os
import time
import numpy as np
import pandas as pd
from sklearn import tree
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from joblib import parallel_backend
import utils.baseline_functions as base
os.chdir('/mnt/phd/jihu/opioid')
year = 2019

with parallel_backend('threading', n_jobs=40):
    
    SAMPLE = pd.read_csv('Data/FULL_' + str(year) +'_LONGTERM_UPTOFIRST.csv', delimiter = ",", 
                         dtype={'concurrent_MME': float, 'concurrent_methadone_MME': float,
                                'num_prescribers': int, 'num_pharmacies': int,
                                'concurrent_benzo': int, 'consecutive_days': int,
                                'alert1': int, 'alert2': int, 'alert3': int, 'alert4': int, 'alert5': int, 'alert6': int})
    SAMPLE = SAMPLE.fillna(0)
    
    ###########################################################################
    
    N = 20
    SAMPLE_STUMPS = pd.read_csv('Data/FULL_' + str(year) + '_STUMPS_UPTOFIRST' + str(0) + '.csv', delimiter = ",")
    for i in range(1, N):
        TEMP = pd.read_csv('Data/FULL_' + str(year) + '_STUMPS_UPTOFIRST' + str(i) + '.csv', delimiter = ",")
        SAMPLE_STUMPS = pd.concat([SAMPLE_STUMPS, TEMP])
    
    SAMPLE_STUMPS = SAMPLE_STUMPS[SAMPLE_STUMPS.columns.drop([col for col in SAMPLE_STUMPS if col.startswith(('long_term_180', 'age', 'days_supply', 'daily_dose',
                                                                                                              'quantity_per_day', 'total_dose', 'dose_diff',
                                                                                                              'concurrent_benzo_same', 'concurrent_benzo_diff',
                                                                                                              'concurrent_methadone_MME', 'avgMME',
                                                                                                              'consecutive_days'))])]
    
    SAMPLE_STUMPS = SAMPLE_STUMPS[SAMPLE_STUMPS.columns.drop(['num_prescribers1', 'num_pharmacies1', 'num_presc1'])]
    SAMPLE_STUMPS = SAMPLE_STUMPS[SAMPLE_STUMPS.columns.drop(['quantity10', 'quantity15', 'quantity20', 'quantity25', 'quantity30',
                                                              'quantity40', 'quantity50', 'quantity75', 'quantity100', 'quantity150',
                                                              'quantity200', 'quantity300'])]
    
    SAMPLE_STUMPS = SAMPLE_STUMPS[SAMPLE_STUMPS.columns.drop([col for col in SAMPLE_STUMPS if col.startswith(('Codeine_MME', 'Hydrocodone_MME',
                                                                                                              'Oxycodone_MME', 'Morphine_MME', 
                                                                                                              'Hydromorphone_MME', 'Methadone_MME',
                                                                                                              'Fentanyl_MME', 'Oxymorphone_MME'))])]
    
    SAMPLE_STUMPS = SAMPLE_STUMPS[SAMPLE_STUMPS.columns.drop(['Codeine_Medicaid', 'Codeine_CommercialIns', 
                                                              'Codeine_Medicare', 'Codeine_CashCredit', 'Codeine_MilitaryIns', 'Codeine_WorkersComp', 'Codeine_Other',
                                                              'Codeine_IndianNation', 'Hydrocodone_Medicaid', 'Hydrocodone_CommercialIns', 'Hydrocodone_Medicare',
                                                              'Hydrocodone_CashCredit', 'Hydrocodone_MilitaryIns', 'Hydrocodone_WorkersComp', 'Hydrocodone_Other',
                                                              'Hydrocodone_IndianNation', 'Oxycodone_Medicaid', 'Oxycodone_CommercialIns', 'Oxycodone_Medicare',
                                                              'Oxycodone_CashCredit', 'Oxycodone_MilitaryIns', 'Oxycodone_WorkersComp', 'Oxycodone_Other',
                                                              'Oxycodone_IndianNation', 'Morphine_Medicaid', 'Morphine_CommercialIns', 'Morphine_Medicare',
                                                              'Morphine_CashCredit', 'Morphine_MilitaryIns', 'Morphine_WorkersComp', 'Morphine_Other',
                                                              'Morphine_IndianNation', 'Hydromorphone_Medicaid', 'Hydromorphone_CommercialIns', 'Hydromorphone_Medicare',
                                                              'Hydromorphone_CashCredit', 'Hydromorphone_MilitaryIns', 'Hydromorphone_WorkersComp', 'Hydromorphone_Other',
                                                              'Hydromorphone_IndianNation', 'Methadone_Medicaid', 'Methadone_CommercialIns', 'Methadone_Medicare',
                                                              'Methadone_CashCredit', 'Methadone_MilitaryIns', 'Methadone_WorkersComp', 'Methadone_Other', 'Methadone_IndianNation',
                                                              'Fentanyl_Medicaid', 'Fentanyl_CommercialIns', 'Fentanyl_Medicare', 'Fentanyl_CashCredit', 'Fentanyl_MilitaryIns',
                                                              'Fentanyl_WorkersComp', 'Fentanyl_Other', 'Fentanyl_IndianNation', 'Oxymorphone_Medicaid', 'Oxymorphone_CommercialIns',
                                                              'Oxymorphone_Medicare', 'Oxymorphone_CashCredit', 'Oxymorphone_MilitaryIns', 'Oxymorphone_WorkersComp', 'Oxymorphone_Other',
                                                              'Oxymorphone_IndianNation'])]
    
    SAMPLE_STUMPS = SAMPLE_STUMPS[SAMPLE_STUMPS.columns.drop(['Hydromorphone', 'Methadone', 'Fentanyl', 'Oxymorphone'])]
    
    SAMPLE_STUMPS = SAMPLE_STUMPS[SAMPLE_STUMPS.columns.drop(['MME_diff25', 'MME_diff50', 'MME_diff75', 'MME_diff100', 'MME_diff150',
                                                              'quantity_diff25', 'quantity_diff50', 'quantity_diff75', 'quantity_diff100', 'quantity_diff150',
                                                              'days_diff3', 'days_diff5', 'days_diff7', 'days_diff10', 'days_diff14', 'days_diff21', 'days_diff25', 'days_diff30'])]
        
    SAMPLE_STUMPS['(Intercept)'] = 1
    intercept = SAMPLE_STUMPS.pop('(Intercept)')
    SAMPLE_STUMPS.insert(0, '(Intercept)', intercept)
    x = SAMPLE_STUMPS
    
    print(SAMPLE_STUMPS.columns.tolist()) # so that we know the order of features
    
    ## Use stumps instead of 
    # x = SAMPLE[['concurrent_MME', 'concurrent_methadone_MME', 'num_prescribers', 'num_pharmacies', 'consecutive_days', 'concurrent_benzo']]
    
    ###########################################################################
    
    y = SAMPLE['long_term_180'].values
    
    start = time.time()

    # Decision Tree
    depth = [3,4,5,6]
    min_samples = [5,10]
    impurity = [0.001,0.01,0.1]
    dt_summary_balanced = base.DecisionTree(X=x, Y=y, 
                                    depth=depth, 
                                    min_samples=min_samples, 
                                    impurity=impurity,
                                    class_weight="balanced",
                                    seed=42)
    
    # os.chdir('/mnt/phd/jihu/opioid')
    # np.savetxt("Result/dt_y.csv", dt_summary_balanced, delimiter=",")

    # L2 logistic
    # c = np.linspace(1e-5,1,5).tolist()
    # c = [1e-5, 1e-3, 1e-1, 10]
    # logistic_summary_balanced = base.Logistic(X=x, Y=y, C=c, class_weight="balanced", seed=42)
    # np.savetxt("Result/l2_y.csv", logistic_summary_balanced, delimiter=",")
    
    # L1 logistic
    # c = np.linspace(1e-5,1,5).tolist()
    # c = [1e-5, 1e-3, 1e-1, 10]
    # lasso_summary_balanced = base.Lasso(X=x, Y=y, C=c, class_weight="balanced", seed=42)
    # np.savetxt("Result/l1_y.csv", lasso_summary_balanced, delimiter=",")
    
    # LinearSVM
    # c = np.linspace(1e-6,1e-2,5).tolist()
    # svm_summary_balanced = base.LinearSVM(X=x, Y=y, C=c, class_weight="balanced", seed=42)
    # np.savetxt("Result/svm_y.csv", svm_summary_balanced, delimiter=",")
    
    # Random Forest 
    # depth = [3,4,5,6]
    # n_estimators = [50,100,200]
    # impurity = [0.001,0.01]
    # rf_summary_balanced = base.RF(X=x, Y=y,
    #                               depth=depth,
    #                               estimators=n_estimators,
    #                               impurity=impurity,
    #                               class_weight="balanced",
    #                               seed=42)
    # np.savetxt("Result/rf_y.csv", rf_summary_balanced, delimiter=",")
    
    # XGBoost
    # depth = [4,5,6]
    # n_estimators =  [50,100]
    # gamma = [5,10]
    # child_weight = [5,10]
    # xgb_summary_balanced = base.XGB(X=x, Y=y,
    #                                 depth=depth,
    #                                 estimators=n_estimators,
    #                                 gamma=gamma,
    #                                 child_weight=child_weight,
    #                                 class_weight="balanced",
    #                                 seed=42)
    # np.savetxt("Result/xgb_y.csv", xgb_summary_balanced, delimiter=",")
    
    end = time.time()
    print(str(round(end - start,1)) + ' seconds')
    

    ###########################################################################
    
    # DT
    balanced = {"Accuracy": str(round(np.mean(dt_summary_balanced['holdout_test_accuracy']), 4)) + " (" + str(round(np.std(dt_summary_balanced['holdout_test_accuracy']), 4)) + ")",
               "Recall": str(round(np.mean(dt_summary_balanced['holdout_test_recall']), 4)) + " (" + str(round(np.std(dt_summary_balanced['holdout_test_recall']), 4)) + ")",
               "Precision": str(round(np.mean(dt_summary_balanced['holdout_test_precision']), 4)) + " (" + str(round(np.std(dt_summary_balanced['holdout_test_precision']), 4)) + ")",
               "ROC AUC": str(round(np.mean(dt_summary_balanced['holdout_test_roc_auc']), 4)) + " (" + str(round(np.std(dt_summary_balanced['holdout_test_roc_auc']), 4)) + ")",
               "PR AUC": str(round(np.mean(dt_summary_balanced['holdout_test_pr_auc']), 4)) + " (" + str(round(np.std(dt_summary_balanced['holdout_test_pr_auc']), 4)) + ")",
               "Brier": str(round(np.mean(dt_summary_balanced['holdout_test_brier']), 4)) + " (" + str(round(np.std(dt_summary_balanced['holdout_test_brier']), 4)) + ")",
               "F2": str(round(np.mean(dt_summary_balanced['holdout_test_f2']), 4)) + " (" + str(round(np.std(dt_summary_balanced['holdout_test_f2']), 4)) + ")"}
    
    balanced = pd.DataFrame.from_dict(balanced, orient='index', columns=['Decision Tree'])
    dt_results = balanced 
    print(dt_results)

    # L2
    # balanced = {"Accuracy": str(round(np.mean(logistic_summary_balanced['holdout_test_accuracy']), 4)) + " (" + str(round(np.std(logistic_summary_balanced['holdout_test_accuracy']), 4)) + ")",
    #             "Recall": str(round(np.mean(logistic_summary_balanced['holdout_test_recall']), 4)) + " (" + str(round(np.std(logistic_summary_balanced['holdout_test_recall']), 4)) + ")",
    #             "Precision": str(round(np.mean(logistic_summary_balanced['holdout_test_precision']), 4)) + " (" + str(round(np.std(logistic_summary_balanced['holdout_test_precision']), 4)) + ")",
    #             "ROC AUC": str(round(np.mean(logistic_summary_balanced['holdout_test_roc_auc']), 4)) + " (" + str(round(np.std(logistic_summary_balanced['holdout_test_roc_auc']), 4)) + ")",
    #             "PR AUC": str(round(np.mean(logistic_summary_balanced['holdout_test_pr_auc']), 4)) + " (" + str(round(np.std(logistic_summary_balanced['holdout_test_pr_auc']), 4)) + ")",
    #             "Brier": str(round(np.mean(logistic_summary_balanced['holdout_test_brier']), 4)) + " (" + str(round(np.std(logistic_summary_balanced['holdout_test_brier']), 4)) + ")",
    #             "F2": str(round(np.mean(logistic_summary_balanced['holdout_test_f2']), 4)) + " (" + str(round(np.std(logistic_summary_balanced['holdout_test_f2']), 4)) + ")"}
    
    # balanced = pd.DataFrame.from_dict(balanced, orient='index', columns=['Logistic (L2)'])
    # logistic_results = balanced
    

    # L1
    # balanced = {"Accuracy": str(round(np.mean(lasso_summary_balanced['holdout_test_accuracy']), 4)) + " (" + str(round(np.std(lasso_summary_balanced['holdout_test_accuracy']), 4)) + ")",
    #             "Recall": str(round(np.mean(lasso_summary_balanced['holdout_test_recall']), 4)) + " (" + str(round(np.std(lasso_summary_balanced['holdout_test_recall']), 4)) + ")",
    #             "Precision": str(round(np.mean(lasso_summary_balanced['holdout_test_precision']), 4)) + " (" + str(round(np.std(lasso_summary_balanced['holdout_test_precision']), 4)) + ")",
    #             "ROC AUC": str(round(np.mean(lasso_summary_balanced['holdout_test_roc_auc']), 4)) + " (" + str(round(np.std(lasso_summary_balanced['holdout_test_roc_auc']), 4)) + ")",
    #             "PR AUC": str(round(np.mean(lasso_summary_balanced['holdout_test_pr_auc']), 4)) + " (" + str(round(np.std(lasso_summary_balanced['holdout_test_pr_auc']), 4)) + ")",
    #             "Brier": str(round(np.mean(lasso_summary_balanced['holdout_test_brier']), 4)) + " (" + str(round(np.std(lasso_summary_balanced['holdout_test_brier']), 4)) + ")",
    #             "F2": str(round(np.mean(lasso_summary_balanced['holdout_test_f2']), 4)) + " (" + str(round(np.std(lasso_summary_balanced['holdout_test_f2']), 4)) + ")"}
    
    # balanced = pd.DataFrame.from_dict(balanced, orient='index', columns=['Logistic (L1)'])
    # lasso_results = balanced

    # SVM
    # balanced = {"Accuracy": str(round(np.mean(svm_summary_balanced['holdout_test_accuracy']), 4)) + " (" + str(round(np.std(svm_summary_balanced['holdout_test_accuracy']), 4)) + ")",
    #            "Recall": str(round(np.mean(svm_summary_balanced['holdout_test_recall']), 4)) + " (" + str(round(np.std(svm_summary_balanced['holdout_test_recall']), 4)) + ")",
    #            "Precision": str(round(np.mean(svm_summary_balanced['holdout_test_precision']), 4)) + " (" + str(round(np.std(svm_summary_balanced['holdout_test_precision']), 4)) + ")",
    #            "ROC AUC": str(round(np.mean(svm_summary_balanced['holdout_test_roc_auc']), 4)) + " (" + str(round(np.std(svm_summary_balanced['holdout_test_roc_auc']), 4)) + ")",
    #            "PR AUC": str(round(np.mean(svm_summary_balanced['holdout_test_pr_auc']), 4)) + " (" + str(round(np.std(svm_summary_balanced['holdout_test_pr_auc']), 4)) + ")",
    #            "Brier": str(round(np.mean(svm_summary_balanced['holdout_test_brier']), 4)) + " (" + str(round(np.std(svm_summary_balanced['holdout_test_brier']), 4)) + ")",
    #            "F2": str(round(np.mean(svm_summary_balanced['holdout_test_f2']), 4)) + " (" + str(round(np.std(svm_summary_balanced['holdout_test_f2']), 4)) + ")"}
    
    # balanced = pd.DataFrame.from_dict(balanced, orient='index', columns=['SVM'])
    # svm_results = balanced
    
    # RF
    # balanced = {"Accuracy": str(round(np.mean(rf_summary_balanced['holdout_test_accuracy']), 4)) + " (" + str(round(np.std(rf_summary_balanced['holdout_test_accuracy']), 4)) + ")",
    #            "Recall": str(round(np.mean(rf_summary_balanced['holdout_test_recall']), 4)) + " (" + str(round(np.std(rf_summary_balanced['holdout_test_recall']), 4)) + ")",
    #            "Precision": str(round(np.mean(rf_summary_balanced['holdout_test_precision']), 4)) + " (" + str(round(np.std(rf_summary_balanced['holdout_test_precision']), 4)) + ")",
    #            "ROC AUC": str(round(np.mean(rf_summary_balanced['holdout_test_roc_auc']), 4)) + " (" + str(round(np.std(rf_summary_balanced['holdout_test_roc_auc']), 4)) + ")",
    #            "PR AUC": str(round(np.mean(rf_summary_balanced['holdout_test_pr_auc']), 4)) + " (" + str(round(np.std(rf_summary_balanced['holdout_test_pr_auc']), 4)) + ")",
    #            "Brier": str(round(np.mean(rf_summary_balanced['holdout_test_brier']), 4)) + " (" + str(round(np.std(rf_summary_balanced['holdout_test_brier']), 4)) + ")",
    #            "F2": str(round(np.mean(rf_summary_balanced['holdout_test_f2']), 4)) + " (" + str(round(np.std(rf_summary_balanced['holdout_test_f2']), 4)) + ")"}
    
    # balanced = pd.DataFrame.from_dict(balanced, orient='index', columns=['Random Forest'])
    # rf_results = balanced
    
    # XGB
    # balanced = {"Accuracy": str(round(np.mean(xgb_summary_balanced['holdout_test_accuracy']), 4)) + " (" + str(round(np.std(xgb_summary_balanced['holdout_test_accuracy']), 4)) + ")",
    #            "Recall": str(round(np.mean(xgb_summary_balanced['holdout_test_recall']), 4)) + " (" + str(round(np.std(xgb_summary_balanced['holdout_test_recall']), 4)) + ")",
    #            "Precision": str(round(np.mean(xgb_summary_balanced['holdout_test_precision']), 4)) + " (" + str(round(np.std(xgb_summary_balanced['holdout_test_precision']), 4)) + ")",
    #            "ROC AUC": str(round(np.mean(xgb_summary_balanced['holdout_test_roc_auc']), 4)) + " (" + str(round(np.std(xgb_summary_balanced['holdout_test_roc_auc']), 4)) + ")",
    #            "PR AUC": str(round(np.mean(xgb_summary_balanced['holdout_test_pr_auc']), 4)) + " (" + str(round(np.std(xgb_summary_balanced['holdout_test_pr_auc']), 4)) + ")",
    #            "Brier": str(round(np.mean(xgb_summary_balanced['holdout_test_brier']), 4)) + " (" + str(round(np.std(xgb_summary_balanced['holdout_test_brier']), 4)) + ")",
    #            "F2": str(round(np.mean(xgb_summary_balanced['holdout_test_f2']), 4)) + " (" + str(round(np.std(xgb_summary_balanced['holdout_test_f2']), 4)) + ")"}
    
    # balanced = pd.DataFrame.from_dict(balanced, orient='index', columns=['XGB'])
    # xgb_results = balanced
    
    # results = pd.concat([dt_results, logistic_results], axis=1)
    # results = pd.concat([results, lasso_results], axis=1)
    # results = pd.concat([results, svm_results], axis=1)
    # results = pd.concat([results, rf_results], axis=1)
    # results = pd.concat([results, xgb_results], axis=1)
    # results = results.T
    
    # results = pd.concat([logistic_results, lasso_results], axis=1)
    # results = pd.concat([results, svm_results], axis=1)
    results = results.T
    results.to_csv("Result/Longterm/logistic_results.csv")
    
    