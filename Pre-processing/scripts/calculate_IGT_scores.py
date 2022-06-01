"""
Script: Calculate_IGT_scores.py
Author: Chinmaib

Description: Calculates IGT scores and plots them

"""

import os
import numpy as np
import matplotlib.pyplot as plt

from utils import *

# Get Parent Directoryi. MRI folder is the home directory.
home = os.path.abspath('..')
exp_path = os.path.join(home,'Experiments')

# Set Errors to empty
Errors = ''

line_break='*******************************************************************\n'
print line_break,

def main():

	global home,exp_dir
	global Errors

	exp_dir = os.path.join(exp_path,'IGT')

	# Create a plot folder to store the block net score plots.
	plot_dir = os.path.join(exp_dir,'Block_Net_Plots')
	# If folder doens't exist create one.
	if not os.path.isdir(plot_dir):
		os.mkdir(plot_dir)

	subjects = filter(lambda x: filter_hidden_folders(x,exp_dir),os.listdir(exp_dir))

	if len(subjects) == 0:
		Errors += 'Error: Unable to retrieve subjects from ' +exp_dir+'\n'
		print Errors,
		return

	# Sort the subjects alphabeticaly
	subjects.remove('Block_Net_Plots')
	subjects.sort()
	# Maintain a nested list to store the IGT2 scores for each subjects.
	scores = {}
	key = ['Name','NetT','Block','DeckT']
	nett_list = []

	for sub in subjects:
		#print sub
		
		behv_path = os.path.join(exp_dir,sub,'Behavioral')
		files = filter(filter_hidden,os.listdir(behv_path))
		if len(files) != 7:
			print 'Error: Choice files missing for ',sub
			continue
		
		# To Calculate NET TOTAL
		# Read in files sub_Choose.RESP.txt
		adv  = 0
		dadv = 0
		nett = 0
		# List of scores
		block = [0,0,0,0,0]
		deck   = [0,0,0,0]
		
		cresp_file = os.path.join(behv_path,sub+'_Choose.RESP.txt')
		if not os.path.exists(cresp_file):
			print 'Error: Unable to find behavioral file for ',sub
			break
		
		fd = open(cresp_file,'r')
		lines = fd.read().split('\n')
		fd.close()
		del lines[len(lines)-1]			# Last line is a new-line char
		j = 0 							# Block counter#
		
		for i in range(0,len(lines)):
			if lines[i] == '1' or lines[i] =='2':
				dadv+=1
				if lines[i] == '1':		# Deck A
					deck[0] += 1
				else:					# Deck B
					deck[1] +=1

			elif lines[i] =='3' or lines[i] =='4':
				adv+=1
				if lines[i] == '3':		# Deck C
					deck[2] += 1
				else:					# Deck D
					deck[3] +=1
		
			if ( (i+1) % 20 == 0):
				block[j] = adv - dadv
				j+=1

		nett = adv-dadv
		nett_list.append(nett)
		#print 'NET TOTAL: ',nett
		#print 'Block Net Scores: ',block
		#print 'Cards from Deck : ',deck
		
		#plot_block_net_score(block)

		#scores[sub] = [sub,nett,block,deck]
		#scores[i][key[1]] = nett
		#scores[i][key[2]] = block
		#scores[i][key[3]] = deck
		# Using CREP Transformed file
		# Read in files sub_Choose.RESP.transformed.txt
		adv  = 0
		dadv = 0
		cresp_file = os.path.join(behv_path,sub+'_Choose.RESP_transformed.txt')
		if not os.path.exists(cresp_file):
			print 'Error: Unable to find behavioral file for ',sub
			break

		# Using Numpy and transfored file
		M = np.loadtxt(cresp_file)
		#print 'Net Total using transformed: ',M.sum()

	imp   = 0
	unimp = 0
	below_avg = 0
	for sc in nett_list:
		if int(sc) <= -10:
			imp +=1
		elif int(sc) > -10 and int(sc) <= 7:   
			below_avg +=1
		elif int(sc) > 7:
			unimp += 1

	print 'Impaired: ', imp
	print 'Unimpaired: ', unimp
	print 'Below Average: ', below_avg

	nmat = np.asarray(nett_list)
	print 'Mean: ',nmat.mean()
	print 'Standard Deviation: ',nmat.std()
	print 'Max Score: ',max(nett_list)
	print 'Min Score: ',min(nett_list)

def plot_block_net_score(block):

	plt.plot(['NET 1','NET 2','NET 3','NET 4','NET 5'],block)
	plt.title('Subject: '+sub)
	plt.xlabel('No of Cards Selected')
	plt.ylabel('NET TOTAL')
	plt.grid(True)
	plt.savefig(os.path.join(plot_dir,sub+'_block_net.png'))
	plt.close()

main()
