#!/usr/bin/env python
#!/usr/bin/env python
import os, shutil, sys, tempfile, zipfile, glob
from git import Repo
from git import Git
import includes.modsdb as modsdb
from distutils.dir_util import copy_tree
lms_mods_store = modsdb.lms_mods_store_path

######################
def copyDirectory(src, dest):
    try:
        copy_tree(src, dest)
    # Directories are the same
    except shutil.Error as e:
        print('Directory not copied. Error: %s' % e)
    # Any error saying that the directory doesn't exist
    except OSError as e:
        print('Directory not copied. Error: %s' % e)
######################


def pull(lmsdata):
    frompath = lms_mods_store + lmsdata['address']
    topath = lmsdata["modspath"]
### this has just gotten much much harder indeed
    ## Need to check if their is an git entry and pull from their
    for x in modsdb.repos:
        modfound = False
        if x['domain'] == lmsdata['address']:
            print ("Found and pulling now")
            repofolder = topath
            git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no'
            print ("Getting using Git")
            try:
                with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                    gitrepo = Repo.clone_from(x['repo'], repofolder, branch=x['branch'])
                if os.path.exists(repofolder + "/.git"):
                    shutil.rmtree(repofolder +"/.git")
                if os.path.exists(repofolder + "/readme.md"):
                    os.remove(repofolder + "/readme.md")
            except Exception as e:
                modfound = False
                sys.exit("Somthing happend " + e)
            else:
                print ("Pull done")
                modfound = True

    #If not found in the modsdb.repo arrey checks if the domain found in frompath
    if (os.path.exists(frompath) is False and modfound is False):
        ##If not then pull then from current LMS files
        print ("tempery to pull theme mods from currentLMS")
        os.mkdir(frompath)
        currenttheme = lmsdata["currentlmspath"] + '/theme/lnroots/'
        pixfolder = currenttheme + '/pix'
        stylfolder = currenttheme + '/style'
        tmpthemepath = lmsdata["tmpfolder"] + "/theme/lnroots"
        fromthemepath = frompath + "/theme/lnroots"
        print ("pull theme data")
        copyDirectory(currenttheme,tmpthemepath)
        #remove all files aprt
        themlist = os.listdir(tmpthemepath)
        tokeep = ['config.php','pix','style','java','javascript']
        for item in themlist:
            if item in tokeep:
                print ("Found not removeing")
            else:
                torm = tmpthemepath + '/' + item
                if os.path.isfile(torm) is True:
                    os.remove(torm)
                if os.path.isdir(torm) is True:
                    shutil.rmtree(torm)
        #clear out style folder
        themlist = os.listdir(tmpthemepath + '/style')
        todel = ['lnroots-noprocess.css','totara.css','totara-rtl.css']
        for item in todel:
            if item in todel:
                torm = tmpthemepath + '/style' + '/' + item
                print ("removng: -> " + torm)
                if os.path.isfile(torm) is True:
                    os.remove(torm)
                if os.path.isdir(torm) is True:
                    shutil.rmtree(torm)
        copyDirectory(tmpthemepath,fromthemepath)
        shutil.rmtree(tmpthemepath)
##need to dop the same for certificates
        print ("tempery to pull certificate mods from currentLMS")
        currentcertpath = lmsdata["currentlmspath"] + '/mod/certificate/type/'
        tmpcertpath = lmsdata["tmpfolder"] + "/mod/certificate/type/"
        fromcertpath = frompath + "/mod/certificate/type/"
        print ("pull certificates data")
        copyDirectory(currentcertpath,tmpcertpath)
        certlist = os.listdir(tmpcertpath)
        todel = ['A4_embedded','letter_embedded','A4_non_embedded','letter_non_embedded']
        for item in todel:
            if item in todel:
                torm = tmpcertpath + item
                print ("removng: -> " + torm)
                if os.path.isfile(torm) is True:
                    os.remove(torm)
                if os.path.isdir(torm) is True:
                    shutil.rmtree(torm)
        copyDirectory(tmpcertpath,fromcertpath)
        shutil.rmtree(tmpcertpath)

    if (os.path.exists(frompath) is True and modfound is False):
        ##If it is found (one way or anouther) its copyed to the tmp foder
        try:
            copyDirectory(frompath, topath)
            print ("!!Removing git stuff!!")
            if os.path.exists(topath + "/.git"):
                shutil.rmtree(topath +"/.git")
            if os.path.exists(topath + "/readme.md"):
                os.remove(topath + "/readme.md")
        except Exception as e:
            sys.exit("Somthing happend " + e)
    else:
        print("No mods found")
