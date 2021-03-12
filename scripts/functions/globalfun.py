import os, shutil, sys, glob, hashlib
from distutils.dir_util import copy_tree

def gitclear(folderrp):
    gitlist = ['.git','.gitignore','readme.md']
    for gitfold in gitlist:
        print (gitfold)
        for name in glob.glob(folderrp + "/"+gitfold):
            if os.path.isdir(name) == True:
                print ("Removing " + gitfold)
                shutil.rmtree(name)
            if os.path.isfile(name) == True:
                print ("Removing " + gitfold)
                os.remove(name)


def copyDirectory(src, dest):
    try:
#        shutil.copytree(src, dest)
        copy_tree(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not copied. Error: %s' % e)

def createdir(folder):
    try:
        os.mkdir(folder)
    except OSError:
        print ("Creation of the directory failed")
    else:
        print ("Successfully created the directory")


def gethash(filename):
    with open(filename,"rb") as f:
        bytes = f.read() # read entire file as bytes
        readable_hash = hashlib.sha256(bytes).hexdigest();
    return (readable_hash)
