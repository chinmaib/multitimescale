"""
Script : vtc_to_csv_cubic_neo.py
Author : Chinmai

This script Extracts VTC Data for ALL the voxels specified in VOI file.

NOTE: The VOI files are Cubic. They are not as originally defined.
fMRI resolution is 2x2x2. ALternative voxels are considered.
Location: BV_scripts/VOI/Cubic_VOI_Neo

Description: Script checks if the VTC is present and CSV files are already extracted. 
If not, calls the MATLAB script to extract CSV corresponding to each choice. 

We have 4 different experiments and each of them have their own timings.
"""
import datetime

# Get Current data and time
now = datetime.datetime.now()

import os
import sys
import shutil
from subprocess import call

# Import all functions from utils.py
from utils import *

home = os.path.abspath('..')
exp_path = os.path.join(home,'Experiments')
log_path = os.path.join(home,'Logs/CSV_Extraction')

# MATLAB script
m_path = os.path.join(home,'MATLAB')

# COLLECTION task no. of CSV files in 40
#csv_num = 40

Errors = ''

log = 'Running vtc_to_csv.py @ '+now.strftime("%m-%d-%y %H:%M:%S")+'\n'
print log,

line_break='*******************************************************************\n'
print line_break

def main():

	global home,m_path,exp_path
	global Errors,log

	Expr = get_experiments(exp_path)
	Expr.sort()
	#Expr = ['IGT']
	for exp in Expr:

		log += 'Experiment: '+exp+'\n'
		print 'Experiment: ',exp
		# Set experiment directory and choice directory
		exp_dir = os.path.join(exp_path,exp)


		# Get a list of all Subjects
		subjects = filter(lambda x:filter_hidden_folders(x,exp_dir),os.listdir(exp_dir))
		subjects.sort()
		
		# Reading Configuration file
		conf_file = os.path.join(exp_dir,'config')
		config = open(conf_file,'r')
		if not config:
			Errors += 'Error: Config file not present in '+exp_dir+'\n'
			print 'Error: Unable to Open Config File in ',exp_dir,line_break
			continue

		param = config.read()
		param_list = param.split('\n')
		# No of functional volumes is 3rd line
		num_vol = int(param_list[2].split(':')[1])
	
		# Temporal resolution is the last line,12
		temp_res = int(param_list[11].split(':')[1])

		phases = param_list[10].split(':')
		phases_list = phases[1].split(',')
		print '\tPhases: ',phases_list
		
		# No of choices will be the No. of CSV files output. Line 13
		csv_num = int(param_list[12].split(':')[1])

		# Brodmann Areas
		BA = param_list[13].split(':')
		BA_list = BA[1].split(',')
		print '\tBrodman Areas:',BA_list

		for sub in subjects:

			print '\tSubject : ',sub
			log += '\tSubject: '+sub + '\n'

			sub_path = os.path.join(exp_dir,sub)
			sub_func_path = os.path.join(sub_path,'Functional')
		
			# Check if VTC is present and DCM is not present
			# This mean data archiving is complete. If not continue
			if not vtc_present(sub_func_path) or dcm_present(sub_func_path):
				Errors += 'Error: Data pre-processing not yet complete for '+sub+'\n'
				print 'Error: Data pre-processing not yet complete for ',sub
				continue

			# Check if CSV folder is present. If present check if all the 
			# 40 csv files are present. in All sub folders. if yes continue
			sub_csv_path = os.path.join(sub_path,'CSV_Cubic_Neo')

			if os.path.exists(sub_csv_path):
				print '\tCSV_Cubic_Neo folder exists for ',sub
				# CSV folder exists. Now check if all files are present
				if check_CSV_files(sub_csv_path,csv_num,BA_list):
					log += '\t'+sub +' CSV files already extracted.'+'\n'
					print '\t',sub,' CSV files already extracted.' 
					continue
			else:
				print '\tCreating CSV_Cubic_Neo folder for ',sub
				create_CSV_fold(sub_path,BA_list)

			# Calling MATLAB
			cwd = os.getcwd()
			os.chdir(os.path.join(m_path,exp))
			call(["matlab -nodisplay -r \"export_vtc_to_csv_cubic_neo(\'%s\',\'%s\')\"" % (sub,exp)],shell=True);
			os.chdir(cwd)
			if check_CSV_files(sub_csv_path,csv_num,BA_list):
				log += sub + 'successfully Processed!'+'\n'
				print sub, ' successfully Processed!'
			else:
				Errors += 'MATLAB Error! '+sub+' not processed.'+'\n'
				print 'MATLAB Error! ',sub,' not processed.' 
			 #Delete Folders??

def create_CSV_fold(fold_path,BA_list):
	"""
	Function creates CSV_Cubic_Neo folder and all the sub-folders corresponding
	to each region.
	"""
	CSV_fold = os.path.join(fold_path,'CSV_Cubic_Neo')
	os.mkdir(CSV_fold)
	all_fold = os.path.join(CSV_fold,'All')
	os.mkdir(all_fold)
	for ba in BA_list:
		ba = ba.strip()
		fold = os.path.join(CSV_fold,ba)
		os.mkdir(fold)

	return

def check_CSV_files(path,csv_num,BA_list):
	"""
	Function checks if the CSV_Cubic_Neo folder has exactly 6 sub folders and
	in of these sub-folders have csv_num files exactly
	"""
	# get all 5 sub folders
	# COLLECTION experiment has 5 sub regions.	
	#global csv_num
	folders = filter(lambda x:filter_hidden_folders(x,path),os.listdir(path))
	# folders => len(BA_list) + 1 to include All folder
	if len(folders) != len(BA_list)+1:
		return 0

	for fold in folders:
		file_path = os.path.join(path,fold)
		files = filter(filter_hidden,os.listdir(file_path))
		if len(files) != csv_num:
			return 0
	return 1		

def get_vtc_file(fold_path):
	vtc_file = ''
	vtc_path = os.path.join(fold_path,'Functional')
	files = os.listdir(vtc_path)
	for fl in files:
		if fl.endswith('mm.vtc'):
			vtc_file = fl
	return vtc_file

main()

# If there are any Errors present, then write them to the error file

if Errors == '':
	log += 'NO ERRORS WHILE PROCESSING!\n'
	Errors +='NO ERRORS WHILE PROCESSING!\n'
else:
	print Errors
	log += line_break + Errors

#err = open(os.path.join(log_path,'MATLAB_extraction_log'+now.strftime("%m%d%y_%H%M%S")),'w')
#err.write(log)
#err.close()

