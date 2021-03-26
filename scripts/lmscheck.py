#!/usr/bin/env python
#import functions.totarav2 as totara
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
    key = gpg.dec(data['securekey'])

encryption_type = Fernet(key)

def decryt(encval):
    enctxt = encval.encode()
    decrypted = encryption_type.decrypt(enctxt)
    decrypted = decrypted.decode()
    return decrypted

print ("I am just doing some LMS checks, just to be safe")

global browser
url = "https://" + data['lmsaddress']
totara.webb(url,False)
totara.login(decryt(data['lmsserver_user']),decryt(data['lmsserver_pass']))
testres = True

### Check goes their
res = totara.check_plugins(url)
if res['finalcheck'] == False:
    totara.maxerr()
    testres = False
    sys.exit("An issue was found with plugins")

res = totara.check_security(url)
if res['counts']['err'] > 0:
    testres = False
    print("Some LMS security Warining have been found")
    for isse in res['issues_n']:
        print (isse)
    sys.exit("These need to be looked in to")
else:
    if res['counts']['warn'] > 2:
        print("Some LMS security Warining have been found")
        testres = False
        for isse in res['issues_n']:
            print (isse)
    else:
        print ("--Checks reported--")
        print (str(res['counts']['ok']) + " checks as ok")
        print (str(res['counts']['warn']) + " checks as warnings")
        print (str(res['counts']['err']) + " checks as erros")
        if (res['counts']['warn'] > 0 or res['counts']['err'] > 0):
            for isse in res['issues_n']:
                print (isse)
        print ("-------------------")

res = totara.check_envextra(url)
if res['finalcheck'] == False:
    totara.maxerr()
    testres = False
    sys.exit("An issue was found with Php")

if testres == True:
    totara.set_maintenancemode(url,'Disable')
    totara.close()
    print ("All Tests came out clear")
else:
    totara.set_maintenancemode(url,'Disable')
    totara.close()
    print ("!!!Some tests shows some issues but nothing to stop LMS running!!!")
