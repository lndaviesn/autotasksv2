from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
import re
import string
import random
import mmap
import os

def webb(addr):
    global browser
    browser = webdriver.Firefox()
    browser.get(addr+"/?saml=off")
#    browser.minimize_window()

def login(lguser,lgpass):
    check_loop=0
    while( check_loop<70):
        if (re.search('id="page-login-index"', browser.page_source)):
            print ("Found page")
            try:
                lg_username = browser.find_element_by_xpath('//*[@id="username"]')
                lg_username.clear()
                lg_username.send_keys(lguser)
                lg_username = browser.find_element_by_xpath('//*[@id="password"]')
                lg_username.clear()
                lg_username.send_keys(lgpass)
                browser.find_element_by_xpath('//*[@id="loginbtn"]').click()
            except Exception as e:
                sleep(2)
                print (e)
                try:
                    browser.find_element_by_xpath('//*[@class="showLogin"]').click()
                except Exception as e:
                    sleep(2)
                    print (e)
            else:
                print("next")
                break
        else:
            sleep(2)
    sleep(3)
    check_loop=0
    while( check_loop<70):
        if (re.search('id="page-site-index"', browser.page_source)):
            break
        else:
            sleep(2)





def setup_sitelanguage():
    check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Choose a language</h2>', browser.page_source)):
            break
        else:
            sleep(2)
    browser.find_element_by_xpath("//select[@id='langselect']/option[text()='English (en)']").click()
    browser.find_element_by_xpath('//*[@id="nextbutton"]').click()
    sleep(2)

def setup_sitedata():
    check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Confirm paths</h2>', browser.page_source)):
            break
        else:
            sleep(2)
    datafolder_path = browser.find_element_by_xpath('//*[@id="id_dataroot"]')
    datafolder_path_value = datafolder_path.get_attribute('value')
    for val in range(len('sitedata')):
        datafolder_path.send_keys(Keys.BACK_SPACE)
    datafolder_path.send_keys('totara_data')
    browser.find_element_by_xpath('//*[@id="nextbutton"]').click()
    sleep(5)
    if (re.search("alert-error", browser.page_source)): #First error handeling to this :( script
      return "error"

def setup_database(dbname,dbuser,dbpass):
    d = dict()
    check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Choose database driver</h2>', browser.page_source)):
            break
        else:
            sleep(2)
    browser.find_element_by_xpath("//select[@name='dbtype']/option[text()='Improved MySQL (native/mysqli)']").click()
    browser.find_element_by_xpath('//*[@id="nextbutton"]').click()
    check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Database settings</h2>', browser.page_source)):
            break
        else:
            sleep(2)
    db_name = browser.find_element_by_xpath('//*[@id="id_dbname"]')
    db_name.clear()
    db_name.send_keys(dbname)
    db_user = browser.find_element_by_xpath('//*[@id="id_dbuser"]')
    db_user.clear()
    db_user.send_keys(dbuser)
    db_pass = browser.find_element_by_xpath('//*[@id="id_dbpass"]')
    db_pass.clear()
    db_pass.send_keys(dbpass)
    browser.find_element_by_xpath('//*[@id="nextbutton"]').click()
    sleep(5)
    if (re.search("alert-error", browser.page_source) or re.search("alert-danger", browser.page_source)): #First error handeling to this :( script20      d['error'] = True
      d['msg']   = "Error found on screen"
      d['error'] = True
      return d
    else:
      d['error'] = False
      d['msg']   = ""
      return d

def setup_yescopyright():
    #wait till page loads
    check_loop=0
    while( check_loop<70):
        if (re.search('Copyright notice</h2>', browser.page_source)):
            break
        else:
            sleep(2)
    browser.find_element_by_xpath('//*[@type="submit"]').click()


