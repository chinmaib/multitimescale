"""
Script: generate_voi.py
Author: Chinmai

Generates VOI files for all UEF subjects.
"""

import os
from subprocess import call

voi_home = "/home/chinmai/src/UEF_2019/VOI"

voi_script1 = "/home/chinmai/src/UEF/VOI_Scripts/create_neo_voi.py"
voi_script2 = "/home/chinmai/src/UEF/VOI_Scripts/create_cubic_neo_voi.py"

def filter_hidden(x,path):
    """
    x:        is the name of the folder
    path: is the absolute path of the folder

    A filter to remove any files or hidden folders and return a list
    of folders present in path.
    """
    if x[0] != '.' and os.path.isdir(os.path.join(path,x)):
        return True
    else:
        return False

def main():

    # Get all the folder names from the disk location 
    subjects = filter(lambda x:filter_hidden(x,voi_home),os.listdir(voi_home))
    subjects.sort()

    # For each subject folder
    for sub in subjects:
        print sub
        call(["python "+voi_script1+' '+sub],shell=True)
        call(["python "+voi_script2+' '+sub],shell=True)

main()
