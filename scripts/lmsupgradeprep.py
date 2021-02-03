#!/usr/bin/env python
import json, os, shutil, glob, tempfile, zipfile, sys
from git import Repo
from git import Git
from time import sleep
import functions.get_lms_plugins as lmsplugins
import functions.get_lms_mods as lmsmods
import functions.totara_config as totara_config
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
createdir(lmsdata["uplmsfolder"])


#added mode for config or upgarde.json file
if os.path.isfile(spath + '/upgrade.json'):
    configpath = spath + '/upgrade.json'

if os.path.isfile(spath + '/config.json'):
    configpath = spath + '/config.json'


f = open(configpath,)


data = json.load(f)
print ("this is for LMS " + data['lmsaddress']);
print ("Getting LMS totara for version " + data['lmsupgardeversion']);

#set LMSdata array
lmsdata["address"] = data['lmsaddress']
lmsdata["version"] = data['lmsupgardeversion']
lmsv = lmsdata["version"].split(".")
lmsdata["version_major"] = lmsv[0]
lmsdata["version_minor"] = lmsv[1]
lmsv.clear()



#Different repos beteen 0 to 12 and 13
lmsdata["gitrepo"] = 'ssh://git@code.totaralms.com/totara.git'
lmsdata["tmpfolder"] = tempfile.mkdtemp()
lmsdata["modspath"] = lmsdata["tmpfolder"] + "/mods"
lmsdata["currentlmspath"] = lmsdata["tmpfolder"] + "/currentlms"
lmsdata["newlmspath"] = lmsdata["tmpfolder"] + "/newlms"
lmsdata["pluginspath"] = lmsdata["tmpfolder"] + "/plugins"
print ("Tmp Folder: " + lmsdata["tmpfolder"])


#Search for webfolder and unzip the folder
finding_current = False
for name in glob.glob(lmsdata["curlmsfolder"] + '/*htdocs*.zip'):
    finding_current = True
    print ("Unpacking current LMS file ")
    with zipfile.ZipFile(name, 'r') as zip_ref:
        zip_ref.extractall(lmsdata["tmpfolder"])
    os.rename(lmsdata["tmpfolder"] + "/httpdocs",lmsdata["currentlmspath"])


for name in glob.glob(lmsdata["curlmsfolder"] + '/*public_html*.zip'):
    finding_current = True
    print ("Unpacking current LMS file ")
    with zipfile.ZipFile(name, 'r') as zip_ref:
        zip_ref.extractall(lmsdata["tmpfolder"])
    os.rename(lmsdata["tmpfolder"] + "/public_html",lmsdata["currentlmspath"])

for name in glob.glob(lmsdata["curlmsfolder"] + '/*httpdocs*.zip'):
    finding_current = True
    print ("Unpacking current LMS file ")
    with zipfile.ZipFile(name, 'r') as zip_ref:
        zip_ref.extractall(lmsdata["tmpfolder"])
    os.rename(lmsdata["tmpfolder"] + "/httpdocs",lmsdata["currentlmspath"])

if finding_current == False:
    sys.exit("current LMS folder missing")


##Pulling upgradekey and saving to config
lmsinstall = {}
lmsconfig = {}
lmsconfig['upgradekey'] = totara_config.config_get_upgradekey(lmsdata["currentlmspath"] + "/config.php")
if (lmsconfig['upgradekey'] == ""):
    print ("!!!no upgrade key found Sould add one!!!")
##Adding to maserdata
lmsinstall['config'] = lmsconfig
#writing data back to config file
data['lmsettings']=lmsinstall
with open( configpath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)



##getting plugins
createdir(lmsdata["pluginspath"])
#make plugin folder
print ("Getting Plugins")
for i in data['plugins']:
    plugindataraw = json.dumps(i);
    plugindata = json.loads(plugindataraw);
    if plugindata["pluginupgarde"] == "false":
        lmsplugins.pull(plugindata, lmsdata)
    elif plugindata["pluginupgarde"] == "true":
        lmsplugins.get(plugindata, lmsdata)

##Get mods (if any)
print ("Getting Mods")
lmsmods.pull(lmsdata)

##Get the core LMS
git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no'
repotag = "totara-"+ lmsdata["version"]
repofolder = lmsdata["newlmspath"]
print ("Getting corelms using Git")
with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
    gitrepo = Repo.clone_from(lmsdata["gitrepo"], repofolder, branch=repotag)

print ("Generating ZIP file")
##Build zip file
#!for record need to do this way to by pass the issue of not being able to over wtire folders
#make version folder

domain_split = data['lmsaddress'].split(".")
lmsfodname = "totara-" + lmsdata["version_major"] + lmsdata["version_minor"]+"-" + domain_split[0]
lmsfodpath = lmsdata["tmpfolder"] + "/" + lmsfodname

zipname = lmsfodname + ".zip"
os.chdir(lmsdata["tmpfolder"])
zipcmd = 'zip -qr ' + zipname + ' ' + lmsfodname



#Create zip file of corelms
print("Applying LMS core")
##Copy corelms to folder
copyDirectory(lmsdata["newlmspath"],lmsfodpath)
for name in glob.glob(lmsfodpath + "/.git"):
    if os.path.isdir(name) == True:
        print ("removed folder")
        shutil.rmtree(lmsfodpath + "/.git")
    if os.path.isfile(name) == True:
        print ("It be an file")

copyDirectory(lmsdata["newlmspath"], lmsdata["uplmsfolder"] + "/totara")

if os.path.exists(lmsdata["pluginspath"]):
    #Copy plugins to folder
    print("Applying LMS plugins")
    copyDirectory(lmsdata["pluginspath"],lmsfodpath)
    for name in glob.glob(lmsfodpath + "/.git"):
        if os.path.isdir(name) == True:
            print ("removed folder")
            shutil.rmtree(lmsfodpath + "/.git")
        if os.path.isfile(name) == True:
            print ("It be an file")
    copyDirectory(lmsdata["pluginspath"], lmsdata["uplmsfolder"] + "/plugins")

if os.path.exists(lmsdata["modspath"]):
    ##Copy mods to folder
    print("Applying LMS mods")
    copyDirectory(lmsdata["modspath"],lmsfodpath)
    for name in glob.glob(lmsfodpath + "/.git"):
        if os.path.isdir(name) == True:
            print ("removed folder")
            shutil.rmtree(lmsfodpath + "/.git")
        if os.path.isfile(name) == True:
            print ("It be an file")
    copyDirectory(lmsdata["modspath"], lmsdata["uplmsfolder"] + "/mods")


shutil.copy2(lmsdata["currentlmspath"] + "/config.php",lmsdata["uplmsfolder"]+"/config.php")
os.system(zipcmd)
shutil.copyfile(zipname,lmsdata["uplmsfolder"]+zipname)

#Empty tmp folder (adding so dont forget)
shutil.rmtree(lmsdata["tmpfolder"])
