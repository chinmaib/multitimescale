"""
Script: data_organization.py for 2018 Neuroimaging Data.

Description : 
	- Reads raw data from the SYNC folder.
	- Extracts the experiment folders and reads in experiment parameters
	- Extracts the right Functional/Anatomical folders using exp parameters.
	- Copies and renames IMA files to exp folder & renames them to DCM
	- Pepares the JavaScript parameters to be run using BrainVoyager.
	- Cleans Up the SYNC folder.

"""

import datetime
# Get Current data and time
now = datetime.datetime.now()

import os
import sys
import shutil
from subprocess import call

# All the script realted functions are defined in utils.py
from utils import *

# Current Scripts Directory
home = os.path.abspath('..')
exp_path = os.path.join(home,'Experiments')
path	 = os.path.join(home,'SYNC') 
log_path = os.path.join(home,'Logs/Organization')

# We know the Number of Anatomical Slices is 192 for all experiments.
# We will use this to obtain the VMR folder.
anat_slices = 192

# Set Errors to empty
Errors = ''

log = 'Running data_organization.py at '+now.strftime("%m-%d-%y %H:%M:%S")+'\n'
print'Running data_organization.py at '+now.strftime("%m-%d-%y %H:%M:%S")
print 'WARNING: All data in SYNC folder will be erased.'

line_break='*******************************************************************\n'
print line_break

def main():
	global log,Errors,line_break
	global path,home,log_path,exp_path

	# Get a list of all the experiments.
	Expr = get_experiments(exp_path)
	
	# Get a list of all subjects & filter out files starting with '.'
	subjects = filter(lambda x: filter_hidden_folders(x,path) ,os.listdir(path))
	# Sort the subjects alphabeticaly
	subjects.sort()

	# CHECK 1: Check all the folders in the SYNC are indeed subject folders.
	# Subject folders have the convention Number_Date_Initials (01_20180506_CB)

	subjects = check_SYNC_folder_contents(subjects)

	log += line_break + 'Processing Subjects:\n'
	print 'Processing Subjects:'

	count = 0
	for sub  in subjects:
		
		log += '\tSUBJECT : '+sub+'\n'
		print '\tSUBJECT : ',sub
		
		# There is ONLY 1 sub-folder starting with name REIMANN_XX_XX_XX
		temp_path = os.path.join(path,sub)
		temp_fold = os.listdir(temp_path)
		sub_path = os.path.join(temp_path,temp_fold[0])
	
		# Get a list of all the folders under the subject.
		folds = filter (lambda x: filter_hidden_folders(x,sub_path), os.listdir(sub_path))

		if len(folds) == 0:
			log += sub+' folder empty or already processed.'+'\n\n'
			print sub,' folder empty or already processed.\n'
			continue

		# Empty list to store processed folders
		processed = []

		# Get the VMR Folder. We know the number of anatomical slices.	
		vmr = get_vmr_folder(sub_path,anat_slices) 

		if	vmr == '':
			Errors += 'Error: Unable to find VMR for '+sub+'\n\n'
			print 'Error: Unable to find VMR for ',sub,'\n'
			continue

		print '\tVMR folder found: ',vmr
		log += '\tVMR folder found: '+vmr+'\n'

		processed.append(vmr)

		##############TESTING##############
				
		# For each folder in subject folder, 
		for fold in folds:
			# Skip VMR folder.
			if fold == vmr:
				continue
			
	
			if fold not in Expr:
				Errors += fold + ': Experiment does not exist!\n'
				print fold,': Experiment does not exist!\n'
				continue 
		
			print '\tEXPERIMENT: ',fold
			log += '\tEXPERIMENT: '+ fold + '\n'

			fold_path = os.path.join(sub_path,fold)

			# Get the main experiment directory under home
			exp_dir = os.path.join(exp_path,fold)

			# List all subjects already processed in Exp Folder
			sub_in_exp = os.listdir(exp_dir)
	
			if sub in sub_in_exp:
				# Subject folder already exists, continue to next.
				print sub ,' folder already Synced for ',fold
				log += sub +' folder already Synced for '+fold+'\n'
				processed.append(fold)		
				continue

			# create folder and, define Func and Anat paths.
			x = os.path.join(exp_dir,sub)
			os.mkdir(x)
			x_behv = os.path.join(x,'Behavioral')
			os.mkdir(x_behv)
			# These folder get created while copying files
			x_func = os.path.join(x,'Functional')
			x_anat = os.path.join(x,'Anatomical')
			
			# Read from the configuration file in exp_dir
			conf_file = os.path.join(exp_dir,'config')	   
		
			if not os.path.exists(conf_file):
				Errors += 'Error: Unable to find config file for '+expr+'\n'
				continue
		
			# Get no of functional volumes from config file
			vol = get_vol_from_config(conf_file)	
	
			files = filter(filter_hidden,os.listdir(fold_path))

			if int(vol) == len(files):
				fmr = fold
			else:
				Errors += 'Error: Unable to find FMR folder for '+sub+' for '+fold+'\n'
				shutil.remtree(x)
				continue

			# Once I get FMR and VMR remove all other directories
		
			print '\tfmr folder found for ', fmr 
			log += '\tfmr folder found for '+ fmr +'\n'
		
			# Copy the contents of the appropriate folders to anatomical and 
			# functional data folders.
			shutil.copytree(os.path.join(sub_path,fmr),x_func) 
			shutil.copytree(os.path.join(sub_path,vmr),x_anat)
		
			print '\tFMR and VMR files copied successfully.' 
			log += '\tFMR and VMR files copied successfully.\n'
			
			# Rename the files from IMA to DCM
			rename_IMA_to_DCM(x_func)
			rename_IMA_to_DCM(x_anat)

			# Subject specific Javascript file to exp folder
			j_script = os.path.join(x,sub+'.js')
		
			# Read in the files in func and anat folders, sort them
			# To obtain the source (first) filename.
	
			anat_files = filter(filter_dcm,os.listdir(x_anat))
			anat_files.sort()		
		
			func_files = filter(filter_dcm,os.listdir(x_func))
			func_files.sort()
	   
			# Let's construct the list of variable declarations for the JavaScript

			# Adding the 1st line in pre-processing script.
			#vari = '\nSubjects['+str(count)+'] = new Subject("'+sub+'",\n' 
			vari ='"'+x_anat+'/",\n'
			vari +='"'+x_func+'/",\n'
			vari +='"'+anat_files[0]+'",\n'
			vari +='"'+func_files[0]+'");\n'

			fw = open(j_script,'w')
			fw.write(vari)
			fw.close()
		
			# Add Subject to Successfully processed.
			processed.append(fold)

		count = count + 1

		log += 'Successfully Processed:'+sub+'\n'
		print 'Successfully Processed:',sub

		for i in range(1,len(processed)+1):
			log += str(i) + ': '+ processed[i-1] +'\n' 
			print i,': ',processed[i-1]
		cleanup_sync(processed,sub_path)
		print line_break
		log += line_break

