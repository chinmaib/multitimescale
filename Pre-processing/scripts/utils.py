import os

def filter_hidden(x):
	if x[0] != '.' :
		return True
	else:
		return False

def filter_dcm(x):
	if x[0] != '.' and (x.lower().endswith('dcm') or x.lower().endswith('ima')):
		return True
	else:
		return False

def filter_hidden_folders(x,path):
	"""
	x:	  is the name of the folder 
	path: is the absolute path of the folder

	A filter to remove any files or hidden folders and return a list
	of folders present in path.
	"""
	if x[0] != '.' and os.path.isdir(os.path.join(path,x)):
		return True
	else:
		return False

def fmr_present(path):

	files = filter(filter_hidden,os.listdir(path))
	for fl in files:
		if fl.endswith('fmr') or fl.endswith('FMR'):
			return True

	return False

def dcm_present(path):

	files = filter(filter_hidden,os.listdir(path))
	for fl in files:
		if fl.endswith('DCM') or fl.endswith('dcm'):
			return True

	return False

def vtc_present(path):

	files = filter(filter_hidden,os.listdir(path))
	for fl in files:
		if fl.endswith('vtc') or fl.endswith('VTC'):
			return True

	return False

def get_experiments(path):
	"""
	Function take the absolute path of the home directory as argument and
	returns a list of all the Experiment folders present in inside 'Experiments'
	It also filter out any files and hidden folders.
	"""
	expr = filter(lambda x:filter_hidden_folders(x,path),os.listdir(path))
	return expr	


def get_vol_from_config(conf_file):
	
	config = open(conf_file,'r')
	param = config.read()
	param_list = param.split('\n')
	volumes  = param_list[2].split(':')[1]
	config.close()
	return volumes

def filter_anatomy_folders(x,path):
	"""
	x:	  is the name of the folder 
	path: is the absolute path of the folder

	A filter to return a list of Experiment folders present in a subject folder
	leaving out the Anatomy folder.

	Anatomical files begin with 'T1_MPRAGE_'
	"""
	if x[0] != '.' and os.path.isdir(os.path.join(path,x)):
		return True
	else:
		return False

def rename_IMA_to_DCM(x_path):
	files = filter(filter_dcm,os.listdir(x_path))
	count = 0
	for f in files:
		if(f[-3:] == 'DCM'):
			continue
		f = os.path.join(x_path,f)
		temp = f[:-3]
		temp = temp + 'DCM'
		os.rename(f,temp)
		count = count + 1
	print '\t',count, ' file extentions changed to DCM'

def rename_anat_files(a_files,path): 
	"""Renames anatomical DICOM files to BrainVoyager readable format
	"""
	for fl in a_files:
		flist = fl.split('.')
		# Fomat : name-series-volume-image.DCM
		# 0th item is name, 3rd is series and 4th is volume.
		dest = flist[0]+'-'+flist[3]+'-'+flist[4]+'-'+str('%05d'%(int(flist[4])))+'.dcm'
		os.rename(os.path.join(path,fl),os.path.join(path,dest))

def check_anat_format(name):
	""" Checks if the anatomical filenames are in Braivoyager readable format or not
	"""
	items = name.split('-')
	if len(items) < 3:
		return 'old'
	else:
		return 'new'

