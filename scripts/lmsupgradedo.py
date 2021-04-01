#!/usr/bin/env python
import functions.totarav2 as totara
import cryptography
from cryptography.fernet import Fernet
import os, shutil, sys, glob, tempfile, json, time, getopt
from os.path import basename
import functions.gpg as gpg
import functions.globalfun as glfun

##extra opst settings
#need to set the options to true first
opt_rcheck = True
opt_cronwait = True
opt_nocontinue = True
opt_notoclose = True
opt_rnodiff = True
opt_medldiff = True
#options
options, remainder = getopt.getopt(sys.argv[1:], 'ho:v', ['help',
                                                         'h',
                                                         'noreportcheck',
                                                         'nocronwait',
                                                         'nocontinue',
                                                         'notoclose',
                                                         'noreportdiff',
                                                         'nomeldcheck'
                                                         ])
for opt, arg in options:
    if opt in ('-h', '--help'):
        print ("-----------------LN LMS upgrade helper----------------")
        print ("* --help or -h: Shows help screen (this screen)")
        print ("* Reporting")
        print ("** --noreportcheck: to disable report downloading and checking")
        print ("** --noreportdiff: to disable report checking only")
        print ("** --nomeldcheck: to disable using medl to maualy compare reports if different")
        print ("* Other")
        print ("** --nocronwait: to disable cronwating (!!for testing only!!)")
        print ("** --nocontinue: to disable auto clicking on continue buttions")
        print ("** --notoclose: Wont close Browser when done")
        print ("------------------------------------------------------")
        quit()
    else:
        if opt in ('--noreportcheck'):
            opt_rcheck = False
        if opt in ('--noreportdiff'):
            opt_rnodiff = False
        if opt in ('--nomeldcheck'):
            opt_medldiff = False
        if opt in ('--nocronwait'):
            print ("Disable Cron wait is for test only and not to be done on live srevers")
            repans = input("Are you sure? [Y/n]:")
            if (repans == "Y" or repans == "y"):
                opt_cronwait = False
            else:
                opt_cronwait = True
        if opt in ('--nocontinue'):
            opt_nocontinue = False
        if opt in ('--notoclose'):
            opt_notoclose = False


spath = os.getcwd()
#added mode for config or upgarde.json file
if os.path.isfile(spath + '/upgrade.json'):
    configpath = spath + '/upgrade.json'

if os.path.isfile(spath + '/config.json'):
    configpath = spath + '/config.json'


f = open(configpath,)
data = json.load(f)

#Added extras to data
lmsrports={}
lmsrports['base'] = spath + '/reports-lms'
lmsrports['old'] = lmsrports['base'] + '/old-lms'
lmsrports['new'] = lmsrports['base'] + '/new-lms'
data['reports']=lmsrports

glfun.createdir(data['reports']['base'])

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
print ("Logging in to LMS")

url = "https://" + data['lmsaddress']
totara.webb(url,False)
totara.login(decryt(data['lmsserver_user']),decryt(data['lmsserver_pass']))
versplit = totara.check_version(url)
print ("Getting Version number")
if (versplit['error'] == False):
    ver_major = versplit['major']
    ver_minor = versplit['minor']
    print ("--> Version: " + ver_major + "." + ver_minor)
else:
    sys.exit(versplit['errormsg'])
###Before-upgrade
#Login to webserver
print ("LMS info")
print ("--> Server Address: " + data['lmsserver_address'])
print ("--> Domain Address: " + data['lmsaddress'])

#Place site in to matiance mode
totara.set_maintenancemode(url,'Enable')

#Ask user to disable cron service
if (opt_cronwait == True):
#    dhold = input("Please disable cron service and press enrter to carry on")
    crondisable = False
    while (crondisable == False):
        sch_check = totara.check_scheduledtasks(url)
        for chk in sch_check:
            if chk['check_goov'] == True:
                print ("Cron been disabled Confirmed")
                crondisable = True
            else:
                print ("Cron not dsabled")
                print ("Wating 1 minutes and will try again")
                time.sleep(60)
                time.sleep(30)
                print ("30 seconds left")
                time.sleep(30)
                crondisable = False




else:
    print ("Cronwait disabled")
    if (opt_rcheck == True):
        #just to give me some time to set reports to be downlaed befor the auto goes through
        print ("I am going to wait for 1 minute so you can set the reports to autodown")
        time.sleep(120)

