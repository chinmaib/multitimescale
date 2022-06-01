"""
Script: Extracts MNI normalized VMR files from Disk location and
copies them into destination subject folder.
"""
import os
import shutil

disk="/media/chinmai/Seagate Backup Plus Drive/fMRI UEF/UEF_VTC_Extracted"

cwd = os.getcwd()
#path = os.path.join(cwd,"MOCOSERIES_0013")
vtc_path = os.path.join(cwd,"VTC_Files")

def filter_hidden(x,path):
    """
    x:        is the name of the folder
    path: is the absolute path of the folder

    A filter to remove any files or hidden folders and return a list
    of folders present in path.
    """
    if x[0] != '.' and os.path.isdir(os.path.join(path,x)):
        return True
    else:
        return False

def filter_vmr_files(x,path):
    """
    x:        is the name of the file
    path: is the absolute path of the folder

    A filter to get only files with extension VMR and has MNI in it.
    Filter also excludes hidden files.
    """

    if x[0] != '.':
        if (x.endswith('.vmr') and ('MNI' in x)):  
            return True
    else:
        return False

def main():
    # Get all the folder names from the disk location 
    folders = filter(lambda x:filter_hidden(x,disk),os.listdir(disk))
    
    # For each subject folder from the disk, create a folder if it's not present
    for sub in folders:
        v_path = os.path.join(vtc_path,sub)

        # Get a list of all sub-folder. Disk path + subject
        # NOTE: List obtained is always sorted.
        # 1st folder is Trial 1, 2nd is Trial 2 and so on. 
        sub_path = os.path.join(disk,sub)
        sub_folders = filter(lambda x:filter_hidden(x,sub_path),os.listdir(sub_path))
        #print sub_folders
        
        # For each sub-folder (trial)
        i = 1
        for trial in sub_folders:

            # get a list of all the required files.
            trial_path= os.path.join(sub_path,trial)
            fl = filter(lambda x:filter_vmr_files(x,trial_path),os.listdir(trial_path))
            #print fl

            # If NO required files are present then skip that folder.
            if (len(fl)==0):
                continue
            
            # Create ANAT folder inside the subject folder at destination.
            t_fold_name = v_path+"/ANAT_"+str(i)
            os.mkdir (t_fold_name)
            i = i + 1
    
            # Copy all the required files to destination folder.

            for f in fl:
                print 'Copying File ',f,' from ',sub,' and ',trial
                shutil.copy2(os.path.join(trial_path,f),t_fold_name)
            break
main()