def setup_install_check():
    d = dict()
    #checking the site loaded up
    check_loop=0
    while( check_loop<70):
        check_loop = check_loop + 1
        if (re.search('<h2>Server checks</h2>', browser.page_source)):
          break
        else:
          sleep(2)
    if (re.search('label-danger">Check', browser.page_source) or re.search('label-warning">Check', browser.page_source)):
      if (re.search('label-warning">Check', browser.page_source)):
          d['error'] = True
          d['msg']   = "Warning"
    return d

#need to be split to mini functions
def setup_install():
    #checking the site loaded up
    check_loop=0
    while( check_loop<70):
      if (re.search('<h2>Server checks</h2>', browser.page_source)):
          break
      else:
          sleep(2)
    browser.find_element_by_xpath('//*[@type="submit"]').click()
    check_loop=0
    while( check_loop<70):
        if (re.search('<input type="submit" value="Continue">', browser.page_source)):
             break
        else:
            sleep(5)
    browser.find_element_by_xpath('//*[@type="submit"]').click()

def setup_adminuser(adminuser,adminpass,adminemail):
    d = dict()
    #wait till page loads
    check_loop=0
    while( check_loop<70):
        if (re.search('id="id_username"', browser.page_source)):
            break
        else:
            sleep(2)
    #set up the admin information
    #Admin_username
    admin_username = browser.find_element_by_xpath('//*[@id="id_username"]')
    admin_username.clear()
    admin_username.send_keys(adminuser)
    #admin_password
    admin_password = browser.find_element_by_xpath('//*[@id="id_newpassword"]')
    admin_password.clear()
    admin_password.send_keys(adminpass)
    #admin_email
    admin_email = browser.find_element_by_xpath('//*[@id="id_email"]')
    admin_email.clear()
    admin_email.send_keys(adminemail)
    #Hide email address
    browser.find_element_by_xpath("//select[@name='maildisplay']/option[text()='Hide my email address from everyone']").click()
    browser.find_element_by_xpath('//*[@id="id_submitbutton"]').click()
    if (re.search('class="error"', browser.page_source)):
        d['error'] = True
        d['msg']   = "Error on page"
    else:
        d['error'] = False
        d['msg']   = ""
    return d


def setup_nameinglms(sitefullname,siteshortname):
#Checking if the page will load up
    check_loop=0
    while( check_loop<70):
        if (re.search('id="id_s__fullname"', browser.page_source)):
            break
        else:
            sleep(2)
    sleep(5)
    site_fullname = browser.find_element_by_xpath('//*[@id="id_s__fullname"]')
    site_fullname.clear()
    site_fullname.send_keys(sitefullname)
    site_shortname = browser.find_element_by_xpath('//*[@id="id_s__shortname"]')
    site_shortname.clear()
    site_shortname.send_keys(siteshortname)
    browser.find_element_by_class_name("form-submit").click()


def setup_registerlms():
    sleep(5)
    browser.find_element_by_xpath("//select[@name='sitetype']/option[text()='Development']").click()
    browser.find_element_by_xpath('//*[@id="id_submitbutton"]').click()
    check_loop=0
    while( check_loop<70):
        if (re.search('Totara registration was updated</div>', browser.page_source)):
            break
        else:
            sleep(2)
###############customiseing now

def custom_adduser(lms_site,user_info):
    d = dict()
    check_loop=0
    browser.get(lms_site+'/user/editadvanced.php?id=-1&returnto=profile')
    while( check_loop<70):
        if (re.search('Add a new user</h2>', browser.page_source)):
            break
        else:
            sleep(2)
    browser.find_element_by_xpath('//*[@id="id_username"]').send_keys(user_info['username'])
    browser.find_element_by_xpath('//*[@id="id_createpassword"]').click()
    #firstname
    browser.find_element_by_xpath('//*[@id="id_firstname"]').send_keys(user_info['first'])
    #lastname
    browser.find_element_by_xpath('//*[@id="id_lastname"]').send_keys(user_info['last']+" LN_admin")
    browser.find_element_by_xpath('//*[@id="id_email"]').send_keys(user_info['email'])
    browser.find_element_by_xpath("//select[@id='id_maildisplay']/option[text()='Hide my email address from everyone']").click()
    #smituser
    browser.find_element_by_xpath('//*[@id="id_submitbutton"]').click()
    check_loop=0
    while( check_loop<70):
        if (re.search('class="userprofile">', browser.page_source) or re.search('Administration: Users: Accounts: Add a new user</title>', browser.page_source)):
            break
        else:
            sleep(2)
    if (re.search('class="error"', browser.page_source)):
        d['error'] = True
        d['msg']   = "Creating user check page"
    else:
        d['error'] = False
        d['msg']   = ""
    return d

