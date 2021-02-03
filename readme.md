# Auto Tasks V2

An upgraded try at creating automated steps to help upgrade Totara LMS

## Setup and Use

You need to install the python requirments listed in requirments.txt
as well as have access to all needed git repoes (sshkeys)

## Scripts

### Functions (folder)

#### Get_lms_mods.py
This script is used with genlmspackage.py, to
* Get the mods from source location
* Or if their is no matching domain in the source location, pull from the current LMS folder this will pull mods for only
  * Theme
  * Certificates

#### totara.py
Using selenium, I created some totara function, that are usful, their is steps to auto install and new LMS if needed (but not used in an while)

#### Get_lms_plugins.py
This script is used with genlmspackage.py, to
* Get the plugins from source locations (git, moodle site)
* Copy the plugin from the current lms folder

### includes

#### plugindb.py
This is an list of all plugins names and
* The location where they are installed
* Where pulled from current-lms folder
* What repors and locations to get the source from

### modsdb.py (example in repo)
This is an list of all the customer LMS mods stored in guthub
as this contains LMS address only an blank example is stored on the repo

### installdb.py (example in repo)
This is an list of all the servers with the correct paths for clamav and users that need to be added. As this contains LMS address only an blank example is stored on the repo


### Configgen.py
This file makes a upgarde.json file and the folders needed to start the upgarde, with added encryption for ftp password storage
Runs on windows and linux

All scritps runs on linux only (due to file paths and extra software)

### lmsupgradeprep.py
When the current-lms is pulled down, it Will
* it will unpack the current LMS
* Pass through any plugins that are not being upgraded
* Pull any plugins from source locations
* Pull mods, if not in store repo
* Install mods, from repo
* Create packages up new LMS zip file

### lmsupgradedo.py
to be done soon

### lmsinstallprep.py
This script preps the install package ready for deployment
* added the LNroot
* adds any plugins required
* adds any modes they have been created

### lmsinstalldo.py
This script goes through the stages of install and modding the LMS
* The install/setup process
  * Sets DB up
  * Sets data Paths
  * Sets the admin password
* Tells the user to make changes to the config.php
* Also does the LMS mods for Learning Nexus  
  * Adds Users
  * Sets Users as Admins
  * Sets ClamAV settings
  * Goes though install process
  * Sets the lnroots theme
* Tells the user to make changes to the config.php
* Then Runs same checks as lmscheck.py does

### lmschanges.py
This, script logins a an user defined in the upgarde.json file,
* Will clear the cache of the LMS
* On versions 10 and above will disable "Content Market", service

### lmscheck.py (To do list)
This script can be used for testing some thing things being missed out
* Check custom Certificates (Need to add these)
* Checking All plugins are correct
* Environment settings are correct
* Checking Security Settings


### regenzip.py
This script remakes the packed up zip file from the data pulled from lmsupgradeprep

### lmslogin.py
using the login info from the config file it logs you in to the LMS
