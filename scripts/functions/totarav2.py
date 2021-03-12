#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from time import sleep
import re
import string
import random
import mmap
import os
#Basics

##Loads the webpage
def webb(addr,min):
    global browser
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk","text/csv")
    profile.set_preference("browser.download.panel.shown", False)
    profile.set_preference("browser.helperApps.alwaysAsk.force", False)
    profile.set_preference("browser.download.dir", "/tmp/")
    browser = webdriver.Firefox(firefox_profile=profile)
    browser.get(addr+"/?saml=off")
    if (min == True):
        browser.minimize_window()

##Maxmise the window
def maxerr():
    sleep (2)
    browser.maximize_window()

##Close the LMS window
def close():
    sleep (10)
    browser.quit()

##logins
def login(lguser,lgpass):
    check_loop=0
    while( check_loop<70):
        if (re.search('id="page-login-index"', browser.page_source)):
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
                    sleep(5)
                    print (e)
                    try:
                        browser.find_element_by_xpath('//*[@class="showlogin"]').click()
                    except Exception as e:
                        sleep(5)
                        print (e)
            else:
                break
        else:
            sleep(2)
    sleep(3)
    check_loop=0
    while( check_loop<70):
        if (re.search('id="page-site-index"', browser.page_source) or  re.search('<span class="usertext">', browser.page_source)):
            break
        else:
            sleep(2)

#Upgrade
##enter upgradkey
def upgrade_upgradekey(lms_site,upkey):
    browser.get(lms_site+'/admin/index.php')
    check_loop=0
    while( check_loop<70):
        if (re.search('<div class="upgradekeyreq">', browser.page_source)):
            lg_upgardekey = browser.find_element_by_xpath('//*[@name="upgradekey" and @type="password"]')
            lg_upgardekey.clear()
            lg_upgardekey.send_keys(upkey)
            sleep(2)
            browser.find_element_by_xpath('//*[@type="submit" and @value="Submit"]').click()
            break
        else:
            sleep(2)
            check_loop = check_loop +1

def upgrade_goon_buttion(value_text):
    check_loop=0
    while( check_loop<70):
        if (browser.find_element_by_xpath('//*[@type="submit" and @value="'+value_text+'"]')):
            browser.find_element_by_xpath('//*[@type="submit" and @value="'+value_text+'"]').click()
            break
        else:
            sleep(2)
            check_loop = check_loop +1

#Checks
##Check all plugins ae correct
def check_plugins(lms_site):
    d = dict()
    d['finalcheck'] = True
    if (lms_site != "nourl"):
        browser.get(lms_site+'/admin/plugins.php')
    sleep (2)
    check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Plugins overview</h2>', browser.page_source) or re.search('<h1>Plugins check</h1>', browser.page_source) ):
            break
        else:
            sleep(2)
    if (re.search('<h1>Plugins check</h1>', browser.page_source) ):
        table_id = browser.find_element_by_xpath('//*[@id="plugins-check"]')
    elif (re.search('<h2>Plugins overview</h2>', browser.page_source)):
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


##Certificates check
#next on list
def check_certs(lms_site):
    print ("on todo list")

##Checks the php extras are ok
def check_envextra(lms_site):
    d = dict()
    d['finalcheck'] = True
    if (lms_site != "nourl"):
        browser.get(lms_site+'/admin/environment.php')
    sleep (2)
    check_loop=0
    while( check_loop<70):
        if (re.search('>Environment</h2>', browser.page_source) or re.search('Server checks</h2>', browser.page_source)):
            break
        else:
            sleep(2)
    table_id = browser.find_element_by_xpath('//*[@id="serverstatus"]')
    row_len=len(table_id.find_elements_by_tag_name("td"))
    rows = table_id.find_elements_by_tag_name("td") # get all of the rows in the table
    td_count=1
    for row in rows:
        td_count + 1
        if (re.search('Check', row.text)):
            plugid = str(td_count)
            d['plugin_m_'+plugid]   = "Environment issue"
            d['plugin_s_'+plugid]   = "error"
            d['finalcheck'] = False
    return d

