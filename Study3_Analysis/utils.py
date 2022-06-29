"""
Script: utils.py
Author: chinmaib
"""
import os
import sys
import numpy as np
import math

def test1():
    x = np.random.randint(0,10,(5,5))
    print (x)

def calculate_MCC (cmat, n):
    """
    Function calculates the Matthew's Correlation Coefficient for
    given confusion matrix cmat and total number of labels n.
    """    
    # True distribution of labels
    t_k = np.sum(cmat,axis=1)
    # Predicted distribution of labels
    p_k = np.sum(cmat,axis=0)
    #print (t_k)
    #print (p_k)
    # Total correctly predicted.
    # Sum of diagonal elements in the confusion matrix
    c = np.trace(cmat)
    print ('Correct c:',c)
    s = cmat.sum()
    s2 = s ** 2
    print ('Total s:',s)
    c_times_s = c * s
    sig_pk_times_tk = 0
    sig_pk2  = 0
    sig_tk2  = 0

    for i in range(0,n):
        temp = t_k[i] * p_k[i]
        sig_tk2  += t_k[i]**2
        sig_pk2  += p_k[i]**2

        sig_pk_times_tk += temp
        #print (temp)

    print ('Sum p_k times t_k:',sig_pk_times_tk)
    print ('s^2:',s2)
    print ('Sum t_k^2:',sig_tk2)
    print ('Sum p_k^2:',sig_pk2)

    MCC = ((c * s) - sig_pk_times_tk)/math.sqrt((s2 - sig_pk2)*(s2 - sig_tk2))
    print ('MCC:', MCC)