def custom_makeadmin(lms_site,user_info):
    browser.get(lms_site+'/admin/roles/admins.php')
    browser.find_element_by_xpath('//*[@id="addselect_searchtext"]').send_keys(user_info['email'])
    select = Select(browser.find_element_by_xpath('//*[@id="addselect"]'))
    select.select_by_visible_text(user_info['first']+' '+user_info['last']+' LN_admin ('+user_info['username']+', ' +user_info['email']+')')
    browser.find_element_by_xpath('//*[@id="add"]').click()
    sleep(4)
    browser.find_element_by_xpath('//*[@type="submit" and @value="Continue"]').click()
    sleep(5)



def disable_content_market(lms_site,lms_version):
    if (lms_version >= "11"):
        #http://10.20.56.137/admin/tool/capability/index.php
        browser.get(lms_site+'/admin/tool/capability/index.php')
        check_loop=0
        while( check_loop<70):
            if (re.search('<span itemprop="title">Capability overview</span>', browser.page_source)):
                break
            else:
                sleep(2)
        browser.find_element_by_xpath('//*[@id="capabilitysearch"]').send_keys('totara/contentmarketplace:config')
        browser.find_element_by_xpath('//*[@type="submit" and @value="Get the overview"]').click()
        table_id = browser.find_element_by_xpath('//*[@class="lastrow"]')
        row_len=len(table_id.find_elements_by_tag_name("td"))
        rows = table_id.find_elements_by_tag_name("td") # get all of the rows in the table
        td_count=1
        for row in rows:
            td_count + 1
            if (row.text == "Allow"):
                browser.get(lms_site+'/admin/roles/define.php?action=view&roleid='+str(td_count))
                browser.find_element_by_xpath('//*[@type="submit" and @value="Edit"]').click()
                if (browser.find_element_by_xpath('//*[@type="checkbox" and @name="totara/contentmarketplace:config"]').is_selected() == True):
                    browser.find_element_by_xpath('//*[@type="checkbox" and @name="totara/contentmarketplace:config"]').click()
                if (browser.find_element_by_xpath('//*[@type="checkbox" and @name="totara/contentmarketplace:add"]').is_selected() == True):
                    browser.find_element_by_xpath('//*[@type="checkbox" and @name="totara/contentmarketplace:add"]').click()
                browser.find_element_by_xpath('//*[@type="submit" and @value="Save changes"]').click()
                disable_content_market(lms_site,lms_version)
                break

    else:
        print("Incorect Version ")


def purgecache(lms_site,lms_version):
    if (lms_version >= "11"):
        browser.get(lms_site+'/admin/purgecaches.php')
        check_loop=0
        while( check_loop<70):
            if (re.search('Purge all caches</title>', browser.page_source)):
                break
            else:
                sleep(2)
        browser.find_element_by_xpath('//*[@value="Purge all caches"]').click()
        check_loop=0
        while( check_loop<70):
            if (re.search('All caches were purged.', browser.page_source)):
                sleep(2)
                break
            else:
                print ("Wating for cache to clear")
                sleep(2)