def cleanup_sync(processed,sub_path):

	global path,line_break,log

	print 'Cleaning Up SYNC folder'
	log += 'Cleaning Up SYNC folder\n'

	for fold in processed:
		shutil.rmtree(os.path.join(sub_path,fold))

	fl = os.listdir(sub_path)
	if len(fl) == 0:
		shutil.rmtree(sub_path)
	return

def get_vmr_folder(path,num):
	"""
	Input:	
	  	path : Absolute path of the subject folder.
	 	 num  : No. of anatomical slices.
	We know the VMR folders contain T1_MPRAGE or T1-MPRAGE 
	Output:
		Function return the name of VMR folder.
	"""	
	global log
	correct_fold=''
	folds = filter(lambda x:filter_hidden_folders(x,path),os.listdir(path))
	for fo in folds:
		files = filter(filter_dcm,os.listdir(os.path.join(path,fo)))

		#if len(files) == int(num) and 'T1' in fo and 'MPRAGE' in fo :
		if len(files) == int(num):
			correct_fold = fo
			# If Motion Corrected Data set is found then Keep it.
			if "MOCO" in fo:
				log +='Motion Corrected Data Set Present.\n'
				print 'Motion Corrected Data Set Present.'
				break
	return correct_fold

def check_SYNC_folder_contents(subjects):
	""" Functions goes through all the folders in SYNC and
	makes sure that all the folders are subject folders with appropriate
	sub-folder structure and naming convention.
	"""

	global log,line_break,path
	log += 'Checking SYNC folder contents:'
	print 'Checking SYNC folder contents:'
	remove_list = []	# List of folder indices to be removed.

	for i in range(0,len(subjects)):
		fmt = 0		# Format flag

		s_list = subjects[i].split('_')

		# Check is folder name in SYNC conforms to convention
		if len(s_list) == 3:
			if(s_list[0].isdigit() and s_list[1].isdigit() and s_list[2].isalpha()):
				# Now check sub-folder structure.
				sub_folds = os.listdir(os.path.join(path,subjects[i]))
				if len(sub_folds) == 1:
					sub_sub_folds = os.listdir(os.path.join(path,subjects[i],sub_folds[0]))
					if len(sub_sub_folds) != 0:
						fmt = 1

		# If it doesn't add to remove_list
		if fmt == 0:
			log += '\t'+subjects[i]+ " doesn't conform to SYNC folder convention\n"
			print '\t',subjects[i]," doesn't conform to SYNC folder convention"
			remove_list.append(i)

	if len(remove_list) == 0:
		log += 'All folders conform to SYNC convention\n'+line_break
		print 'All folders conform to SYNC convention'
		print line_break
		return subjects
	count = 0		
	for i in remove_list:
		del subjects[i-count]
		count = count +1
		# We have to do -count because everytime you delete an item
		# list size reduces by 1.
	print line_break
	return subjects

main()

# If there are any Errors present, then write them to the error file
if Errors == '':
	log += 'NO ERRORS WHILE PROCESSING!\n'
	Errors ='NO ERRORS WHILE PROCESSING!\n'
else:
	print Errors
	log += line_break + Errors

err = open(os.path.join(log_path,'Organization_log'+now.strftime("%m%d%y_%H%M%S")),'w')
err.write(log)
err.close()

