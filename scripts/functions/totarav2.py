#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
import re, string, random, mmap, os, time, datetime, pytz
#Basics

##Loads the webpage
def webb(addr,min):
    global browser
    options = webdriver.FirefoxOptions()
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
    time.sleep(2)
    browser.maximize_window()

##Close the LMS window
def close():
    time.sleep(10)
    browser.quit()

##logins
def login(lguser,lgpass):
    check_loop=0
    loginckh=False
    while( check_loop<70):
        if (re.search('id="page-login-index"', browser.page_source)):
            #check if their is any lick to login page links
            try:
                browser.find_element_by_xpath('//*[@class="showLogin"]').click()
            except Exception as e:
                loginckh = False
            try:
                browser.find_element_by_xpath('//*[@id="togglelogin"]').click()
            except Exception as e:
                loginckh = False
            #ok this where i login you see
            try:
                lg_username = browser.find_element_by_xpath('//*[@id="username"]')
                lg_username.clear()
                lg_username.send_keys(lguser)
                lg_username = browser.find_element_by_xpath('//*[@id="password"]')
                lg_username.clear()
                lg_username.send_keys(lgpass)
                browser.find_element_by_xpath('//*[@id="loginbtn"]').click()
            except Exception as e:
                time.sleep(2)
                print ("Error with login")
                print (e)
            else:
                break
        else:
            if (re.search('id="page-site-index"', browser.page_source) or  re.search('class="usertext"', browser.page_source)):
                print ("OR ready loged in")
                break
            time.sleep(2)
    check_loop=0
    while( check_loop<70):
        if (re.search('id="page-site-index"', browser.page_source) or  re.search('class="usertext"', browser.page_source)):
            break
        else:
            time.sleep(2)
            check_loop = check_loop + 1

#Upgrade
##Confirm Upgrade
def upgrade_confirm(autopass):
    try:
        w = WebDriverWait(browser, 120)
        w.until(EC.title_contains('Administration'))
        w.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='buttons']")))
        if (autopass == True):
            print ("Make sure the version is correct and Press the Continue buttion")
        else:
            print ("Bypasing Manualy Version check")
            browser.find_element_by_xpath('//*[@type="submit" and @value="Continue"]').click()
        w = WebDriverWait(browser, 200)
        w.until(EC.title_contains('Current release information'))
        return True
    except TimeoutException:
        print ("Timeout finding the page or pressing the buttion to Continue")
        return False

def upgrade_witing():
    try:
        w = WebDriverWait(browser, 150)
        if (w.until(EC.title_contains('Upgrading to new version'))):
            print ("Wating for upgrade to complete")
            w = WebDriverWait(browser, 500)
            a_test = w.until(EC.visibility_of_element_located((By.XPATH, "//*[@class='continuebutton']")))
            if (a_test):
                browser.execute_script("window.scrollTo(0,document.body.scrollHeight)")
                return True
    except TimeoutException:
        return False



##enter upgradkey
def upgrade_upgradekey(lms_site,upkey):
    browser.get(lms_site+'/admin/index.php')
    check_loop=0
    while( check_loop<70):
        if (re.search('<div class="upgradekeyreq">', browser.page_source)):
            lg_upgardekey = browser.find_element_by_xpath('//*[@name="upgradekey" and @type="password"]')
            lg_upgardekey.clear()
            lg_upgardekey.send_keys(upkey)
            time.sleep(2)
            browser.find_element_by_xpath('//*[@type="submit" and @value="Submit"]').click()
            break
        else:
            time.sleep(2)
            check_loop = check_loop +1

def update_carryon(btext,timeout):
    try:
        w = WebDriverWait(browser, int(timeout))
        w.until(EC.visibility_of_element_located((By.XPATH, '//*[@type="submit" and @value="'+btext+'"]')))
        browser.find_element_by_xpath('//*[@type="submit" and @value="'+ btext +'"]').click()
        return True
    except TimeoutException:
        print ("Error timeout looking for buttion")
        return False