def security(lms_site,lms_version):
    if (lms_version >= "11"):
        browser.get(lms_site+'/admin/settings.php?section=httpsecurity')
        check_loop=0
        while( check_loop<70):
            if (re.search('HTTP security</h2>', browser.page_source)):
                print ("---page-loaded")
                break
            else:
                print ("---wating for page to load")
                sleep(2)
    #cookie http only set
        #check if its or ready been sletdet for
        if (browser.find_element_by_id('id_s__cookiehttponly').is_selected() == False):
            browser.find_element_by_xpath('//*[@id="id_s__cookiehttponly"]').click()
        else:
            print("---cookie http only oready set")
    #cookie https only set
        #check if its or ready been sletdet for
        if (browser.find_element_by_id('id_s__cookiesecure').is_selected() == False):
            browser.find_element_by_xpath('//*[@id="id_s__cookiesecure"]').click()
        else:
            print("---cookie secure oready set")
        browser.find_element_by_xpath('//*[@type="submit" and @value="Save changes"]').click()
        check_loop=0
        while( check_loop<70):
            if (re.search('<div class="alert-message">Changes saved</div>', browser.page_source)):
                print ("---Changes saved next")
                break
            else:
                print ("---Saving changes")
                sleep(2)
    else:
        print("Incorect Version ")



