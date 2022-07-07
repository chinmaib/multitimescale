"""
Script: calculate_baseline3.py
Author: Chinmaib

Description: Read in CSV file and calculate baseline measures.
Baseline1: Predicting the most common label as output everytime.

Validation: LOOCV (Leave one subject out validation)
Total: 96 data points from 48 participants.

Baseline2 : Here we emperically calculate the distribution of
labels in the training data. We sample the output sequence from the
distribution calculated from training data and use that as our predicted
sequence.
"""

import sys

import os
import json
import numpy as np
import math

from sklearn.metrics import matthews_corrcoef

from utils import *

np.random.seed(1230)

# Declare location of files and folders.
data_dir ="/home/chinmaib/tomcat/annotations"
num_labels = 10
cmat = np.zeros((num_labels,num_labels))

def main():
    # Open metadata file for reading.
    global data_dir, cmat, num_labels
    csv_file = sys.argv[1]
    csv_file_path = os.path.join(data_dir,csv_file)

    mat = np.loadtxt(csv_file_path, dtype=int, delimiter=',')
    n,cols = (mat.shape)

    acc_list = []

    # Need to calculate the most probable label
    for i in range(0,n):
        # Most probable symbols
        prob_sym = []
        # Divide the dataset into training and testing.
        train = np.delete(mat,i,0)
        test  = mat[i,]
        row,col = train.shape

        # From the training dataset, calculate the most probable label
        # 

        for j in range(0,col):
            temp = train[:,j]
            # Obtain the frequence of all the labels.
            sm,co = np.unique(temp,return_counts=True)
            #print (sm,co)
            
            # Check if -1 is present in the labels.
            if -1 in sm:
                # If -1 is present, it'll always be the first symbol
                sm = sm[1:]
                co = co[1:]
                # If -1 is the only class label available.
                # This will be the case in the longest sequence.
                if sm.shape[0] == 0:
                    # Here we need to calculate the most probable symbol
                    # and add it as the output.
                    sym,counts = np.unique(train,return_counts=True)
                    sym = sym[1:]
                    counts = counts[1:]
                    m_ind = counts.argmax()
                    prob_sym.append(sym[max_ind])
                    continue

            max_ind = co.argmax()
            prob_sym.append(sm[max_ind])
            #prob_sym.append(1)
        corr = 0
        missing = 0
        # Most probable symbol - psym
        for j in range(0,len(test)):
            if test[j] == -1:
                missing += 1
                continue

            if test[j] == prob_sym[j]:
                corr += 1
            # Update the confusion matrix.
            cmat[test[j]][prob_sym[j]] += 1
        #print (corr,missing)
        
        acc = corr / (len(test) - missing)
        acc_list.append(acc)
        #print ('Accuracy: ',acc)
    
    calculate_MCC(cmat,num_labels)
    acc_array = np.asarray(acc_list)
    #print (min(acc_list))
    #print (max(acc_list))
    mean_acc = acc_array.mean()
    #print (len(acc_list))
    std_acc = acc_array.std()
    std_err = std_acc/math.sqrt(len(acc_list))
    print ('Mean Accuracy: ',mean_acc,'+-',std_err)
    np.set_printoptions(precision=4,suppress=True)
    print (cmat)


main()

