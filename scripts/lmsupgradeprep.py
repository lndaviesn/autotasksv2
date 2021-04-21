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

##Get mods (if any)
print ("Getting Mods")
lmsmods.pull(lmsdata)



print ("Generating ZIP file")
##Build zip file
#!for record need to do this way to by pass the issue of not being able to over wtire folders
#make version folder

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

shutil.copy2(lmsdata["currentlmspath"] + "/config.php",lmsdata["uplmsfolder"] + "/config.php")
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

#Empty tmp folder (adding so dont forget)
shutil.rmtree(lmsdata["tmpfolder"])