def check_security(lms_site):
    d = dict()
    issulist = []
    d['counts'] = dict()
    d['counts']['ok'] = 0
    d['counts']['warn'] = 0
    d['counts']['err'] = 0
    check_loop = 0
    browser.get(lms_site+'/report/security/index.php')
    while( check_loop<70):
        if (re.search('Security overview</h2>', browser.page_source)):
            table_id = browser.find_element_by_xpath('//*[@id="securityreporttable"]')
            table_body = table_id.find_elements_by_tag_name("tbody")
            for body in table_body:
                body_tr = body.find_elements_by_tag_name("tr")
                for btr in body_tr:
                    body_td = btr.find_elements_by_tag_name("td")
                    tdinfo = []
                    for btd in body_td:
                        tdinfo.append(btd.text)
                    nams_issue = tdinfo[0]
                    stats_issue = tdinfo[1]
                    if (stats_issue == "OK"):
                        d['counts']['ok'] = d['counts']['ok'] + 1
                    if (stats_issue == "Warning"):
                        d['counts']['warn'] = d['counts']['warn'] + 1
                        issulist.append(nams_issue + " - Warning")
                    if (stats_issue == "Error"):
                        d['counts']['err'] = d['counts']['err'] + 1
                        issulist.append(nams_issue + " - Error")
                d['issues_n'] = issulist
            return d
        else:
            sleep(2)
            check_loop = check_loop + 1
#LMS mods
##Get_reports
def get_reports(lms_site,dpath):
    rport_lists = []
    browser.get("about:config")
    browser.find_element_by_xpath('//*[@id="warningButton"]').click()
    browser_ui_search = browser.find_element_by_xpath('//*[@id="about-config-search"]')
    browser_ui_search.clear()
    browser_ui_search.send_keys("browser.download.dir")
    sleep(4)
    browser.find_element_by_xpath('//*[@data-l10n-id="about-config-pref-edit-button"]').click()
    sleep(4)
    browser_ui_mod_text = browser.find_element_by_xpath('//*[@id="prefs"]/tr[@class="has-user-value "]/td[@class="cell-value"]/form[@id="form-edit"]/input[@type="text"]')
    browser_ui_mod_text.clear()
    browser_ui_mod_text.send_keys(dpath)
    browser.find_element_by_xpath('//*[@id="prefs"]/tr[@class="has-user-value "]/td[@class="cell-edit"]/button[@title="Save"]').click()
    sleep(4)
    browser.get(lms_site+'/totara/reportbuilder/index.php')
    #https://wshelearn.learningnexus.co.uk/totara/reportbuilder/report.php?id=67
    check_loop = 0
    while( check_loop<70):
        ##For totara 10 and + i hope
        if (re.search('<h2>Manage user reports</h2>', browser.page_source)):
            print("Totara 10 +")
            print ("Searching Table")
            table_body = browser.find_element_by_xpath('//*[@id="manage_user_reports"]/tbody')
            table_trs = table_body.find_elements_by_tag_name("tr")
            for trs in table_trs:
                tdinfo = []
                tdinf = trs.find_element_by_xpath('td[@class="cell c0 report_namelinkeditview"]')
                tdinfo.append(tdinf.get_attribute('innerHTML'))
                url = re.search('\(<a href=[\'"]?([^\'" >]+)"', tdinfo[0])
                if url:
                    rport_lists.append(url.group(1))
                else:
                    print ("not added")
        elif(re.search('>User generated Reports</h2>', browser.page_source)):
            print("Totara 9")
            print ("Searching Table")
            table_body = browser.find_element_by_xpath('//*[@class="generaltable"]/tbody')
            table_trs = table_body.find_elements_by_tag_name("tr")
            for trs in table_trs:
                tdinfo = []
                tdinf = trs.find_element_by_xpath('td[@class="cell c0"]')
                tdinfo.append(tdinf.get_attribute('innerHTML'))
                url = re.search('\(<a href=[\'"]?([^\'" >]+)"', tdinfo[0])
                if url:
                    rport_lists.append(url.group(1))
                else:
                    print ("not added")
        else:
            sleep(2)
            check_loop + check_loop + 1
            print("wating")


        #pulling the reports down
        print ("Downloading reports")
        rcount = 0
        for rlsit in rport_lists:
            if (rcount > 9):
                continue
            else:
                browser.get(rlsit)
                browser.find_element_by_xpath('//*[@name="export" and @type="submit" and @value="Export" and @id="id_export"]').click()
                rcount = rcount + 1
        #wait 10 seconds for all reports to finsh downloading
        sleep(10)
        break





