"""
Script : vtc_to_csv_neo.py
Author : Chinmai
Date   : 04/03/2019

This script Extracts VTC Data for ALL the voxels specified in the Neo VOI file.

NOTE: The VOI files are not Cubic. They are as originally defined.
Location: /home/chinmai/src/VOI/Neo_VOI

Description: Script checks if the VTC is present and CSV files are already extracted. 
If not, calls the MATLAB script to extract CSV corresponding to each choice. 
"""

import datetime

# Get Current data and time
now = datetime.datetime.now()

import os
import sys
import shutil
from subprocess import call

#sys.path.append(os.path.abspath('..'))
home = '/home/chinmai/src/UEF_2019'

# Import all functions from utils.py
from utils import *

# MATLAB script
m_path = '/home/chinmai/src/UEF/MATLAB'

Errors = ''
log = 'Running vtc_to_csv_neo.py @ '+now.strftime("%m-%d-%y %H:%M:%S")+'\n'
print log,

line_break='*******************************************************************\n'
print line_break
csv_fold = 'CSV_Neo'
vtc_post = 'Script_MNI.vtc'

def main():

	global home,m_path
	global Errors,log

	log += 'Experiment: UEF\n'
	
	# Set experiment directory
	vtc_dir = os.path.join(home,'VTC_Files')

	# Get a list of all Subjects
	subjects = filter(lambda x:filter_hidden_folders(x,vtc_dir),os.listdir(vtc_dir))
	subjects.sort()

	for sub in subjects:
		print ''
		print '\tSubject : ',sub
		log += '\tSubject: '+sub + '\n'

		# Check if CSV folder is present. If present check if CSV files are present. 
		# 40 csv files are present. in All sub folders. if yes continue
		sub_path = os.path.join(home,'Subjects',sub)

		if os.path.exists(sub_path):
			print '\tCSV_Neo folder exists for ',sub
			continue
		else:
			print '\tCreating CSV_Neo folder for ',sub
			create_CSV_fold(sub_path)

		# Calling MATLAB
		cwd = os.getcwd()
		os.chdir(os.path.join(m_path))
		call(["matlab -nodisplay -r \"export_vtc_to_csv_neo(\'%s\')\"" % (sub)],shell=True);
		os.chdir(cwd)

		
def create_CSV_fold(fold_path):
	"""
	Function creates CSV folder and all the sub-folders corresponding
	to each region.
	"""
	global csv_fold
	os.mkdir(fold_path)
	CSV_fold = os.path.join(fold_path,csv_fold)
	os.mkdir(CSV_fold)
	return


def get_vtc_file(fold_path):
	vtc_file = ''
	vtc_path = os.path.join(fold_path,'Functional')
	files = os.listdir(vtc_path)
	for fl in files:
		if fl.endswith('mm.vtc'):
			vtc_file = fl
	return vtc_file

main()

