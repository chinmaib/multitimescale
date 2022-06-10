"""
Script: label_count.py
Author: Chinmaib

Description: Counts how many class labels and prints out the percentages.
File reads .seq files from the Output directory under Study3_Annotations
"""

import sys
import os

out_dir = '/home/chinmai/src/ASIST/Scripts/Study3_Annotation/Output'
labels = ['ST','NV','SR','OD','TV','PM','RM','TU','RA','IE']

def main():
    global out_dir,labels
    # Read all sequence files in the output folder.

    seq_files = []
    files = os.listdir(out_dir)
    for x in files:
        if x[0] != '.' and x.endswith('.seq'):
            seq_files.append(x)

    print (seq_files)


    for ff in seq_files:
        print ('Filename: ',ff)
        fd = open(os.path.join(out_dir,ff),'r')
        data = fd.read()
        lines = data.split('\n')
        del lines[-1]
        total_elem = len(lines)

        for lab in labels:
            lab_count = lines.count(lab)
            #print (lab,' count : ',lab_count,'\tpercentage: ',(lab_count*100.0)/total_elem)
            percent = lab_count *100.0/total_elem
            print ("%s count : %5d \tpercentage: %f" % (lab,lab_count,percent))

        print ('')
main()

