#!/usr/bin/env python
import json, os, shutil, glob, tempfile, zipfile, sys
from git import Repo
from git import Git
from time import sleep
import functions.get_lms_plugins as lmsplugins
import functions.get_lms_mods as lmsmods
from distutils.dir_util import copy_tree

#######################################
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

##########################################

lmsdata={}
spath = os.getcwd()
lmsdata["uplmsfolder"] = spath + "/upgrade-lms/"
lmsdata["curlmsfolder"] = spath + "/current-lms/"

#added mode for config or upgarde.json file
if os.path.isfile(spath + '/upgrade.json'):
    configpath = spath + '/upgrade.json'

if os.path.isfile(spath + '/config.json'):
    configpath = spath + '/config.json'


f = open(configpath,)


data = json.load(f)
print ("this is for LMS " + data['lmsaddress']);
print ("Getting LMS totara for version " + data['lmsupgardeversion']);
lmsdata["tmpfolder"] = tempfile.mkdtemp()

#set LMSdata array
lmsdata["address"] = data['lmsaddress']
lmsdata["version"] = data['lmsupgardeversion']
lmsv = lmsdata["version"].split(".")
lmsdata["version_major"] = lmsv[0]
lmsdata["version_minor"] = lmsv[1]
lmsv.clear()

print ("Tmp Folder: " + lmsdata["tmpfolder"])

copyDirectory(lmsdata["uplmsfolder"], lmsdata["tmpfolder"])

domain_split = data['lmsaddress'].split(".")
lmsfodname = "totara-" + lmsdata["version_major"] + lmsdata["version_minor"]+"-" + domain_split[0]
lmsfodpath = lmsdata["tmpfolder"] + "/" + lmsfodname

zipname = lmsfodname + "-update" + ".zip"
os.chdir(lmsdata["tmpfolder"])

print ("adding corelms files")
if os.path.exists('totara'):
    copyDirectory('totara',lmsfodpath)
    for name in glob.glob(lmsfodpath + "/.git"):
        if os.path.isdir(name) == True:
            shutil.rmtree(lmsfodpath + "/.git")
        if os.path.isfile(name) == True:
            print ("It be an file")
else:
    sys.exit("Core lms folder not found")

if os.path.exists('plugins'):
    print ("adding plugins files")
    copyDirectory('plugins',lmsfodpath)
else:
    print ("No plugins files to add")

if os.path.exists('mods'):
    print ("adding mods files")
    copyDirectory('mods',lmsfodpath)
else:
    print ("No mod files to add")

zipcmd = 'zip -qr ' + zipname + ' ' + lmsfodname
os.system(zipcmd)
shutil.copyfile(zipname,lmsdata["uplmsfolder"]+zipname)

#Empty tmp folder (adding so dont forget)
shutil.rmtree(lmsdata["tmpfolder"])
