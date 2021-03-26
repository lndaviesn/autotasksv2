#!/usr/bin/env python
#!/usr/bin/env python
import os, shutil, sys, tempfile, zipfile, glob
from git import Repo
from git import Git
import includes.modsdb as modsdb
import functions.globalfun as glfun
lms_mods_store = modsdb.lms_mods_store_path

#rebuild with mutple defs
def pull(lmsdata):
    testv = False
    modfound = False
    frompath = lms_mods_store + lmsdata['address']
    topath = lmsdata["modspath"]
    #Ttheir is 2 options to this
# * Have on laptop (could be moded)
    if (os.path.exists(frompath) is True and modfound is False):
        print ("Mods found on System oready")
        try:
            glfun.copyDirectory(frompath, topath)
            if os.path.exists(topath + "/.git"):
                shutil.rmtree(topath +"/.git")
            if os.path.exists(topath + "/readme.md"):
                os.remove(topath + "/readme.md")
            modfound = True
        except Exception as e:
            sys.exit("Somthing happend " + e)

# * Need to check git and pull down
    if (modfound is False):
        for x in modsdb.repos:
            if x['domain'] == lmsdata['address']:
                repofolder = topath
                git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no'
                print ("Found in git Pulling down")
                try:
                    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
                        gitrepo = Repo.clone_from(x['repo'], repofolder, branch=x['branch'])
                    if os.path.exists(repofolder + "/.git"):
                        shutil.rmtree(repofolder +"/.git")
                    if os.path.exists(repofolder + "/readme.md"):
                        os.remove(repofolder + "/readme.md")
                    modfound = True
                except Exception as e:
                    modfound = False
                    sys.exit("Somthing happend " + e)

#need to pull from currentlms
    if (os.path.exists(frompath) is True and modfound is False):
        print ("!!alert this way may not pass all mods!!")
        print ("!!As script only checks theme and certs!!")
        #theme
        current_path = lmsdata["currentlmspath"] + '/theme/lnroots/'
        plugin_path = lmsdata["pluginspath"] + '/theme/lnroots/'
        mod_path = topath + '/theme/lnroots/'
        if os.path.exists(plugin_path):
            #we shall store all the file names in this list
            filelist = []
            for root, dirs, files in os.walk(current_path):
            	for file in files:
                    #append the file name to the list
            		filelist.append(os.path.join(root,file))
            #print all the file names
            for name in filelist:
                current_file = name
                plugin_file = name.replace("currentlms", "plugins")
                mod_file = name.replace(current_path, mod_path)

                if (os.path.exists(plugin_file) is False):
                    print ("File missing: "+ mod_file)
                    os.makedirs(os.path.dirname(mod_file), exist_ok=True)
                    shutil.copyfile(current_file,mod_file)
                    modfound = True
                elif ( glfun.gethash(current_file) != glfun.gethash(plugin_file)):
                    print ("File modifed: "+ mod_file)
                    os.makedirs(os.path.dirname(mod_file), exist_ok=True)
                    shutil.copyfile(current_file,mod_file)
                    modfound = True
        #certs
        current_path = lmsdata["currentlmspath"] + '/mod/certificate/type/'
        plugin_path = lmsdata["pluginspath"] + '/mod/certificate/type/'
        mod_path = topath + '/mod/certificate/type/'

        glfun.copyDirectory(current_path, mod_path)

        #need top copy to frompath with extras
        glfun.copyDirectory(topath, frompath+"-pulldlms")

    if (modfound is False):
        print ("No mods found from any resource")
