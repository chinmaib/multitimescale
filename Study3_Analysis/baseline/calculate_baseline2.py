"""
Script: calculate_baseline2.py
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

    # Most probable symbols
    prob_sym = []
    acc_list = []

    # Need to calculate the most probable label
    for i in range(0,n):
        # Divide the dataset into training and testing.
        train = np.delete(mat,i,0)
        test  = mat[i,]

        row,col = train.shape
        co = 0
        # We will create an empty pred list, compute most prob symbol
        # at each step and add the symbol to pred
        
        sym,counts = np.unique(train,return_counts=True)
        tsym,tcounts = np.unique(test,return_counts=True)
        # Remove the first element from sym and counts,
        # since the first element is -1 corresponding to NA
        
        # NOTE: Only remove the first element if there are 11 
        # elements in the list. 
        r = sym.shape
        if (r[0] == 11):
            sym = sym[1:]
            counts = counts[1:]
            tsym = tsym[1:]
            tcounts = tcounts[1:]

        #print (sym,counts)
        # Calculate total elements and divide counts/total get a prob distribution
        total = counts.sum()
        prob_counts = counts / total
        #print (prob_counts)
        # Sequence generated from the probability distribution.
        pred = np.random.choice(sym,(len(test),),p=prob_counts) 
        corr = 0
        missing = 0
        
        for j in range(0,len(test)):
            if test[j] == -1:
                missing += 1
                continue

            if test[j] == pred[j]:
                corr += 1
            # Update the confusion matrix.
            cmat[test[j]][pred[j]] += 1
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
    #print (cmat)

main()