def clamav(lms_site,lms_version,pathtoclam,pathtounixsocket):
    #checks how to
    pathtoclam_orset = False
    pathtounixsocket = False

    if (lms_version >= "11"):
        browser.get(lms_site+'/admin/settings.php?section=antivirussettingsclamav')
        sleep(2)
        check_loop=0
        while( check_loop<70):
            if (re.search('<h2>ClamAV antivirus</h2>', browser.page_source)):
                break
            else:
                sleep(2)

        if (browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtoclam"]').get_attribute('value') == pathtoclam ):
            print ("oready set")
            pathtoclam_orset = True
        else:
            if ( browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtoclam"]').get_attribute('readonly')):
                print ("readonly-true")
            else:
                browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtoclam"]').clear()
                browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtoclam"]').send_keys(pathtoclam)

        if (browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtounixsocket"]').get_attribute('value') == pathtoclam ):
            print ("oready set")
            pathtounixsocket = True
        else:
            if ( browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtounixsocket"]').get_attribute('readonly')):
                print ("readonly-true")
            else:
                browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtounixsocket"]').clear()
                browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtounixsocket"]').send_keys(pathtounixsocket)

        browser.find_element_by_xpath("//select[@id='id_s_antivirus_clamav_clamfailureonupload']/option[text()='Treat files like viruses']").click()

        browser.find_element_by_xpath("//select[@id='id_s_antivirus_clamav_runningmethod']/option[text()='Command line']").click()
#        browser.find_element_by_xpath("//select[@id='id_s_antivirus_clamav_runningmethod']/option[text()='Unix domain socket']").click()

        if (pathtounixsocket == False and pathtoclam_orset == False):
            browser.find_element_by_class_name("form-submit").click()
            sleep(2)
            check_loop=0
            while( check_loop<70):
                if (re.search('Changes saved', browser.page_source)):
                    print ("---Changes saved next")
                    break
                else:
                    print ("---Saving changes")
                    sleep(2)

        print ("--Enable Clamav")
        browser.get(lms_site+'/admin/settings.php?section=manageantiviruses')
        if (re.search('class="flex-icon ft-fw ft fa-eye-slash"', browser.page_source)):
            browser.find_element_by_xpath('//*[@class="flex-icon ft-fw ft fa-eye-slash"]').click()



## Global_settings
def global_settings(lms_site):
    browser.get(lms_site+'/admin/settings.php?section=modsettingfacetoface')
    sleep(2)
    check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Global settings</h2>', browser.page_source)):
            break
        else:
            sleep(2)
            check_loop = check_loop +1
    browser.find_element_by_xpath('//*[@id="id_s__facetoface_fromaddress"]').clear()
    browser.find_element_by_xpath('//*[@id="id_s__facetoface_fromaddress"]').send_keys('noreply@learningnexus.co.uk')
    browser.find_element_by_xpath('//*[@type="submit" and @value="Save changes"]').click()
    sleep(2)
    check_loop=0
    while( check_loop<70):
        if (re.search('Changes saved', browser.page_source)):
            break
        else:
            sleep(2)
            check_loop = check_loop +1




###config path

def config_add_upgradekey(config_path,upgradekey):
    line_count = sum(1 for line in open(config_path)) -3
    with open(config_path, 'r+') as f: #r+ does the work of rw
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith('$CFG->admin'):
                print("found admin")
                if ( not upgradekey == '' ):
                    found_upgradekey=False
                    for lr in range(0, line_count-i):
                        if (lines[i+lr].startswith('$CFG->upgradekey')):
                            found_upgradekey=True
                    if (found_upgradekey == False):
                        lines.insert(i+2,'$CFG->upgradekey = \''+upgradekey+'\';\n')
                else:
                    print("---no upgrade key set")
        tf=open(config_path+'.tmp', 'w')
        for line in lines:
            tf.write(line)
        tf.close()
        f.close()
        os.remove(config_path)
        os.rename(config_path+'.tmp',config_path)


def config_add_preventexecpath(config_path):
    line_count = sum(1 for line in open(config_path)) -3
    with open(config_path, 'r+') as f: #r+ does the work of rw
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith('$CFG->admin'):
                print("found admin")
                found_preventexecpath=False
                for lr in range(0, line_count-i):
                    if (lines[i+lr].startswith('$CFG->preventexecpath')):
                        found_preventexecpath=True
                if (found_preventexecpath == False):
                    lines.insert(i+1,'$CFG->preventexecpath = false;\n')
        tf=open(config_path+'.tmp', 'w')
        for line in lines:
            tf.write(line)
        tf.close()
        f.close()
        os.remove(config_path)
        os.rename(config_path+'.tmp',config_path)

def config_section_disable(what,config_path):
    with open(config_path, 'r') as file :
        filedata = file.read()
         # Replace the target string
        if (filedata.find('// $CFG->'+what) < 0):
            print ("---"+what+" is Disabled")
            filedata = filedata.replace('$CFG->'+what, '// $CFG->'+what)
        else:
            with open(config_path+'.tmp', 'w') as file:
                file.write(filedata)
            os.remove(config_path)
            os.rename(config_path+'.tmp',config_path)

def maintenance(lms_site,maiopt):
    browser.get(lms_site+'/admin/settings.php?section=maintenancemode')
    sleep (2)
    check_loop=0
    while( check_loop<70):
        if (re.search('page-admin-setting-maintenancemode', browser.page_source)):
            break
        else:
            sleep(2)
    browser.find_element_by_xpath("//select[@id='id_s__maintenance_enabled']/option[text()='"+maiopt+"']").click()
    browser.find_element_by_xpath('//*[@type="submit" and @value="Save changes"]').click()
    check_loop=0
    while( check_loop<70):
        if (re.search('Changes saved', browser.page_source)):
            break
        else:
            sleep(2)


def check_plugins(lms_site):
    d = dict()
    d['finalcheck'] = True
    browser.get(lms_site+'/admin/plugins.php')
    sleep (2)
    check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Plugins overview</h2>', browser.page_source)):
            break
        else:
            sleep(2)
    table_id = browser.find_element_by_xpath('//*[@id="plugins-control-panel"]')
    row_len=len(table_id.find_elements_by_tag_name("td"))
    rows = table_id.find_elements_by_tag_name("td") # get all of the rows in the table
    td_count=1
    for row in rows:
        td_count + 1
        if (re.search('Missing from disk!', row.text)):
            plugid = str(td_count)
            d['plugin_m_'+plugid]   = "Found plugin missing from disk!!"
            d['plugin_s_'+plugid]   = "error"
            d['finalcheck'] = False

    return d


def maxerr():
    sleep (2)
    browser.maximize_window()


def close():
    sleep (10)
    browser.quit()
