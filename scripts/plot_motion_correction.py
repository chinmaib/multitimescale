"""
Script: plot_motion_correction.py
Experiment : 2018 MRI Data

Description: Plots motion correction 3D graph for the suject and saves the plot.

"""

import datetime

# Get Current data and time
now = datetime.datetime.now()

import os
import imp
import shutil
plot_lib = 0
try:
	imp.find_module('matplotlib')
	plot_lib = 1
	import matplotlib.pyplot as plt
except ImportError:
	plot_lib = 0

# Import functions from utils.py
from utils import *

# Max motion threshold to 0.1 mm
# threshold_count : no. of times motion crosses threshold.
# threshold_time  : max time the subject crosses threshold. 
threshold = 3.0	 	#  3 mm
threshold_count = 25	# 5% of no. of volumes
threshold_time  = 20	# 5% of no. of volumes

home = os.path.abspath('..')
exp_path = os.path.join(home,'Experiments')
log_path = os.path.join(home,'Logs/Plot')

log_end ='_Script_SCLAI2_3DMC.log'

# Set Errors to empty
Errors = ''

log = 'Running plot_motion_correction.py at '+now.strftime("%m-%d-%y %H:%M:%S")+'\n'
print log

line_break='*******************************************************************\n'
print line_break,

def main():

	global log,Errors,line_break
	global home,exp_path

	# Get a list of experiments.
	Expr = get_experiments(exp_path)

	for exp in Expr:
		exp_dir = os.path.join(exp_path,exp)
		
		log += 'Experiment: '+exp+'\n'
		print 'Experiment :',exp
	
		# Read the configuration file in exp_dir & extract volumes
		conf_file = os.path.join(exp_dir,'config')
		vol = int(get_vol_from_config(conf_file))
	
		subjects = filter(lambda x: filter_hidden_folders(x,exp_dir),os.listdir(exp_dir))

		if len(subjects) == 0:
			Errors += 'Error: Unable to retrieve subjects from ' +exp_dir+'\n'
			print 'Error: Unable to retrieve subjects from ',exp_dir
			continue

		# Sort the subjects alphabeticaly
		subjects.sort()
		
		for sub in subjects:

			log += '\tSubject: '+sub+'\n'
			print '\tSubject: ',sub
			
			sub_path = os.path.join(exp_dir,sub)	
			# Functional path
			f_path = os.path.join(sub_path,'Functional')

			log_file = os.path.join(f_path,sub+log_end)

			if not os.path.exists(log_file):
				Errors += sub+' pre-processing not yet done!\n'
				print sub,' pre-processing not yet done!'
				continue

			plot_path  = os.path.join(sub_path,'Plot')
			if os.path.isdir(plot_path):
				#log += 'Plotting already done for '+sub+'\n'
				#print 'Plotting already done for ',sub
				#continue
				shutil.rmtree(plot_path)

			os.mkdir(plot_path)

			fd = open(log_file,'r')
			data = fd.read()
			lines = data.split('\n')

			fd.close()
	
			# 1st 4 lines are header information. Data starts from 5th line
			# vol+3 because 1st vol info is skipped.
			X = lines[4:vol+3]

			dx = []
			dy = []
			dz = []
			rx = []
			ry = []
			rz = []

			for i in range(0,len(X)):
				val = X[i].split(':')
				dx.append(float(val[3].strip().split(' ')[0]))
				dy.append(float(val[4].strip().split(' ')[0]))
				dz.append(float(val[5].strip().split(' ')[0]))
				rx.append(float(val[6].strip().split(' ')[0]))
				ry.append(float(val[7].strip().split(' ')[0]))
				rz.append(float(val[8].strip().split(' ')[0]))

			params = {'dx':dx,'dy':dy,'dz':dz,'rx':rx,'ry':ry,'rz':rz}
			
			max_motion=analyze_params(params,sub,plot_path)
			# If matplot lib is present.
			if plot_lib:		
				motion_plot(dx,dy,dz,rx,ry,rz,plot_path,sub,vol,max_motion)
				log += '\t3D Motion Plot completed for '+sub+'\n'
				print '\t3D Motion Plot completed for ',sub



		print line_break
		log += line_break