##enable/Disable matiance mode
def set_maintenancemode(lms_site,maiopt):
    browser.get(lms_site+'/admin/settings.php?section=maintenancemode')
    sleep (2)
    check_loop=0
    while( check_loop<70):
        if (re.search('page-admin-setting-maintenancemode', browser.page_source)):
            if (re.search('<option value="1" selected="selected">Enable</option>', browser.page_source) and maiopt == 'Enable'  or re.search('<option value="1" selected="selected">Disable</option>', browser.page_source) and maiopt == 'Disable'):
                print ("matiance is oready set as " + maiopt)
                break
            else:
                browser.find_element_by_xpath("//select[@id='id_s__maintenance_enabled']/option[text()='"+maiopt+"']").click()
                browser.find_element_by_xpath('//*[@type="submit" and @value="Save changes"]').click()
                print ("its been set")
        check_loop=0
        while( check_loop<70):
            if (re.search('Changes saved', browser.page_source)):
                print("changes saved")
                break
            else:
                sleep(2)
        else:
            sleep(2)
        break



##Disables content market
def disable_content_market(lms_site,lms_version):
    if (lms_version >= "11"):
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
        td_count=0
        for row in rows:
            td_count += 1
            if (row.text == "Allow"):
                print ("Found role with it enabled now disabling")
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
## Purge the LMS cache
def purgecache(lms_site,lms_version):
    if (lms_version >= "11"):
        browser.get(lms_site+'/admin/purgecaches.php')
        check_loop=0
        while( check_loop<70):
            if (re.search('Purge all caches', browser.page_source)):
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

##hide course nav
def hideblock(lms_site,blockname):
    print ("Disableing " + blockname +" Block")
    browser.get(lms_site+'/admin/blocks.php')
    check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Blocks</h2>', browser.page_source)):
            print("lets do stuff")
            table_id = browser.find_element_by_xpath('//*[@id="compatibleblockstable"]')
            table_body = table_id.find_elements_by_tag_name("tbody")
            for body in table_body:
                body_tr = body.find_elements_by_tag_name("tr")
                for btr in body_tr:
                    if (re.search(blockname, btr.text)):
                        body_td = btr.find_elements_by_tag_name("td")
                        for btd in body_td:
                            testll = btd.find_elements_by_tag_name("a")
                            for leang in testll:
                                if (leang.text == "Hide"):
                                    leang.click()
                                    return
                                else:
                                    break
                            sleep(10)
            break
        else:
            sleep(2)

# LMS install
##lowimportance
#dbname,dbuser,dbpass,adminuser,adminpass,adminemail, sitefullname, siteshortname
def setup_install(lmsdata):
    d = dict()
    d['error'] = False
    check_loop = 0
    sleep(5)
    if ( check_loop>69):
      d['error'] = True
      d['msg'] = "Timeout on page loading"
      return d
    else:
      check_loop=0
    ## Set lanuage
    while( check_loop<70):
        if (re.search('<h2>Choose a language</h2>', browser.page_source)):
            print ("Setting Lanuage")
            browser.find_element_by_xpath("//select[@id='langselect']/option[text()='English (en)']").click()
            browser.find_element_by_xpath('//*[@id="nextbutton"]').click()
            sleep(5)
            break
        else:
            sleep(2)
            check_loop = check_loop + 1

    if ( check_loop>69):
      d['error'] = True
      d['msg'] = "Timeout on page loading"
      return d
    else:
      check_loop=0
    ## Set dataaddress
    while( check_loop<70):
        if (re.search('<h2>Confirm paths</h2>', browser.page_source)):
            print ("Setting Data Paths")
            datafolder_path = browser.find_element_by_xpath('//*[@id="id_dataroot"]')
            datafolder_path_value = datafolder_path.get_attribute('value')
            for val in range(len('sitedata')):
                datafolder_path.send_keys(Keys.BACK_SPACE)
            datafolder_path.send_keys('totara_data')
            browser.find_element_by_xpath('//*[@id="nextbutton"]').click()
            sleep(5)
            if (re.search("alert-error", browser.page_source)): #First error handeling to this :( script
              return "error"
            break
        else:
            sleep(2)
            check_loop = check_loop + 1

    #Set DB driver
    if ( check_loop>69):
      d['error'] = True
      d['msg'] = "Timeout on page loading"
      return d
    else:
      check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Choose database driver</h2>', browser.page_source)):
            print ("Setting Database Driver")
            browser.find_element_by_xpath("//select[@name='dbtype']/option[text()='Improved MySQL (native/mysqli)']").click()
            browser.find_element_by_xpath('//*[@id="nextbutton"]').click()
            break
        else:
            sleep(2)
            check_loop = check_loop + 1
    #Set DB creds
