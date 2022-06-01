import os

def filter_hidden(x,path):
	"""
	x:	  is the name of the folder 
	path: is the absolute path of the folder

	A filter to remove any files or hidden folders and return a list
	of folders present in path.
	"""
	if x[0] != '.' and ("12.14.54." in x):
		return True
	else:
		return False

cwd = os.getcwd()
path = os.path.join(cwd,"MOCOSERIES_0013")
files = filter(lambda x:filter_hidden(x,path),os.listdir(path))

for fl in files:
	print 'Removing file: ',fl
	os.remove(os.path.join(path,fl))
	#print fl


