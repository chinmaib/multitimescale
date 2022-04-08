"""
Script: Plot_3D_voi.py
Author: Chinmai

Description: Reads VOI file and creates a 3D scatter plot.
"""

import os
import matplotlib.pyplot as plt

def main():

	voi_file = '/home/chinmai/src/UEF_2019/UEF_Functional_Neo.voi'

	fd = open(voi_file,'r')
	
	voi_contents = fd.read()
	fd.close()
	# Seperate the data line by line.
	lines = voi_contents.split('\n')

	# strip the first 20 lines containing header information
	# and the last 3 lines containing footer info
	lines = lines[20:-4]	# -4 coz the last item is a new line

	# Line 2 and 3 are color and new line
	# line 4 contains the number of voxels
	vox_num = int(lines[3].split(':')[1])
	# Etract the lines containing voxels
	# line no 5 to no of voxels
	vox = lines[4:4+vox_num]
	print ('Voxels:',len(vox))
	x=[]
	y=[]
	z=[]

	# Convert coordinates from string to list
	for v in vox:
		tmp = v.split(' ')
		x.append(int(tmp[0]))
		y.append(int(tmp[1]))
		z.append(int(tmp[2]))

	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d')
	ax.scatter(x,y,z)
	plt.show()

main()