#dbname,dbuser,dbpass
    while( check_loop<70):
        if (re.search('<h2>Database settings</h2>', browser.page_source)):
            print ("Setting Database settings")
            db_name = browser.find_element_by_xpath('//*[@id="id_dbname"]')
            db_name.clear()
            db_name.send_keys(lmsdata['db']['name'])
            db_user = browser.find_element_by_xpath('//*[@id="id_dbuser"]')
            db_user.clear()
            db_user.send_keys(lmsdata['db']['user'])
            db_pass = browser.find_element_by_xpath('//*[@id="id_dbpass"]')
            db_pass.clear()
            db_pass.send_keys(lmsdata['db']['pass'])
            browser.find_element_by_xpath('//*[@id="nextbutton"]').click()
            sleep(5)
            if (re.search("alert-error", browser.page_source) or re.search("alert-danger", browser.page_source)): #First error handeling to this :( script20      d['error'] = True
              d['msg']   = "Error found on screen"
              d['error'] = True
              return d
            break
        else:
            sleep(2)
            check_loop = check_loop + 1
    #wait till page loads
    if ( check_loop>69):
      d['error'] = True
      d['msg'] = "Timeout on page loading"
      return d
    else:
      check_loop=0
    while( check_loop<70):
        if (re.search('Copyright notice</h2>', browser.page_source)):
            print ("Agreeing to Copyright")
            browser.find_element_by_xpath('//*[@type="submit"]').click()
            break
        else:
            sleep(2)
            check_loop = check_loop + 1
    #Checking server checks
    if ( check_loop>69):
      d['error'] = True
      d['msg'] = "Timeout on page loading"
      return d
    else:
      check_loop=0
    print ("Checking for possable issues")
    while( check_loop<70):
        check_loop = check_loop + 1
        if (re.search('<h2>Server checks</h2>', browser.page_source)):
            if (re.search('label-danger">Check', browser.page_source) or re.search('label-warning">Check', browser.page_source)):
              if (re.search('label-warning">Check', browser.page_source)):
                  d['error'] = True
                  d['msg']   = "Warning Found"
                  return d
            else:
                print ("Installing LMS")
                browser.find_element_by_xpath('//*[@type="submit"]').click()
                print ("Install done")
                if ( check_loop>69):
                  d['error'] = True
                  d['msg'] = "Timeout on page loading"
                  return d
                else:
                  check_loop=0
                while( check_loop<70):
                    if (re.search('<input type="submit" value="Continue"', browser.page_source)):
                        print ("Install of LMS Compleated")
                        browser.find_element_by_xpath('//*[@type="submit"]').click()
                        break
                    else:
                        print ("Wating to carry on")
                        sleep(5)
                        check_loop = check_loop + 1
            break
        else:
          sleep(2)
          check_loop = check_loop + 1
    ##Wating for install to complete
        if ( check_loop>69):
          d['error'] = True
          d['msg'] = "Timeout on page loading"
          return d
        else:
          check_loop=0
    ##Set admin password
    while( check_loop<70):
        if (re.search('id="id_username"', browser.page_source)):
            print ("Setting Admin Password")
            #set up the admin information
            #Admin_username
            admin_username = browser.find_element_by_xpath('//*[@id="id_username"]')
            admin_username.clear()
            admin_username.send_keys(lmsdata['admin']['user'])
            #admin_password
            admin_password = browser.find_element_by_xpath('//*[@id="id_newpassword"]')
            admin_password.clear()
            admin_password.send_keys(lmsdata['admin']['pass'])
            #admin_email
            admin_email = browser.find_element_by_xpath('//*[@id="id_email"]')
            admin_email.clear()
            admin_email.send_keys(lmsdata['admin']['email'])
            #Hide email address
            browser.find_element_by_xpath("//select[@name='maildisplay']/option[text()='Hide my email address from everyone']").click()
            browser.find_element_by_xpath('//*[@id="id_submitbutton"]').click()
            print ("Subbmited admin creds")
            if (re.search('class="error"', browser.page_source)):
                print ("Error At page source")
                d['error'] = True
                d['msg']   = "Error at setting Admin password"
                return d
            break
        else:
            sleep(2)
            check_loop = check_loop + 1
    #setLMS name
    if ( check_loop>69):
      d['error'] = True
      d['msg'] = "Timeout on page loading"
      return d
    else:
      check_loop=0
    print ("Settinng LMS Name")
    while( check_loop<70):
        if (re.search('id="id_s__fullname"', browser.page_source)):
            site_fullname = browser.find_element_by_xpath('//*[@id="id_s__fullname"]')
            site_fullname.clear()
            site_fullname.send_keys(lmsdata['site']['fullname'])
            site_shortname = browser.find_element_by_xpath('//*[@id="id_s__shortname"]')
            site_shortname.clear()
            site_shortname.send_keys(lmsdata['site']['shortname'])
            browser.find_element_by_class_name("form-submit").click()
            sleep(10)
            break
        else:
            sleep(2)
            check_loop = check_loop + 1
    if ( check_loop>69):
      d['error'] = True
      d['msg'] = "Timeout on page loading"
      return d
    else:
      check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Totara registration</h2>', browser.page_source)):
            print ("Registering LMS")
            browser.find_element_by_xpath("//select[@name='sitetype']/option[text()='Development']").click()
            browser.find_element_by_xpath('//*[@id="id_submitbutton"]').click()
            sub_check_loop=0
            while( sub_check_loop<70):
                if (re.search('Totara registration was updated</div>', browser.page_source)):
                    print ("Totara Been registred")
                    break
                else:
                    sleep(2)
                    sub_check_loop = sub_check_loop + 1
            break
        else:
            sleep(2)
            check_loop = check_loop + 1
    return d


