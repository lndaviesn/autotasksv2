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

print ("I am about to make change to the LMS that are required")

url = "https://" + data['lmsaddress']
totara.webb(url,False)
totara.login(decryt(data['lmsserver_user']),decryt(data['lmsserver_pass']))

versplit = data['lmsupgardeversion'].split('.')
ver_major = versplit[0]
ver_minor = versplit[1]
print (ver_major)
if (int(ver_major) >= 10):
    print ("Disabling Content Market")
    totara.disable_content_market(url,ver_major)
    print ("Content Market Disabled ")

#Clear cache
if (int(ver_major) >= 9):
    print ("Purging Cache")
    totara.purgecache(url,ver_major)
    print ("Cache Purged")

if (int(ver_major) >= 12):
    totara.hideblock(url,'Course navigation')



##clouse the LMS page
totara.close()
