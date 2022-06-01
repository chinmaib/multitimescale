"""
Script : generate_matlab_script.py
Author : Chinmai

This script reads in the timing template for each experiments and 
generates the MATLAB script

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
#log_path = os.path.join(home,'Logs/MATALB_Generation')

# MATLAB script
m_path = os.path.join(home,'MATLAB')


#Errors = ''

log = 'Running generate_matlab_script.py @ '+now.strftime("%m-%d-%y %H:%M:%S")+'\n'
print log,

#line_break='*******************************************************************\n'
#print line_break

def main():

	global home,m_path,exp_path
	global log

	Expr = get_experiments(exp_path)
	Expr.sort()
	#Expr = ['FITTING']
	for exp in Expr:

		#log += 'Experiment: '+exp+'\n'
		print 'Experiment: ',exp
		# Set experiment directory and choice directory
		exp_dir = os.path.join(exp_path,exp)
		
		# Reading Configuration file
		conf_file = os.path.join(exp_dir,'config')
		config = open(conf_file,'r')
		if not config:
			Errors += 'Error: Config file not present in '+exp_dir+'\n'
			print 'Error: Unable to Open Config File in ',exp_dir,line_break
			continue

		param = config.read()
		config.close()
		param_list = param.split('\n')
		# No of functional volumes is 3rd line
		num_vol = int(param_list[2].split(':')[1])
		print '\tNo. of volumes: ',num_vol		
	
		# Temporal resolution is the last line,12
		temp_res = int(param_list[11].split(':')[1])
		print '\tTemporal Resoultion: ',temp_res

		phases = param_list[10].split(':')
		phases_list = phases[1].split(',')
		# Strip blank spaces.
		for i in range(0,len(phases_list)):
			phases_list[i] = phases_list[i].strip()
		print '\tPhases: ',phases_list
		
		# No of choices will be the No. of CSV files output. Line 13
		csv_num = int(param_list[12].split(':')[1])
		print '\tNo. of choices: ',csv_num
		
		# Read in the Timing template.
		time_file = os.path.join(exp_dir,'Timing_'+exp+'.csv')
		timing = open(time_file,'r')

		if not timing:
			print 'Error: Timing file not present in ',exp_dir
			continue
		
		time_data = timing.read()
		timing.close()
	
		time_list = time_data.split('\n')
		
		# Getting rid of first header and  last new line.		
		del time_list[len(time_list)-1]
		del time_list[0]

		# Order, Trial, Phase, Phase, Length, Cue, GoNogo, TimeOnset, TimeOffset
		
		# Get trial length and frame number when trail starts
		# Also mark start and end phase
		trial_len,trial_start,start_phase,end_phase = get_trial_len(time_list,phases_list)
		print '\tLength of each trial: ',trial_len

		# Frame number when the trial starts.
		print '\tTrial Start:',trial_start+1
		print '\tStart Phase:',start_phase
		print '\tEnd_phase:',end_phase
		#print 'Trail Start Entry: ',time_list[trial_start-1]

		# Going through all entries.

		for i in range(trial_start,len(time_list)-1,trial_len):
			values = time_list[i].split(',')
			# Get Trial number. Trail is second value
			#print 'Trail: ',values[1]
			#trial = time_list	
			# Trial will be from i to i+trial_len
			for j in range(i,i+trial_len):
				# Get phase
				phase = time_list[j].split(',')[2]	
				#print phase
				if phase == start_phase:
					start_time = int(time_list[j].split(',')[-2])/temp_res
					break
			for j in range(i,i+trial_len):
				# Get phase
				phase = time_list[j].split(',')[2]	
				#print phase
				if phase == end_phase:
					end_time = int(time_list[j].split(',')[-1])/temp_res
					break
			#print '\tstart time:',start_time/temp_res
			#print '\tend_time:',end_time/temp_res
			cw = "csvwrite(strcat(spath,sub,'_',Exp(1:3),'_"+values[1]+".csv'),voi_timecourse_matrix(:,"
			cw += str(start_time)+':'+str(end_time)+'))'
			print cw
			#print '--------------------------------------------'

# Skipping the Descriptions & Writing Matrices Directly
#	csvwrite(strcat(spath,'11.csv'),voi_timecourse_matrix(:,114:121))

def get_trial_len(time_list,phases_list):

	trial = 1
	trial_len = 0
		
	trial_start = 1000	# 1000 is just an approx big number
	
	start_phase = ''
	end_phase	= ''

	for i in range(0,len(time_list)):
		values = time_list[i].split(',')

		# Instructions don't have trial numbers.
		if values[1].strip() == '':
			continue
		elif i < trial_start:
			# Coming here means trial starts.
			trial_start = i 

		# Trial is second column. We are looking only at 1st trial to find the
		# length, start_phase & end_phase
		# Find out the length in frames of 1st trail.
		if int(values[1]) == trial:		# Means 1st trail
			trial_len = trial_len+1
			
		if int(values[1]) > trial:
			break
	# Start Phase
	for i in range(trial_start,trial_start+trial_len-1):
		values = time_list[i].split(',')
		
		if values[2] in phases_list:
			start_phase = values[2]
			break
	# End Phase
	for i in range(trial_start+trial_len-1,trial_start,-1):
		values = time_list[i].split(',')
		
		if values[2] in phases_list:
			end_phase = values[2]
			break

	return trial_len,trial_start,start_phase,end_phase
		
		
main()