## modfy the freshinstall
def modify_addusers(lmsdata):
    d = dict()
    d['error'] = False
    browser.get(lmsdata['url']+'/user/editadvanced.php?id=-1&returnto=profile')
    check_loop = 0
    while( check_loop<70):
        if (re.search('Add a new user</h2>', browser.page_source)):
            print (lmsdata['first'] + ' ' + lmsdata['last'])
            browser.find_element_by_xpath('//*[@id="id_username"]').send_keys(lmsdata['username'])
            browser.find_element_by_xpath('//*[@id="id_createpassword"]').click()
            #firstname
            browser.find_element_by_xpath('//*[@id="id_firstname"]').send_keys(lmsdata['first'])
            #lastname
            if (lmsdata['isadmin'] == 'true'):
                browser.find_element_by_xpath('//*[@id="id_lastname"]').send_keys(lmsdata['last'] + '(lnadmin)')
            else:
                browser.find_element_by_xpath('//*[@id="id_lastname"]').send_keys(lmsdata['last'])
            browser.find_element_by_xpath('//*[@id="id_email"]').send_keys(lmsdata['email'])
            browser.find_element_by_xpath("//select[@id='id_maildisplay']/option[text()='Hide my email address from everyone']").click()
            #smituser
            browser.find_element_by_xpath('//*[@id="id_submitbutton"]').click()
            check_loop=0
            while( check_loop<70):
                if (re.search('class="userprofile">', browser.page_source) or re.search('Add a new user</h2>', browser.page_source)):
                    if (re.search('class="error"', browser.page_source)):
                        d['error'] = True
                        d['msg']   = "Creating user check page"
                        return d
                    break
            break
        else:
            sleep(2)
            check_loop = check_loop + 1
    return d

def modify_settheme(lmsurl,themename):
    print ("To do")
    browser.get(lmsurl+'/theme/index.php')
    check_loop = 0
    while( check_loop<70):
        if (re.search('<h2>Select device</h2>', browser.page_source)):
            browser.find_element_by_xpath('//*[@type="submit" and @value="Change theme"]').click()
            check_loop = 0
            while( check_loop<70):
                if (re.search('<h2>Select theme for default device</h2>', browser.page_source)):
                    table_id = browser.find_element_by_xpath('//*[@id="adminthemeselector"]')
                    table_body = table_id.find_elements_by_tag_name("tbody")
                    for body in table_body:
                        body_tr = body.find_elements_by_tag_name("tr")
                        for btr in body_tr:
                            body_td = btr.find_elements_by_tag_name("td")
                            for btd in body_td:
                                if (re.search('<input type="hidden" name="choose" value="'+themename+'">', btd.get_attribute('innerHTML'))):
                                    print ("Setting theme " + themename + " as defult")
                                    btd.find_element_by_xpath('//*[@type="submit" and @value="Use theme"]').click()
                                    while( check_loop<70):
                                        if (re.search('<h2>New theme saved</h2>', browser.page_source)):
                                            browser.find_element_by_xpath('//*[@type="submit" and @value="Continue"]').click()
                                            break
                    break
                else:
                    sleep(2)
                    check_loop = check_loop + 1
            break
        else:
            sleep(2)
            check_loop = check_loop + 1

