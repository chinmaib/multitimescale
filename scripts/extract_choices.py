"""
Script: extract_choices.py
Description:
	- Extracts user behavioral data from choices folder under Exp_dir
	- This script has been modified w.r.t IGT task in mind.

	Output:
		- NET TOTAL for each subject
		- Block Net Scores
		- Total number of cards seleted from each deck

"""
import datetime

# Get Current data and time
now = datetime.datetime.now()

import os,io
import sys
import shutil
from subprocess import call

# Import functions from utils.py
from utils import *

# Get Parent Directoryi. MRI folder is the home directory.
home = os.path.abspath('..')

choice_path = os.path.join(home,'choices')
exp_path = os.path.join(home,'Experiments')
log_path = os.path.join(home,'Logs/Choice_Extraction')

# Set Errors to empty
Errors = ''

log = 'Running extract_choices.py @ '+now.strftime("%m-%d-%y %H:%M:%S")+'\n'
print log,

line_break='*******************************************************************\n'
print line_break,

log += line_break

def main():
	global home,exp_path,choice_path
	global log,Errors

	#Expr = get_experiments(exp_path)
	Expr = ['IGT']
	#choice_dic = {}
	for exp in Expr:
	
		log += 'Experiment: '+exp+'\n'
		print 'Experiment: ',exp
		# Set experiment directory and choice directory
		exp_dir = os.path.join(exp_path,exp)
		choice_dir = os.path.join(choice_path,exp)

		# Reading Configuration file
		conf_file = os.path.join(exp_dir,'config')
		config = open(conf_file,'r')
		if not config:
			Errors += 'Error: Config file not present in '+exp_dir+'\n'
			print 'Error: Unable to Open Config File in ',exp_dir,line_break
			continue

		param = config.read()
		param_list = param.split('\n')
		labels = param_list[9].split(':')
		labels_list = labels[1].split(',')
		print '\tLabels: ',labels_list
		log += '\tLabels: '+str(labels_list)+'\n'
		subjects = filter(lambda x: filter_hidden_folders(x,choice_dir),os.listdir(choice_dir))

		if len(subjects) == 0:	
			Errors += 'Error: Unable to retrieve subjects from ' +choice_dir+'\n'
			print Errors,
			continue
	
		# Sort the subjects alphabeticaly
		subjects.sort()

		for sub in subjects:

			write_path = os.path.join(exp_dir,sub,'Behavioral')				
			fold_path  = os.path.join(choice_dir,sub)
			# 6st Check if Subject folder is present in exp_dir.
			if not os.path.isdir(os.path.join(exp_dir,sub)):
					os.mkdir(os.path.join(exp_dir,sub))
					os.mkdir(write_path)
				#Errors += 'Error: '+sub+ ' Neruoimaging data not yet Processed.'+'\n'
				#Errors += 'Recommended: Run data_organization.py first for '+sub+'\n'
				#print 'Error: ',sub,' Neuroimaging data not yet processed'	
				#print 'Recommended: Run data_organization.py first for ',sub
				#continue
		
			log+= '\tSUBJECT : '+sub+'\n'
			print '\tSUBJECT : ',sub

			# Every subject folder has 2 files - .edat and .txt
			# We will assume that it is always the case that 
			# .txt file is the CHOICE file.

			files = filter(filter_hidden,os.listdir(fold_path))
			choice_file = ''

			for fl in files:
				if fl.endswith('.txt'):
					choice_file = os.path.join(fold_path,fl)
					break
		
			if choice_file == '':
				Errors += 'Error: Choice file not present for '+sub+'\n'
				print Errors
				continue

			fd = open(choice_file,'r')
			if fd == '':
				Errors += 'Error: Unable to open Choice file for '+sub+'\n'
				print Errors
				continue
		
			# Read contents of the choice file.
			choice_file_content = fd.read()
			fd.close()
		
			# Split the file into lines
			lines = choice_file_content.decode('utf-16').split('\n')
			#lines = choice_file_content.split('\n')

			# Get Choices by parsing lines list.
			choice_dic = get_choice_list(exp,lines,labels_list)
			#select_list,Accuracy = get_select_accuracy(choice_list)	
		
			# Now that we have choices extracted out, lets write it to file.
			write_to_behavior(sub,exp,choice_dic,write_path)
			log += '\t'+sub+' processed successfully!\n'
			print '\t',sub,' processed successfully!\n'


def get_choice_list(exp,lines,labels_list):
	choice_dic = {}	
	for label in labels_list:
		label = label.strip()
		print '\tLabel: ',label
		choice_list =[]
		for i in range(0,len(lines)):
			# Get rid of beginning & trailing whitespaces
			lines[i] = lines[i].strip()
			if (label+':') in lines[i]:
				temp = lines[i].split(':')
				# No choice made
				if len(temp[1]) == 0:
					choice_list.append('NA')
				else:
					choice_list.append(temp[1].strip())
		choice_dic[label] = choice_list
	return choice_dic


def	write_to_behavior(sub,exp,choice_dic,write_path):

	# Check if Behavioral folder exists.
	if not os.path.isdir(write_path):
		os.mkdir(write_path)
	
	# Different experiments have different file transformations.
	# For the transformed files, _transformed will be appended.
	
	for key,val in choice_dic.iteritems(): 
		# Transformation variable set to 0
		transform = 0
		transformed_choice = []

		# Change {1,2} -> -1 and {3,4} -> 1 => Choose.RESP.transformed		
		if key == 'Choose.RESP' and exp == 'IGT':
			transform = 1
			for v in val:
				if v == '3' or v == '4':
					transformed_choice.append(1)
				elif v == '1' or v == '2':
					transformed_choice.append(-1)
				else:
					transformed_choice.append(0)	
 	
		# File descriptors
		key_fd = open(os.path.join(write_path,sub+'_'+key)+'.txt','w')
		for v in val:
			key_fd.write(str(v)+'\n')
		key_fd.close()
			
		if transform == 1:
			tra_key_fd = open(os.path.join(write_path,sub+'_'+key)+'_transformed.txt','w')
			for v in transformed_choice:
				tra_key_fd.write(str(v)+'\n')
			tra_key_fd.close()
	
	return


main()
# If there are any Errors present, then write them to the error file
if Errors == '':
	Errors ='NO ERRORS WHILE PROCESSING!\n'

log += line_break + Errors


err = open(os.path.join(log_path,'Extraction_log'+now.strftime("%m%d%y_%H%M%S")),'w')
err.write(log)
err.close()