def analyze_params(params,sub,plot_path):
	global log,threshold
	global threshold_time,threshold_count
	log+= '\tAnalyzing parameters for '+sub+'\n'
	print '\tAnalyzing parameters for ',sub

	flag = 0 	# Conformance flag: 0- Yes. 1-No.
	# List of directions where motion crosses threshold
	axis = []
	vari= 'Analyzing parameters for '+sub+'\n'

	for key,par in params.iteritems(): 
		vari += '\nAxis: '+key+'\n'
		# Calculate max motion, mean and variance of motion
		max_motion = max(abs(max(par)),abs(min(par)))
		vari += 'Max Motion:'+str(max_motion)+'\n'
		vari += 'Mean:'+str(get_mean(par))+'\n'
		vari += 'Var: '+str(get_var(par))+'\n'

		log += '\t\tMax Motion:'+str(max_motion)+'\n'
		log += '\t\tMean:'+str(get_mean(par))+'\n'
		log += '\t\tVar: '+str(get_var(par))+'\n'
		# If max motion is less than threshold then all good.
		if max_motion > threshold:
			axis.append(key)
	
	vari += line_break		
	max_time = 0
	count = 0

	for ax in axis:
		log+= '\tAxis:'+ax+'\n'
		vari += 'Axis: '+ax+'\n'
		time = 0
		# get() will return the key->value. In this case it's a list of motion values
		X = params.get(ax)
		it = 0	
		for i in range(0,len(X)):
			if it > 0:		# Simple iterator to skip processed values
				it = it -1 
				continue

			# If a value crosses threshold
			# Then measure the interval
			if abs(X[i]) > threshold:
				count = count + 1
				vari +='Mption crossing threshold at '+str(i)+' '+str(X[i])+'\n' 		
				log += '\tMotion crossing threshold at '+str(i)+str(X[i])+'\n'
				time = 1
				for j in range(i+1,len(X)):
					if abs(X[j]) > threshold:
						time = time + 1
					else:
						break
				#print '\tTime : ',time
				vari += 'Time: '+str(time)+'\n'
				log += '\tTime: '+str(time)+'\n'
				if time > max_time:
					max_time = time
				it = time
			
	log += '\tCount: '+str(count)+'Max Interval:'+str(max_time)+'\n'
	vari += 'No. of times motion excceds threshold: '+str(count) +'\n'
	vari += 'Max interval where motion exceeds threshold: '+str(max_time)+'\n'
					
	# I will have max_time and count 
	if max_time < threshold_time or count < threshold_count:
		print  '\t',sub,' conforms to Motion Threshold'+'\n'
		log += sub+' conforms to Motion Threshold'+'\n'
		vari += sub+' conforms to Motion Threshold'+'\n'
	else:
		print '\t',sub,' DOESN\'T conform to Motion Threshold'
		log += sub+' DOESN\'T conform to Motion Threshold'+'\n'
		vari += sub+' DOESN\'T conform to Motion Threshold'+'\n'

	fw = open(os.path.join(plot_path,sub+'.log'),'w')
	fw.write(vari)
	fw.close()
	return max_motion

def get_var(lst):
	mu = get_mean(lst)
	return (sum((xi-mu)**2 for xi in lst)/len(lst))
	

def get_mean(lst):
	return sum(lst)/len(lst) 

def motion_plot(dx,dy,dz,rx,ry,rz,plot_path,sub,vol,max_motion):
	global log	
	ref = [0] * vol
	thn1 = [-0.5] * vol
	thp1 = [0.5] * vol
	thn2 = [-1.0] * vol
	thp2 = [1.0] * vol
	plt.style.use('dark_background')
	plt.plot(dx,'red',label='dx')
	plt.plot(dy,'green',label='dy')
	plt.plot(dz,'blue',label='dz')
	plt.plot(rx,'yellow',label='rx')
	plt.plot(ry,'magenta',label='ry')
	plt.plot(rz,'cyan',label='rz')
	plt.plot(ref,'white')

	plt.plot(thn1,'w--')	# Threshold line
	plt.plot(thp1,'w--')	# Threshold line
	plt.plot(thn2,'w--')	# Threshold line
	plt.plot(thp2,'w--')	# Threshold line

	plt.xlim(0,vol)
	plt.ylim(-max_motion-0.5,max_motion+0.5)
	plt.legend()
	plt.title('Rigid Body Motion Parameters-3 Translations, 3 Rotations')
	plt.savefig(os.path.join(plot_path,sub+'.png'))
	plt.close()

main()

print line_break
log += line_break
# If there are any Errors present, then write them to the error file
if Errors == '':
    Errors ='NO ERRORS WHILE PROCESSING!\n'
else:
    print Errors
log += line_break + Errors

#print log
err = open(os.path.join(log_path,'Plotting_log'+now.strftime("%m%d%y_%H%M%S")),'w')
err.write(log)
err.close()
