"""
Script: data_archiving.py
Description:
	- After the BrainVoyager script completes running, archive the raw DCM files
"""
import datetime

# Get Current data and time
now = datetime.datetime.now()

import os
import sys
import shutil
from subprocess import call

# Import functions from utils.py
from utils import *

# Get Parent Directory
home = os.path.abspath('..')
exp_path = os.path.join(home,'Experiments')
log_path = os.path.join(home,'Logs/Archiving')

# Set Errors to empty
Errors = ''

log = 'Running data_archiving.py at '+now.strftime("%m-%d-%y %H:%M:%S")+'\n'
print log,

line_break='*******************************************************************\n'
print line_break,

def main():
	global exp_dir,arch_path,home
	global log,Errors

	# Get a list of experiments.
	Expr = get_experiments(exp_path)

	for exp in Expr:

		log += 'EXPERIMENT : '+exp+'\n'
		print 'EXPERIMENT : ',exp

		exp_dir = os.path.join(exp_path,exp)
		arch_path = os.path.join(home,'Archive',exp)

		subjects = filter(lambda x: filter_hidden_folders(x,exp_dir) ,os.listdir(exp_dir))

		if len(subjects) == 0:
			Errors += 'Error: Unable to retrieve subjects from ' +exp_dir+'\n'
			print 'Error: Unable to retrieve subjects from ',exp_dir
			continue

		# Sort the subjects alphabeticaly
		subjects.sort()

		log += line_break + 'Processing Subjects:\n'
		print 'Processing Subjects:'

		for sub in subjects:

			log += '\tSUBJECT : '+sub+'\n'
			print '\tSUBJECT : ',sub

			fold_path = os.path.join(exp_dir,sub)
			f_path = os.path.join(fold_path,'Functional')

			if not fmr_present(f_path):
	
				if not dcm_present(f_path):
					log +='\t'+ sub + ' folder already archived!\n'
					print '\t',sub, ' folder already archived!'
					continue
				else:
					log +='\t'+ sub + ' folder not yet processed!\n'
					print '\t',sub, ' folder not yet processed!'
					continue
			if not check_anat_file(sub,fold_path) or not check_func_files(sub,fold_path):
				Errors += 'Error:'+sub+' not yet processed.\n'
				print 'Error: Files missing for ',sub
				continue
		
			print "\tArchiving Files:"

			os.chdir(fold_path)
		
			f_path = os.path.join(fold_path,'Functional')
			f_tar_files = filter(archive_functional,os.listdir(f_path))

			for i in range(0,len(f_tar_files)):
				f_tar_files[i] = os.path.join('Functional',f_tar_files[i])

			a_path = os.path.join(fold_path,'Anatomical')
			a_tar_files = filter(archive_anatomical,os.listdir(a_path))

			for i in range(0,len(a_tar_files)):
				a_tar_files[i] = os.path.join('Anatomical',a_tar_files[i])
		
			call(['tar','-czf',sub+'.tar.gz']+f_tar_files+a_tar_files)
		
			log += '\tArchive Successfull. Deleting Files'	
			print "\tArchive Successfull. Deleting Files:"

			for fl in f_tar_files:
				os.remove(fl)

			for fl in a_tar_files:
				os.remove(fl)
		
			shutil.move(sub+'.tar.gz',arch_path)

			print '\tData successfully archived for ',sub,'\n'
			log += '\tData successfully archived for '+sub+'\n'
		print line_break
		log += line_break

def archive_anatomical(fname):
	"""
	Archive all files except for ones ending with .trf and .vmr
	"""	
	if fname.endswith('txt') or fname.endswith('v16') or fname.endswith('pos') \
	or fname.endswith('dcm'):
		return True
	
	return False			

def archive_functional(fname):
	"""
	Archive all files except for VTC files.
	"""
	if fname.endswith('txt') or fname.endswith('amr') \
	or fname.endswith('trf') or fname.endswith('fmr') or fname.endswith('pos'):
		return True
	
	return False			
				
def check_anat_file(sub,path):

	global Errors
	a_path = os.path.join(path,'Anatomical')
	
	anat_file_list = ['sorted_file_list.txt',
					 sub+'_Script_BrainMask.vmr',
					 sub+'_Script_IIHC_ISO_MNI.vmr',
					 sub+'_Script_IIHC_ISO_TO_ICBM452_a12.trf',
					 sub+'_Script_IIHC_ISO_TO_MNI_a12.trf',	
					 sub+'_Script_IIHC_ISO_TO_MNIColin27_a12.trf',
					 sub+'_Script_IIHC_ISO.vmr',
					 sub+'_Script_IIHC.v16',
					 sub+'_Script_IIHC.vmr',
					 sub+'_Script.v16',
					 sub+'_Script.vmr',
					 sub+'_Script_VMR.pos']
	for fl in anat_file_list:
		if not os.path.exists(os.path.join(a_path,fl)):
			missing = 1
			Errors += 'Error: '+fl+'  missing for '+sub+'\n'
			print fl,' missing for ',sub
			return False
	print "\tAll Anatomical Files Present!!"
	return True

def check_func_files(sub,path):

	global Errors
	f_path = os.path.join(path,'Functional')
	
	# Missng flag
	missing = 0

	func_file_list = ['DM-Fourier.txt',
					'sorted_file_list.txt',
					sub+'_Script_firstvol_as_anat.amr',
					sub+'_Script_firstvol.fmr',
					sub+'_Script.fmr',
					sub+'_Script_FMR.pos',
					sub+'_Script_MNI_SD3DVSS6.00mm.vtc',
					sub+'_Script_MNI.vtc',
					sub+'_Script_SCLAI2_3DMC.log',
					sub+'_Script_SCLAI2_3DMC.sdm',
					sub+'_Script_SCLAI2_3DMCTS.fmr',
					sub+'_Script_SCLAI2_3DMCTS_LTR_THPGLMF2c.fmr',
					sub+'_Script_SCLAI2_3DMCTS_LTR_THPGLMF2c-TO-'+sub+'_Script_IIHC_ISO_FA.trf',
					sub+'_Script_SCLAI2_3DMCTS_LTR_THPGLMF2c-TO-'+sub+'_Script_IIHC_ISO_IA.trf',
					sub+'_Script_SCLAI2_CoregFirstVol.amr',
					sub+'_Script_SCLAI2.fmr']
					
	for fl in func_file_list:
		if not os.path.exists(os.path.join(f_path,fl)):
			missing = 1
			Errors += 'Error: '+fl+' missing for '+sub+'\n'
			print 'Error: ',fl,' missing for ',sub
			return False

	print "\tAll Functional Files Present!!"
	return True

main()
# If there are any Errors present, then write them to the error file
if Errors == '':
	log += 'NO ERRORS WHILE PROCESSING!\n'
	Errors ='NO ERRORS WHILE PROCESSING!\n'
else:
	print Errors
	log += line_break + Errors

err = open(os.path.join(log_path,'Archiving_log'+now.strftime("%m%d%y_%H%M%S")),'w')
err.write(log)
err.close()

