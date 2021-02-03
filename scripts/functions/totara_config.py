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

def config_get_upgradekey(filnn):
    with open(filnn, "r") as configfp:
        config_lines = configfp.readlines()
        for i, config_line in enumerate(config_lines):
            if config_line.startswith('$CFG->upgradekey'):
                split = config_line.split('=')
                upkey = split[1].replace("\n","").replace("'","",2).replace(";","",1).replace(" ","")
                return upkey





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
