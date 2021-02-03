#!/usr/bin/env python
import functions.totarav2 as totara
import cryptography
from cryptography.fernet import Fernet
import os, shutil, sys, glob, tempfile, json
from os.path import basename
from time import sleep
import functions.gpg as gpg



spath = os.getcwd()
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
    #Will add pgp declater
    key = gpg.dec(data['securekey'])

encryption_type = Fernet(key)


def decryt(encval):
    enctxt = encval.encode()
    decrypted = encryption_type.decrypt(enctxt)
    decrypted = decrypted.decode()
    return decrypted

#data arrary
lmsdata={}
#dbname,dbuser,dbpass,
db = {}
db['name'] = data['lmsettings']['db']['name']
db['user'] = data['lmsettings']['db']['username']
db['pass'] = decryt(data['lmsettings']['db']['password'])
lmsdata['db'] = db
#adminuser, adminpass, adminemail
admin = {}
admin['user'] = data['lmsettings']['admin']['username']
admin['pass'] = decryt(data['lmsettings']['admin']['password'])
admin['email'] = decryt(data['lmsettings']['admin']['email'])
lmsdata['admin'] = admin
#sitefullname siteshortname
site = {}
clamav = {}
clamav['clamavpath'] = data['lmsettings']['site']['clamavpath']
clamav['clamavsocket'] = data['lmsettings']['site']['clamavsocket']
site['fullname'] = data['lmsettings']['site']['full']
site['shortname'] = data['lmsettings']['site']['short']
site['url'] = "https://" + data['lmsaddress']
versplit = data['lmsupgardeversion'].split('.')
site['major_version'] = versplit[0]
site['minor_version'] = versplit[1]
site['avsettings'] = clamav
lmsdata['site'] = site
lmsdata['users'] = data['lmsettings']['users']
totara.webb(lmsdata['site']['url'],True)
res = totara.setup_install(lmsdata)
if (res['error'] == True ):
    print (res['msg'])
    sys.exit("Error Found during install")
#Now for the mods

print ("!!!to do mods you need to manualy!!!")
print ("Add the below to config.php")
print ("$CFG->upgradekey = '"+ data['lmsettings']['config']['upgradekey']+"';")
print ("$CFG->preventexecpath = false;")
print ("When done press enter to carry on")
dhold = input()

res = totara.setup_modify(lmsdata)
if (res['error'] == True ):
    print ('Error Found at: ' + res['msg'])
    sys.exit("Error Found during Modding")

print("Disable Content Market")
totara.disable_content_market(lmsdata['site']['url'],lmsdata['site']['major_version'])
print("Purge Cache")
totara.purgecache(lmsdata['site']['url'],lmsdata['site']['major_version'])



print ("!!!to do mods you need to manualy!!!")
print ("Change in config.php")
print ("$CFG->preventexecpath = True;")
print ("and remove write permishions to config.php")
print ("When done press enter to carry on")
dhold = input()


##Run self tests
testres = True
res = totara.check_plugins(lmsdata['site']['url'])
if res['finalcheck'] == False:
    totara.maxerr()
    testres = False
    sys.exit("An issue was found with plugins")

res = totara.check_envextra(lmsdata['site']['url'])
if res['finalcheck'] == False:
    totara.maxerr()
    testres = False
    sys.exit("An issue was found with Php")

if testres == True:
    totara.close()
    print ("All Tests came out clear")