if (opt_rcheck == True):
    print("Getting reports -> before upgrade")
    #Pull down reports
    glfun.createdir(data['reports']['old'])
    totara.get_reports(url,data['reports']['old'])
else:
    print ("Reporting Grathing Disabled")

###After-upgrade of files
#enter upgrade key if have
try:
    if (data['lmsettings']['config']['upgradekey'] == "null"):
        print ("no LMS upgradkey retrived")
        repans = input("Press enter when upgrade the files on server")
    else:
        print ("Upgrade key: Found -> " + data['lmsettings']['config']['upgradekey'] +" <-" )
        repans = input("Press enter when upgrade the files on server")
        totara.upgrade_upgradekey(url,data['lmsettings']['config']['upgradekey'])

except KeyError:
    print ("no LMS upgradkey retrived")
    repans = input("Press enter when upgrade the files on server")
##After
print ("Approving upgrade request")
totara.upgrade_confirm()
print ("-->Running checks")
res = totara.check_envextra("nourl")
if (res['finalcheck'] == True):
    print ("--->Server Checks are fine")
    if (opt_nocontinue is True):
        if (totara.update_carryon("Continue","120") is False):
            repans = input("Somthing gone wrong press enter to carry on")
            print ("ok carrying on")
    else:
        print ("press the Contuniue buttion")
else:
    print("--->looks to be an issue with server checks")

res = totara.check_plugins("nourl")
if (res['finalcheck'] == True):
    print ("--->Plugins Checks are fine")
    print ("-->Upgrade")
    print ("--->Starting")
    if (opt_nocontinue is True):
        if (totara.update_carryon("Upgrade Totara database now","90000") is False):
            print ("Time out happend (know to happen to upgrade taking longer)")
            if (totara.upgrade_witing() is True):
                print ("--->Compleated")
                repans = input("Press enter to move to the next stage")
            else:
                print ("Somtihng went wrong")
        else:
            if (totara.upgrade_witing() is True):
                print ("-->Upgrade Compleated")
                repans = input("Press enter to move to the next stage")
            else:
                print ("Somtihng went wrong")
    else:
        print ("press the Contuniue buttion")
else:
    print("--->looks to be an issue with plugin checks")
    repans = input("Press enter to move to the next stage")
##Found that may need to reloagin
print ("Check and disable/enable or change settings required")
totara.login(decryt(data['lmsserver_user']),decryt(data['lmsserver_pass']))
time.sleep(5)
##Get new version number
versplit = totara.check_version(url)
print ("Updating Version number")
if (versplit['error'] == False):
    ver_major = versplit['major']
    ver_minor = versplit['minor']
    print ("--> Version: " + ver_major + "." + ver_minor)
else:
    sys.exit(versplit['errormsg'])
#pull down reports
if (opt_rcheck == True):
    print("Getting reports -> after upgrade")
    glfun.createdir(data['reports']['new'])
    totara.get_reports(url,data['reports']['new'])
    ##Basic check reports
    print ("giving 10 seconds for downloads to finsh")
    time.sleep(10)
else:
    print("Reporting Grathing Disabled")
if (opt_rcheck == True and opt_rnodiff == True):
    print("Compaing reports before and after upgrade")
    for reportname in os.listdir(lmsrports['old']):
        print(reportname)
        oldpath=lmsrports['old'] +"/" + reportname
        newpath=lmsrports['new'] +"/" + reportname
        if (os.path.isfile(oldpath) == True and os.path.isfile(newpath) == True):
            if (glfun.gethash(oldpath) == glfun.gethash(newpath) ):
                print ("Files match")
            else:
                print ("!!!Reports do not match!!!")
                print ("Advise checking by hand")
                if (opt_medldiff == True):
                    os.system ("meld " + oldpath + " " + newpath )
                    repans = input("Was the report ok [Y/n]: ")
                    if (repans == "Y" or repans == "y"):
                        print ("Good carrying on")
                    else:
                        repans = input("Dop you want to exit upgrade at this point [Y/n]: ")
                        if (repans == "Y" or repans == "y"):
                            sys.exit("Report was not connect Stoping upgrade")
                else:
                    print ("Manual Reporting Grathing Disabled")
        else:
            print ("Report missing")
else:
    print("Reporting Checking Disabled")

if (opt_notoclose == True):
    print ("-->Closing Browser")
    totara.close()
else:
    print ("Close of browser disabled")
