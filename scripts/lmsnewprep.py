#!/usr/bin/env python
import json, os, shutil, glob, tempfile, zipfile, sys
from time import sleep
import functions.get_lms_plugins as lmsplugins
import functions.get_lms_mods as lmsmods
import functions.totara_config as totara_config
import functions.globalfun as glfun
import includes.corelms as corelms
import functions.get_lms_core as getlms


lmsdata={}
configpath = ""
spath = os.getcwd()
lmsdata["uplmsfolder"] = spath + "/new-lms/"
lmsdata["lmslocalstore"] = corelms.lmsrepor['localloc']
glfun.createdir(lmsdata["uplmsfolder"])
#added mode for config or upgarde.json file
if os.path.isfile(spath + '/upgrade.json'):
    configpath = spath + '/upgrade.json'

if os.path.isfile(spath + '/config.json'):
    configpath = spath + '/config.json'

if configpath =="":
    sys.exit("Error: No config found")
else:
    f = open(configpath,)

data = json.load(f)
lmsdata["address"] = data['lmsaddress']
lmsdata["version"] = data['lmscurrentversion']
lmsdata["lmslocalstore"] = corelms.lmsrepor['localloc']
lmsv = lmsdata["version"].split(".")
lmsdata["version_major"] = lmsv[0]
lmsdata["version_minor"] = lmsv[1]
lmsdata["tmpfolder"] = tempfile.mkdtemp()
lmsdata["newlmspath"] = lmsdata["tmpfolder"] + "/newlms"
lmsdata["pluginspath"] = lmsdata["tmpfolder"] + "/plugins"
lmsdata["modspath"] = lmsdata["tmpfolder"] + "/mods"
lmsv.clear()

try:
    shutil.rmtree(spath + "/current-lms/")
except OSError:
    print ("Deleting of the directory current-lms failed")
else:
    print ("Deleting the directory current-lms was done")

try:
    shutil.rmtree(spath + "/backup-lms/")
except OSError:
    print ("Deleting of the directory backup-lms failed")
else:
    print ("Deleting the directory backup-lms was done")


#Different repos beteen 0 to 12 and 13
if (int(lmsdata["version_major"]) == 13):
    lmsdata["gitrepo"] = corelms.lmsrepor['13']
if (int(lmsdata["version_major"]) > 9 and int(lmsdata["version_major"]) < 13):
    lmsdata["gitrepo"] = corelms.lmsrepor['<12']

print ("this is for LMS " + data['lmsaddress']);
print ("LMS version required " + lmsdata["version"]);

##Get mods (if any)
print ("Checking for Mods")
lmsdata['mods_curpull'] = False
lmsmods.pull(lmsdata)

##getting plugins
glfun.createdir(lmsdata["pluginspath"])
for i in data['plugins']:
    plugindataraw = json.dumps(i);
    plugindata = json.loads(plugindataraw);
    lmsplugins.get(plugindata, lmsdata)

##Get the core LMS
repotag = "totara-"+ lmsdata["version"]
repofolder = lmsdata["newlmspath"]
zippath=lmsdata["lmslocalstore"]+"/"+ repotag +".zip"
##Get the core LMS
print ("Getting Core LMS files")
if (int(lmsdata["version_major"]) <= 12):
    #getting versions 9 to 12
    if (glob.glob(corelms.lmsrepor['localloc'] +"/totaralearn-"+str(lmsdata["version"])+".tar.gz")):
        print ("found Pulling from local store")
        lmsfile = corelms.lmsrepor['localloc'] +"/totaralearn-"+str(lmsdata["version"])+".tar.gz"
        getlms.get_file(lmsfile,lmsdata["tmpfolder"])
        os.rename(lmsdata["tmpfolder"]+"/totaralearn-"+str(lmsdata["version"]),lmsdata["tmpfolder"]+"/newlms")
    else:
        print ("Getting from Totara Git repo")
        giturl = corelms.lmsrepor['<12']
        base = "totara-"+ lmsdata["version"]
        getlms.get_git(giturl,base,lmsdata["tmpfolder"])
        os.rename(lmsdata["tmpfolder"]+"/totara-"+str(lmsdata["version"]),lmsdata["tmpfolder"]+"/newlms")