#Checks
def check_scheduledtasks(lms_site):
    cron_list = []
    time_now = datetime.datetime.now().replace(microsecond=0)
    time_zon = time_now.astimezone(pytz.timezone("Europe/London"))
    cur_time = time_zon.replace(tzinfo=None)
    browser.get(lms_site+'/admin/tool/task/scheduledtasks.php')
    w = WebDriverWait(browser, 120)
    w.until(EC.title_contains('Scheduled tasks'))
    time.sleep(2)
    table_id = browser.find_element_by_xpath('//*[@class="admintable generaltable"]')
    table_body = table_id.find_elements_by_tag_name("tbody")
    for body in table_body:
        body_tr = body.find_elements_by_tag_name("tr")
        for trs in body_tr:
            task_ls = {}
            if (re.search('\*/5 \* \* \*', trs.text)):
                check_name = trs.find_element_by_xpath('th[@class="cell c0"]').text.split("\n")
                check_last = trs.find_element_by_xpath('td[@class="cell c3"]').text
                check_next = trs.find_element_by_xpath('td[@class="cell c4"]').text
                if (check_last == "Never"):
                    check_last = "Never"
                    task_ls['check_last'] = "Never"
                else:
                    check_last_date_time_obj = datetime.datetime.strptime(check_last, '%A, %d %B %Y, %I:%M %p')
                    task_ls['check_last'] = str(check_last_date_time_obj)
                task_ls['name'] = check_name[0]
                if (check_next == "ASAP"):
                    task_ls['check_next'] = check_next
                    task_ls['check_goov'] = True
                    cron_list.append(task_ls)
                else:
                    check_next_date_time_obj = datetime.datetime.strptime(check_next, '%A, %d %B %Y, %I:%M %p')
                    task_ls['check_next'] = str(check_next_date_time_obj)
                    time_delta = (check_next_date_time_obj - cur_time)
                    task_ls['time_delta'] = str(time_delta)
                    task_ls['check_goov'] = False
                    cron_list.append(task_ls)
                return cron_list

#version number
def check_version(lms_site):
    fullversion={}
    browser.get(lms_site+'/admin')
    totara_copyinfo = browser.find_element_by_xpath('//*[@class="totara-copyright"]')
    ver_info = re.findall('Version ([0-9]+).([0-9]+) \(Build\: [0-9]+\.[0-9]+\)',totara_copyinfo.text)
    if (ver_info):
        fullversion['error'] = False
        fullversion['major'] =  ver_info[0][0]
        fullversion['minor'] =  ver_info[0][1]
    else:
        fullversion['error'] = True
        fullversion['errormsg'] = "Cant find version number"
    return fullversion

##Check all plugins ae correct
def check_plugins(lms_site):
    d = dict()
    d['finalcheck'] = True
    if (lms_site != "nourl"):
        browser.get(lms_site+'/admin/plugins.php')
    time.sleep(2)
    check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Plugins overview</h2>', browser.page_source) or re.search('<h1>Plugins check</h1>', browser.page_source) ):
            break
        else:
            time.sleep(2)
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
    time.sleep(2)
    check_loop=0
    while( check_loop<70):
        if (re.search('>Environment</h2>', browser.page_source) or re.search('Server checks</h2>', browser.page_source)):
            break
        else:
            time.sleep(2)
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
            time.sleep(2)
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
    time.sleep(4)
    browser.find_element_by_xpath('//*[@data-l10n-id="about-config-pref-edit-button"]').click()
    time.sleep(4)
    browser_ui_mod_text = browser.find_element_by_xpath('//*[@id="prefs"]/tr[@class="has-user-value "]/td[@class="cell-value"]/form[@id="form-edit"]/input[@type="text"]')
    browser_ui_mod_text.clear()
    browser_ui_mod_text.send_keys(dpath)
    browser.find_element_by_xpath('//*[@id="prefs"]/tr[@class="has-user-value "]/td[@class="cell-edit"]/button[@title="Save"]').click()
    time.sleep(4)
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
            time.sleep(2)
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
        time.sleep(10)
        break

