import tarfile, os
from git import Repo
from git import Git
import functions.globalfun as glfun


def get_file(lmsfile,extratpath):
    if lmsfile.endswith("tar.gz"):
        tar = tarfile.open(lmsfile, "r:gz")
    elif lmsfile.endswith("tar"):
        tar = tarfile.open(lmsfile, "r:")
    tar.extractall(extratpath)
    tar.close()

def get_git(giturl,base,repoloc):
    extratpath = repoloc + "/"+ base
    git_ssh_cmd = 'ssh -o StrictHostKeyChecking=no'
    with Git().custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
        gitrepo = Repo.clone_from(giturl, extratpath, branch=base)
    print ("Removing git folders")
    glfun.gitclear(extratpath)
