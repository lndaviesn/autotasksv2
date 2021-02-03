#!/usr/bin/env python
import json, os, shutil, glob, tempfile, zipfile, sys, cryptography, base64
from git import Repo
from git import Git
from time import sleep
import functions.get_lms_plugins as lmsplugins
import functions.get_lms_mods as lmsmods
import includes.installdb as installdb
from distutils.dir_util import copy_tree
from cryptography.fernet import Fernet
import functions.gpg as gpg
from getpass import getpass

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
lmsdata["nwlmsfolder"] = spath + "/new-lms/"
createdir(lmsdata["nwlmsfolder"])


#added mode for config or upgarde.json file
if os.path.isfile(spath + '/upgrade.json'):
    configpath = spath + '/upgrade.json'

if os.path.isfile(spath + '/config.json'):
    configpath = spath + '/config.json'


f = open(configpath,)
data = json.load(f)

if os.path.isfile(spath + '/secure.key'):
    file = open('secure.key', 'rb')  # Open the file as wb to write bytes
    key = file.read()  # The key is type bytes still
    file.close()
else:
    key = gpg.dec(data['securekey'])

encryption_type = Fernet(key)



lmsdata["address"] = data['lmsaddress']
lmsdata["version"] = data['lmscurrentversion']
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

lmsinsmyjson = {}

##Needs work but want to added each part to config
###Adds DB
lmsdb={}
print ("enter DB name:")
lms_db_dbname = input()
lmsdb['name'] = lms_db_dbname
print ("enter DB Username:")
lms_db_username = input()
lmsdb['username'] = lms_db_username
lms_db_password = getpass(prompt='enter Database password: ').encode()
encrypted_message = encryption_type.encrypt(lms_db_password)
lmsdb['password'] = encrypted_message.decode()
lmsinsmyjson['db'] = lmsdb

### Adds Admin
lmsadmin={}
lmsadmin['username'] = "admin"
lms_admin_password = getpass(prompt='enter Admin password: ').encode()
encrypted_message = encryption_type.encrypt(lms_admin_password)
lmsadmin['password'] = encrypted_message.decode()
print ("enter Admin Email:")
lms_admin_email = input().encode()
encrypted_message = encryption_type.encrypt(lms_admin_email)
lmsadmin['email'] = encrypted_message.decode()
lmsinsmyjson['admin'] = lmsadmin

##Adds LMS data
lmssite={}
print ("enter LMS Fullname:")
lms_name_full = input()
lmssite['full'] = lms_name_full
print ("enter LMS Shortname:")
lms_name_short = input()
lmssite['short'] = lms_name_full



##Get Clamav settings
for avin in installdb.serversets:
    if (avin['server'] == data['lmsserver_address']):
        lmssite['clamavpath'] = avin['clamavpath']
        lmssite['clamavsocket'] = avin['clamavsocket']

lmsinsmyjson['site'] = lmssite


lmsconfig={}
print ("enter LMS upgradekey:")
lms_site_upgradekey = input()
lmsconfig['upgradekey'] = lms_site_upgradekey
lmsinsmyjson['config'] = lmsconfig

###Add users to be added
lmsusers = []
for usr in installdb.users:
    tmpmyjson = {}
    tmpmyjson["first"] = usr['first']
    tmpmyjson["last"] = usr['last']
    tmpmyjson["username"] = usr['username']
    tmpmyjson["email"] = usr['email']
    tmpmyjson["isadmin"] = usr['admin']
    lmsusers.append(tmpmyjson)
lmsinsmyjson['users'] = lmsusers


#Added the extra data to the config file
data['lmsettings']=lmsinsmyjson
with open( configpath, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

createdir(lmsdata["currentlmspath"])
##getting plugins
createdir(lmsdata["pluginspath"])
#make plugin folder
print ("Getting Plugins")
for i in data['plugins']:
    plugindataraw = json.dumps(i);
    plugindata = json.loads(plugindataraw);
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

copyDirectory(lmsdata["newlmspath"], lmsdata["nwlmsfolder"] + "/totara")

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
    copyDirectory(lmsdata["pluginspath"], lmsdata["nwlmsfolder"] + "/plugins")

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
    copyDirectory(lmsdata["modspath"], lmsdata["nwlmsfolder"] + "/mods")

os.system(zipcmd)
shutil.copyfile(zipname,lmsdata["nwlmsfolder"]+zipname)

#Empty tmp folder (adding so dont forget)
shutil.rmtree(lmsdata["tmpfolder"])