##enable/Disable matiance mode
def set_maintenancemode(lms_site,maiopt):
    browser.get(lms_site+'/admin/settings.php?section=maintenancemode')
    time.sleep(2)
    check_loop=0
    while( check_loop<70):
        if (re.search('page-admin-setting-maintenancemode', browser.page_source)):
            drpCountry = Select(browser.find_element_by_xpath('//*[@name="s__maintenance_enabled"]'))
            if (drpCountry.first_selected_option.text == maiopt ):
                print ("Matiance is oready set as " + maiopt)
            else:
                print ("Setting matiance as " + maiopt)
                browser.find_element_by_xpath("//select[@id='id_s__maintenance_enabled']/option[text()='"+maiopt+"']").click()
                browser.find_element_by_xpath('//*[@type="submit" and @value="Save changes"]').click()
                print ("Saving changes")
                check_loop_2 = 0
                while( check_loop_2<70):
                    if (re.search('Changes saved', browser.page_source)):
                        break
                    else:
                        check_loop_2 = check_loop_2 + 1
                        time.sleep(2)
        else:
            check_loop = check_loop +1
            time.sleep(2)

        break


##Disables content market
def disable_content_market(lms_site,lms_version):
    if (lms_version >= "11"):
#optionalsubsystems
        if (lms_version >= "13"):
            browser.get(lms_site+'/admin/settings.php?section=advancedfeatures_learn')
            stringmatch="<h2>Learn settings</h2>"
        else:
            browser.get(lms_site+'/admin/settings.php?section=optionalsubsystems')
            stringmatch="<h2>Advanced features</h2>"
        check_loop=0
        while( check_loop<70):
            if (re.search(stringmatch, browser.page_source)):
                #enablecontentmarketplaces
                if (browser.find_element_by_xpath('//*[@type="checkbox" and @name="s__enablecontentmarketplaces"]').is_selected() == True):
                    browser.find_element_by_xpath('//*[@type="checkbox" and @name="s__enablecontentmarketplaces"]').click()
                    time.sleep(3)
                    browser.find_element_by_xpath('//*[@type="submit" and @class="form-submit" and @value="Save changes"]').click()
                    check_loop=0
                    while( check_loop<70):
                        if (re.search(stringmatch, browser.page_source)):
                            break
                        else:
                            time.sleep(2)
                            check_loop = check_loop + 1
                break
            else:
                time.sleep(2)
                check_loop = check_loop + 1
#capability
        browser.get(lms_site+'/admin/tool/capability/index.php')
        check_loop=0
        while( check_loop<70):
            if (re.search('<span itemprop="title">Capability overview</span>', browser.page_source)):
                break
            else:
                time.sleep(2)
        capability_select = browser.find_element_by_xpath("//select[@id='id_capability']")
        capability_select.find_element_by_xpath("//option[@value='totara/contentmarketplace:config']").click()
        roles_select = browser.find_element_by_xpath("//select[@id='id_roles']")
        roles_select.find_element_by_xpath("//option[@value='0']").click()

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
                time.sleep(2)
        browser.find_element_by_xpath('//*[@value="Purge all caches"]').click()
        check_loop=0
        while( check_loop<70):
            if (re.search('All caches were purged.', browser.page_source)):
                time.sleep(2)
                break
            else:
                print ("Wating for cache to clear")
                time.sleep(2)

##hide course nav
def hideblock(lms_site,blockname):
    browser.get(lms_site+'/admin/blocks.php')
    check_loop=0
    while( check_loop<70):
        if (re.search('<h2>Blocks</h2>', browser.page_source)):
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
                            time.sleep(10)
            break
        else:
            time.sleep(2)