def modify_setadmin(lmsdata):
    browser.get(lmsdata['url']+'/admin/roles/admins.php')
    browser.find_element_by_xpath('//*[@id="addselect_searchtext"]').send_keys(lmsdata['email'])
    select = Select(browser.find_element_by_xpath('//*[@id="addselect"]'))
    select.select_by_visible_text(''+lmsdata['first']+' '+lmsdata['last']+'(lnadmin) ('+lmsdata['username']+', '+lmsdata['email']+')')
    browser.find_element_by_xpath('//*[@id="add"]').click()
    sleep(4)
    browser.find_element_by_xpath('//*[@type="submit" and @value="Continue"]').click()
    sleep(5)

def modify_antivirus(lmsdata):
    print("Set clamv")
    pathtoclam_orset = False
    pathtounixsocket = False
    if (lmsdata['version'] >= "11"):
        browser.get(lmsdata['url']+'/admin/settings.php?section=antivirussettingsclamav')
        check_loop=0
        while( check_loop<70):
            if (re.search('<h2>ClamAV antivirus</h2>', browser.page_source)):
                if (browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtoclam"]').get_attribute('value') == lmsdata['pathtoclam'] ):
                    print ("oready set")
                    pathtoclam_orset = True
                else:
                    if ( browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtoclam"]').get_attribute('readonly')):
                        print ("Path is read only")
                    else:
                        browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtoclam"]').clear()
                        browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtoclam"]').send_keys(lmsdata['pathtoclam'])

                if (browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtounixsocket"]').get_attribute('value') == lmsdata['pathtoclam'] ):
                    print ("oready set")
                    pathtounixsocket = True
                else:
                    if ( browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtounixsocket"]').get_attribute('readonly')):
                        print ("Path is Ready only")
                    else:
                        browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtounixsocket"]').clear()
                        browser.find_element_by_xpath('//*[@id="id_s_antivirus_clamav_pathtounixsocket"]').send_keys(lmsdata['pathtounixsocket'])
                browser.find_element_by_xpath("//select[@id='id_s_antivirus_clamav_clamfailureonupload']/option[text()='Treat files like viruses']").click()
                browser.find_element_by_xpath("//select[@id='id_s_antivirus_clamav_runningmethod']/option[text()='Command line']").click()
        #        browser.find_element_by_xpath("//select[@id='id_s_antivirus_clamav_runningmethod']/option[text()='Unix domain socket']").click()
                if (pathtounixsocket == False and pathtoclam_orset == False):
                    browser.find_element_by_class_name("form-submit").click()
                    sleep(2)
                    check_loop=0
                    while( check_loop<70):
                        if (re.search('Changes saved', browser.page_source)):
                            break
                        else:
                            sleep(2)
                            check_loop = check_loop + 1
                break
            else:
                sleep(2)




def setup_modify(lmsdata):
    d = dict()
    d['error'] = False
    print ("Todo next")
    print ("Set users up")
    for usr in lmsdata['users']:
        tmpdata = {}
        tmpdata['url'] = lmsdata['site']['url']
        tmpdata['first'] = usr['first']
        tmpdata['last'] = usr['last']
        tmpdata['username'] = usr['username']
        tmpdata['email'] = usr['email']
        tmpdata['isadmin'] = usr['isadmin']
        res = modify_addusers(tmpdata)
        if (res['error'] == False):
            if (usr['isadmin'] == 'true'):
                print ('Making user a Admin')
                modify_setadmin(tmpdata)
        else:
            d['error'] = True
            d['msg'] = res['msg']
            return d
    print ("Set antivirus")
    tmpdata = {}
    tmpdata['url'] = lmsdata['site']['url']
    tmpdata['version'] = lmsdata['site']['major_version']
    tmpdata['pathtoclam'] = lmsdata['site']['avsettings']['clamavpath']
    tmpdata['pathtounixsocket'] = lmsdata['site']['avsettings']['clamavsocket']
    modify_antivirus(tmpdata)
    modify_settheme(tmpdata['url'],'lnroots')

    print ("Set security")
    return d
