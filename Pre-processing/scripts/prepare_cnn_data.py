"""
Reads in Voxel intensities from subject/CSV2 and populates the Subject/Features folder
	The Cubic VOI extracted CSV's are in CSV2 folder.

Choice Files:
	completion.txt - 1: For completable  collection 
					 0: For Incompletable collection

	selection.txt  - 1: If participant chose the expected value.
				 	 0: If partcipant did not choose the expected value

"""
import os
import numpy as np
from matplotlib import pyplot as plt
import tensorflow as tf

import keras
from keras.models import Sequential
from keras.layers import Conv3D,MaxPooling3D,Dense,Flatten

from keras.callbacks import EarlyStopping

from keras.optimizers import Adam

home = os.path.abspath('..')
path = os.path.join(home,'COLLECTION')

def main():

	subjects = os.listdir(path)
	subjects.sort()
	
	train_x = np.zeros((1,106,63,71))
	train_y = []

	for i in range(0,len(subjects)):
		if subjects[i][0] == '.' or not os.path.isdir(os.path.join(path,subjects[i])):
			print ('Ignoring Hidden File')
			continue
		
		print ('----------------------------------------------')
		print ('Processing :',subjects[i])

		fold_path = os.path.join(path,subjects[i])

		# Features Folder Path
		feat_path = os.path.join(fold_path,'Features')
		if not feature_folder_check(feat_path):
			continue

		# Read choices from choice files.
		choice_path = os.path.join(fold_path,'Behavioral')
		choice_type,selections = get_choices(choice_path)
		
		reg_path = os.path.join(fold_path,'CSV2','All_Cube') 
		
		# 40 choice files 
		files = os.listdir(reg_path)
		files.sort()

		j = 0		# Counter
		for k in range(0,3): 	# Just 1.csv for now.
		
			if files[k][0] == '.':		#SYstem or Hidden Files. 
				continue
			j = j + 1
			print(files[k])
			fl_path = os.path.join(reg_path,files[k])

			# Read in Numpy matrix
			m = np.loadtxt(fl_path,dtype=float,delimiter=',')
			avg_m = m.mean(axis=1)

			# Reshaping the matrix
			m_3d = avg_m.reshape((106,63,71))

			# NOTE: Inserting new data at the beginning	
			if j == 1:
				train_x[0] = m_3d
			else:
				train_x = np.insert(train_x,0,m_3d,axis=0)
			
			#plt.imshow(m_3d[1,:,:], interpolation='nearest')
			#plt.show()

			choice_index = int(files[k].split('.')[0])-1

			# NOTE: Add labels to the beginning.
			train_y.insert(0,choice_type[choice_index])
		
		# NOTE: Reshaping the array to fit Keras input format
		train_x = train_x.reshape(train_x.shape+(1,))
		print (train_x.shape)
		train_y = np.array(train_y)
		print (train_y.shape)
	
		######################### CNN Model #########################

		model = Sequential()
	
		# Layer 1: 	
		model.add(Conv3D(32,(3,3,3),input_shape=(106,63,71,1),strides=(2,2,2), \
				activation='relu', data_format="channels_last"))
		model.add(MaxPooling3D(pool_size=(2,2,2)))

		model.add(Flatten())
		
		model.add(Dense(64,activation='relu'))

		model.add(Dense(1,activation='sigmoid'))
		
		model.compile(loss='binary_crossentropy',optimizer='adam')
	
		earlystop = EarlyStopping(monitor='loss',min_delta = 0.0001, \
					patience = 5, mode='auto')

		kwargs = {'callbacks': [earlystop]}

		kwargs.update(x = train_x, y = train_y,epochs = 10, batch_size = 1)

		model.fit(**kwargs)



def get_choices(c_path):

	if not os.path.isdir(c_path):
		print ('Behavioral Folder not present')
		return
	files = os.listdir(c_path)
	select_file = os.path.join(c_path,'selection.txt')
	type_file   = os.path.join(c_path,'completion.txt')
	
	if not os.path.exists(select_file) or not os.path.exists(type_file):
		print('Choice files missing')
		return
	
	fs = open(select_file,'r')
	sel_data = fs.read()
	selections = sel_data.split('\n')
	fs.close()
	ft = open(type_file,'r')
	type_data = ft.read()
	choice_type = type_data.split('\n')
	ft.close()

	return choice_type,selections	


def feature_folder_check(feat_path):

	# If 'Features' folder already exists and inside it, it contains
	# 'All' regions folder with files inside it, THEN sub already processed
	if os.path.isdir(feat_path):
		reg_path = os.path.join(feat_path,'All_Cube')
		if os.path.isdir(reg_path):
			feat_files = os.listdir(reg_path)
			if len(feat_files) > 1:
				print ( subjects[i], ' already Processed!')
				return False
		else:
			os.mkdir(reg_path)
	else:
		# Create Feature folder and All_Cube folder.
		# NOTE: Will have to create other sub folders later. 
		os.mkdir(feat_path)
		os.mkdir(os.path.join(feat_path,'All_Cube'))
	return True
main()			
				
