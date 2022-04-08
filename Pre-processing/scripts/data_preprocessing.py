# Script : data_preprocessing.py
# This is a python	script goes throught the folders in /home/MRI/SYNC.

import datetime

# Get Current data and time
now = datetime.datetime.now()

import os
import sys
import shutil
from subprocess import call

# Import functions from utils.py
from utils import *

# Current Scripts Directory
home = os.path.abspath('..')
exp_path = os.path.join(home,'Experiments')
template_path = os.path.join(home,'BV_scripts/allsteps_single_subject_template.js')
log_path = os.path.join(home,'Logs/Preprocessing')

# Set Errors to empty
Errors = ''

log = 'Running data_preprocessing.py at '+now.strftime("%m-%d-%y %H:%M:%S")+'\n'
print log,

line_break='*******************************************************************\n'
print line_break,

def main():
	global log,Errors,line_break
	global home,log_path,template_path
	
	# Get a list of experiments.
	Expr = get_experiments(exp_path)
	
	# Open and Read in the BrainVoyager script template.
	template_fd = open(template_path,'r')
	if not template_fd:
		Errors += 'Error: Unable to read BV template.\n'
		print 'Error: Unable to read BV template.\n'
		return

	template_data = template_fd.read()	
	template_fd.close()

	# Template JS file read in successfully. 
	log += 'BrainVoyager JavaScript template read in successfully!\n'
	print 'BrainVoyager JavaScript template read in successfully!' 

	for exp in Expr:
		log += 'Experiment :'+exp+'\n'
		print 'Experiment :',exp

		exp_dir = os.path.join(exp_path,exp)
		bv_script_path = os.path.join(home,'BV_scripts/Runs',exp)

		# Reading configuration file
		conf_file = os.path.join(exp_dir,'config')	   
		config = open(conf_file,'r')

		if not config:
			Errors += 'Error: Config file not present in '+exp_dir+'\n'
			print 'Error: Unable to Open Config File in ',exp_dir,line_break
			continue
	
		param = config.read()		 
		param_list = param.split('\n')
		subjects = param_list[1].split(':')[1]
		volumes  = param_list[2].split(':')[1]
		f_slices = param_list[3].split(':')[1]
		matx	 = param_list[4].split(':')[1]
		maty	 = param_list[5].split(':')[1]
		slicex	 = param_list[6].split(':')[1]
		slicey	 = param_list[7].split(':')[1]
		a_slices = param_list[8].split(':')[1]
	
		config.close()

		log += 'Config file read successfully for '+exp+'\n'
		print 'Config file read successfully for ',exp

		# Common Parameters of the Experiment go at the beginning of JS file.

		vari = 'var novols = '+volumes+'\n'
		vari = vari + 'var noslices =	'+f_slices+'\n'
		vari = vari + 'var anat_slices= '+a_slices+'\n'
		vari = vari + 'var matrixresX = '+matx+'\n'
		vari = vari + 'var matrixresY = '+maty+'\n'
		vari = vari + 'var sliceresX  = '+slicex+'\n'
		vari = vari + 'var sliceresY  = '+slicey+'\n'

		vari += 'var Subjects = new Array();\n'

		#################################### SUBJECTS #################################

		# Get a list of all subjects & filter out files starting with '.'
		subjects = filter(lambda x: filter_hidden_folders(x,exp_dir) ,os.listdir(exp_dir))
	
		if len(subjects) == 0:
			Errors += 'Error: Unable to retrieve subjects from ' +exp_dir+'\n'
			print 'Error: Unable to retrieve subjects from ',exp_dir,'\n',line_break
			continue

		# Sort the subjects alphabeticaly
		subjects.sort()

		log += line_break + 'Processing Subjects:\n'
		print 'Processing Subjects:'
	
		js_data = ''
		count = 0

		for sub in subjects:
		
			log += '\t'+str(count+1)+'.SUBJECT : '+sub+'\n'
			print '\t',count+1,'.SUBJECT : ',sub

			fold_path = os.path.join(exp_dir,sub)
		
			# Check if Subject already processed and archived.
			f_path = os.path.join(fold_path,'Functional')		
			if not dcm_present(f_path) or vtc_present(f_path):
				log += '\t'+sub + ' folder already processed & archived!\n'
				print '\t',sub, ' folder already processed & archived!'
				continue 

			# Check if JS exists. If Yes, open and read it in.
			js_path = os.path.join(fold_path,sub+'.js')
		
			if not os.path.exists(js_path):
				Errors += 'Error: Unable to locate JS parameters for '+sub+'\n'
				print 'Error: Unable to locate JS parameters for ',sub
				continue
			
			js_script = open (js_path,'r')
			jdata = js_script.read()
			js_script.close() 
			
			# Test if JS file is in new or old format.

			jlines = jdata.split('\n')
			
			if len(jlines) == 7: 
				log+= '\tOld format JS file. Converting to new format\n' 
				print '\tOld format JS file. Converting JS file to new format'
				del jlines[0:2]

			# Check if anatomical and functional folders exist
			data_apath = jlines[0][1:-2]
			data_fpath = jlines[1][1:-2]

			if (not os.path.isdir(data_apath)) or (not os.path.isdir(data_fpath)):
				log += '\tFunc/Anat folder path doesn\'t match. Changing path to relative\n'
				print '\tFunc/Anat folder path doesn\'t match. Changing path to relative\n'
				
				# if they don't exist try using the relative path and test again
				data_apath = os.path.join(fold_path,'Anatomical')
				data_fpath = os.path.join(fold_path,'Functional')
				if (not os.path.isdir(data_apath)) or (not os.path.isdir(data_fpath)):
					Errors += 'Error: Functional/Anatomical folder missing for '+sub+'\n'
					print 'Error: Functional/Anatomical folder missing for ',sub
					continue
				# if relative path works, then change the entry in jlines list
				jlines[0] = '"'+data_apath+'/",'
				jlines[1] = '"'+data_fpath+'/",'
			
			# Check if the source(1st) files are present.
			data_asource = os.path.join(data_apath,jlines[2][1:-2])
			data_fsource = os.path.join(data_fpath,jlines[3][1:-3])

			if (not os.path.exists(data_asource)) or (not os.path.exists(data_fsource)):
				
				log += '\tFunc/Anat source filename doesn\'t match. Changing filename to relative\n'
				print '\tFunc/Anat source filename doesn\'t match. Changing filename to relative\n'
				
				anat_files = filter(filter_hidden,os.listdir(data_apath))
				anat_files.sort()
				data_asource = os.path.join(data_apath,anat_files[0])	
				func_files = filter(filter_hidden,os.listdir(data_fpath))
				func_files.sort()
				data_fsource = os.path.join(data_fpath,func_files[0])	
				if (not os.path.exists(data_asource)) or (not os.path.exists(data_fsource)):
					Errors += 'Error: Functional/Anatomical source file missing for '+sub+'\n'
					print 'Error: Functional/Anatomical source file missing for ',sub
					continue
				# if relative path works, then change the entry in jlines list
				jlines[2] = '"'+anat_files[0]+'",'
				jlines[3] = '"'+func_files[0]+'");'
				
			# Check if the anatomical filename is in the right format.
			form = check_anat_format(data_asource)
			if form == 'old':
				print '\tAnatomical filenames are in old format. Renaming files to new format.'
				log += '\tAnatomical filenames are in old format. Renaming files to new format.\n'
				anat_files = filter(filter_hidden,os.listdir(data_apath))
				# List and rename the files to new format.
				rename_anat_files(anat_files,data_apath)
				# After renaming, list the files and set 1st file as data_asource
				anat_files = filter(filter_hidden,os.listdir(data_apath))
				anat_files.sort()
				jlines[2] = '"'+anat_files[0]+'",'
				
			jdata = '\n'.join(jlines)

			data = '\nSubjects['+str(count)+'] = new Subject("'+sub+'",\n'
			data += jdata
			log += '\t'+sub+' JS file read in and successfully processed!\n'		
			print '\t',sub,' JS file read in and successfully processed!'		
			js_data += data
			count = count + 1		

		if js_data != '':
			script = os.path.join(bv_script_path,'Run_'+exp+'_'+now.strftime("%y%m%d_%H%M%S")+'.js')
			bv_fd = open(script,'w')
			bv_fd.write(vari+js_data+template_data)
			bv_fd.close()

		log += line_break
		print line_break

main()

# If there are any Errors present, then write them to the error file
if Errors == '':
	log += 'NO ERRORS WHILE PROCESSING!\n'
	Errors ='NO ERRORS WHILE PROCESSING!\n'
else:
	print Errors
	log += line_break + Errors

err = open(os.path.join(log_path,'Preprocessing_log'+now.strftime("%m%d%y_%H%M%S")),'w')
err.write(log)
err.close()

