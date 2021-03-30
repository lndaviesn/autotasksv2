#!/usr/bin/env python
import json, os, shutil, glob, tempfile, zipfile, sys
from git import Repo
from git import Git
from time import sleep
import functions.get_lms_plugins as lmsplugins
import functions.get_lms_mods as lmsmods
import functions.totara_config as totara_config
import functions.globalfun as glfun
import includes.corelms as corelms


lmsdata={}
spath = os.getcwd()
lmsdata["uplmsfolder"] = spath + "/upgrade-lms/"
lmsdata["curlmsfolder"] = spath + "/current-lms/"
lmsdata["lmslocalstore"] = corelms.lmsrepor['localloc']
glfun.createdir(lmsdata["uplmsfolder"])


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
glfun.createdir(lmsdata["uplmsfolder"] + "/" + lmsdata["version_major"]+lmsdata["version_minor"])


#Different repos beteen 0 to 12 and 13
if (int(lmsdata["version_major"]) == 13):
    print ("setting LMS repo to version 13")
    lmsdata["gitrepo"] = corelms.lmsrepor['13']
if (int(lmsdata["version_major"]) > 9 and int(lmsdata["version_major"]) < 13):
    print ("setting LMS repo for version 9 to 12")
    lmsdata["gitrepo"] = corelms.lmsrepor['<12']


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
    sys.exit("Current LMS public Folder zip not found")


##Pulling upgradekey and saving to config
lmsinstall = {}
lmsconfig = {}
lmsconfig['upgradekey'] = totara_config.config_get_upgradekey(lmsdata["currentlmspath"] + "/config.php")
if (str(lmsconfig['upgradekey']) == "None"):
    lmsconfig['upgradekey'] = "null"
    print ("!!!no upgrade key found Sould add one!!!")
##Adding to maserdata
lmsinstall['config'] = lmsconfig
#writing data back to config file
data['lmsettings']=lmsinstall
with open( configpath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)



##getting plugins
glfun.createdir(lmsdata["pluginspath"])
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
repotag = "totara-"+ lmsdata["version"]
repofolder = lmsdata["newlmspath"]
zippath=lmsdata["lmslocalstore"]+"/"+ repotag +".zip"
if (os.path.isfile(zippath) == True):
    print ("If found will take from theit and insted")
    print ("And then unzip the file")
    print ("And place it in to the repo location")
    zipcmd = 'unzip ' + zippath + ' -d ' + lmsdata["tmpfolder"] + '> /dev/null'
    os.system(zipcmd)
    for lmsfname in glob.glob(lmsdata["tmpfolder"]+'/totaralearn-'+lmsdata["version"]):
        #found an issue where zip file as an folder in it again :(
        lmsfolder=lmsdata["tmpfolder"]+'/totaralearn-'+lmsdata["version"]+'/totaralearn-'+lmsdata["version"]
        os.rename(lmsfolder, repofolder)
    for lmsfname in glob.glob(lmsdata["tmpfolder"]+'/totaratxp-'+lmsdata["version"]):
        lmsfolder=lmsdata["tmpfolder"]+'/totaratxp-'+lmsdata["version"]+'/totaratxp-'+lmsdata["version"]
        os.rename(lmsfolder, repofolder)




else:
    print ("Getting corelms using Git")
    git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no'
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        gitrepo = Repo.clone_from(lmsdata["gitrepo"], repofolder, branch=repotag)
    print ("Removing git folder")
    glfun.gitclear(repofolder)
    zipname = lmsdata["lmslocalstore"]+"/"+ repotag +".zip"
    os.chdir(lmsdata["tmpfolder"])



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

shutil.copy2(lmsdata["currentlmspath"] + "/config.php",lmsdata["uplmsfolder"] + "/config.php")
persmods_folder ="for i in $(find . -type d'); do chmod 0755 \"$i\" > /dev/null; done"
os.system(persmods_folder)
persmods_file ="for i in $(find . -type f); do chmod 0644 \"$i\" > /dev/null; done"
os.system(persmods_file)


os.system(zipcmd)
shutil.copyfile(zipname,lmsdata["uplmsfolder"] + "/" + lmsdata["version_major"]+lmsdata["version_minor"]+"/"+zipname)

#Empty tmp folder (adding so dont forget)
shutil.rmtree(lmsdata["tmpfolder"])