if (int(lmsdata["version_major"]) == 13):
    #getting versions 13
    if (glob.glob(corelms.lmsrepor['localloc'] +"/totaratxp-"+str(lmsdata["version"])+".tar.gz")):
        print ("found Pulling from local store")
        lmsfile = corelms.lmsrepor['localloc'] +"/totaratxp-"+str(lmsdata["version"])+".tar.gz"
        getlms.get_file(lmsfile,lmsdata["tmpfolder"])
        os.rename(lmsdata["tmpfolder"]+"/totaratxp-"+str(lmsdata["version"]),lmsdata["tmpfolder"]+"/newlms")
    else:
        print ("Getting from Git services")
        giturl = corelms.lmsrepor['13']
        base = "totara-"+ lmsdata["version"]
        getlms.get_git(giturl,base,lmsdata["tmpfolder"])
        os.rename(lmsdata["tmpfolder"]+"/totara-"+str(lmsdata["version"]),lmsdata["tmpfolder"]+"/newlms")

print ("Generating ZIP file")
domain_split = data['lmsaddress'].split(".")
lmsfodname = "totara-" + lmsdata["version_major"] + lmsdata["version_minor"]+"-" + domain_split[0]
lmsfodpath = lmsdata["tmpfolder"] + "/" + lmsfodname
zipname = lmsfodname + ".zip"
os.chdir(lmsdata["tmpfolder"])

#Create zip file of corelms
print("Applying LMS core")
##Copy corelms to folder
glfun.copyDirectory(lmsdata["newlmspath"],lmsfodpath)
glfun.gitclear(lmsfodpath)
glfun.copyDirectory(lmsdata["newlmspath"], lmsdata["uplmsfolder"] + "/" + lmsdata["version_major"]+lmsdata["version_minor"] + "/totara")

if os.path.exists(lmsdata["pluginspath"]):
    #Copy plugins to folder
    print("Applying LMS plugins")
    copyfrom = lmsdata["pluginspath"]
    if (int(lmsdata["version_major"]) == 13):
        copyto = lmsfodpath + "/server"
    else:
        copyto = lmsfodpath
    glfun.copyDirectory(copyfrom,copyto)
    glfun.gitclear(lmsfodpath)

    glfun.copyDirectory(lmsdata["pluginspath"], lmsdata["uplmsfolder"] + "/" + lmsdata["version_major"]+lmsdata["version_minor"] + "/plugins")

if os.path.exists(lmsdata["modspath"]):
    ##Copy mods to folder
    print("Applying LMS mods")
    copyfrom = lmsdata["modspath"]
    if (int(lmsdata["version_major"]) == 13):
        copyto = lmsfodpath + "/server"
    else:
        copyto = lmsfodpath
    glfun.copyDirectory(copyfrom,copyto)
    glfun.gitclear(lmsfodpath)
    glfun.copyDirectory(lmsdata["modspath"], lmsdata["uplmsfolder"] + "/" + lmsdata["version_major"]+lmsdata["version_minor"] + "/mods")

print ("Sorting out permishions")
for root, dirs, files in os.walk(lmsfodpath, topdown=False):
    for dir in [os.path.join(root,d) for d in dirs]:
        os.chmod(dir, 0o777)
    for file in [os.path.join(root, f) for f in files]:
        os.chmod(file, 0o644)

source = lmsdata["tmpfolder"]+"/"+lmsfodname
destination = lmsdata["tmpfolder"]+"/"+zipname
base = os.path.basename(destination)
name = base.split('.')[0]
format = base.split('.')[1]
archive_from = os.path.dirname(source)
archive_to = os.path.basename(source.strip(os.sep))
shutil.make_archive(name, format, archive_from, archive_to)
shutil.move('%s.%s'%(name,format), destination)

shutil.copyfile(zipname,lmsdata["uplmsfolder"] + "/" + lmsdata["version_major"]+lmsdata["version_minor"]+"/"+zipname)

shutil.rmtree(lmsdata["tmpfolder"])
