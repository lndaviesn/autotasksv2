#!/usr/bin/env python
import os, shutil, sys, tempfile, glob, sqlite3, requests
from zipfile import ZipFile
from git import Repo
from git import Git
import includes.plugindb as plugindb
import functions.globalfun as glfun
from distutils.dir_util import copy_tree

def pull(plugindata, lmsdata):
    plugin_found = False
    print ("Looking for " + plugindata['pluginname'])
    print ("will pull from current lms files")
    for x in plugindb.paths:
        if x['name'] == plugindata['pluginname']:
            print ("Found and coping now")
            if (lmsdata['version_major'] == "13"):
                copyingfrom = lmsdata["currentlmspath"] + "/server/" + x['path']
            else:
                copyingfrom = lmsdata["currentlmspath"] + "/" + x['path']
            copyingto = lmsdata["pluginspath"] + "/" + x['path']
            try:
                glfun.copyDirectory(copyingfrom, copyingto)
            except Exception as e:
                plugin_found == False
                sys.exit("Somthing happend " + e)
            else:
                plugin_found = True

    if (plugin_found == False):
        sys.exit("!!!ERROR: Plugin not found or not copyed over!!!")

#get
def get(plugindata, lmsdata):
    plugin_found = False
    print ("Looking for " + plugindata['pluginname'])
    for x in plugindb.new:
        if x['name'] == plugindata['pluginname'] and x['lmsversion'] == lmsdata['version_major']:
            if x['media'] == "curl":
                print ("Found pulling from website")
                filedump = lmsdata["tmpfolder"] + "/filedump/"
                url = x['repo']
                os.mkdir(filedump)
                #checks if the repo is an zip file
                if url.find('.zip') != -1:
                    print ("Found zip content")
                    savefilepath = filedump + "/" + x['name'] + ".zip"
                    copyto = lmsdata["pluginspath"] + "/" + x['path']
                    r = requests.get(url, allow_redirects=True)
                    open(savefilepath, 'wb').write(r.content)
                    with ZipFile(savefilepath, 'r') as zipObj:
                        # Extract all the contents of zip file in different directory
                        try:
                            zipObj.extractall(copyto)
                        except Exception as e:
                            plugin_found == False
                            sys.exit("Somthing happend " + e)
                        else:
                            print('File is unzipped in plugins folder')
                            plugin_found = True
                            shutil.rmtree(filedump)

            if x['media'] == "git":
                #clone the repo to an gitdump folder and then copys to the pulgins folder
                print ("Found pulling from git repo")
                gitdump = lmsdata["tmpfolder"] + "/gitdump/"
                repofolder = gitdump + "/" + x['path']
                git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no'
                print ("Getting using Git")
                try:
                    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                        gitrepo = Repo.clone_from(x['repo'], repofolder, branch=x['branch'])
                    glfun.gitclear(repofolder)
                    copyingfrom = gitdump + "/" + x['path']
                    copyingto = lmsdata["pluginspath"] + "/" + x['path']
                    glfun.copyDirectory(copyingfrom, copyingto)
                except Exception as e:
                    plugin_found == False
                    sys.exit("Somthing happend " + e)
                else:
                    shutil.rmtree(gitdump)
                    plugin_found = True
    if (plugin_found == False):
        sys.exit("!!!ERROR: Plugin not found or copyed!!!")
