#!/usr/bin/env python
import os, shutil, sys, base64, cryptography, json, re
import tkinter as tk
from cryptography.fernet import Fernet
import functions.gpg as gpg

def decryt(encval):
    enctxt = encval.encode()
    decrypted = encryption_type.decrypt(enctxt)
    decrypted = decrypted.decode()
    return decrypted


myjson = {}
arrplugins = []
spath = os.getcwd()
#functions
def addplug():
    tmpmyjson = {}
    tmpmyjson["pluginname"] = txt_lms_plugin_name.get()
    tmpmyjson["pluginversion"] = txt_lms_plugin_ver.get()
    tmpmyjson["pluginupgarde"] = "false"
    arrplugins.append(tmpmyjson)
    txt_lms_plugin_name.delete(0, tk.END)
    txt_lms_plugin_ver.delete(0, tk.END)
    Lb1.insert(tk.END,tmpmyjson["pluginname"] + " - " + tmpmyjson["pluginversion"])


def supg():
    #genertas an key
    key = Fernet.generate_key()
    encryption_type = Fernet(key)
    myjson["lmsaddress"] = txt_lms_domain.get()
    myjson["lmscurrentversion"] = txt_lms_cversion.get()
    myjson["lmsupgardeversion"] = txt_lms_nversion.get()
    myjson["lmsserver_address"] = txt_server_addr.get()

    lms_user_p = txt_lms_user.get().encode()
    encrypted_message = encryption_type.encrypt(lms_user_p)
    myjson["lmsserver_user"] = encrypted_message.decode()

    lms_pass_p = txt_lms_pass.get().encode()
    encrypted_message = encryption_type.encrypt(lms_pass_p)
    myjson["lmsserver_pass"] = encrypted_message.decode()

    myjson["plugins"] = arrplugins
    jsonkey = key.decode("utf-8")
    myjsonsecurekey = gpg.enc(jsonkey)
    myjson["securekey"] = myjsonsecurekey
    try:
        if (re.search(txt_lms_domain.get(), os.getcwd())):
            print ("Oready in folder")
        else:
            os.mkdir(txt_lms_domain.get())
    except OSError:
        print ("Creation of the directory failed" + txt_lms_domain.get())
    else:
        print ("Successfully created the directory" + txt_lms_domain.get())

    try:
        os.mkdir(txt_lms_domain.get()+"/current-lms")
    except OSError:
        print ("Creation of the directory failed current-lms")
    else:
        print ("Successfully created the directory current-lms")

    try:
        os.mkdir(txt_lms_domain.get()+"/backup-lms")
    except OSError:
        print ("Creation of the directory failed backup-lms")
    else:
        print ("Successfully created the directory backup-lms")

    if (re.search(txt_lms_domain.get(), os.getcwd())):
        configpath = "config.json"
    else:
        configpath = txt_lms_domain.get() + "/" + "config.json"

    with open( configpath, 'w', encoding='utf-8') as f:
        json.dump(myjson, f, ensure_ascii=False, indent=4)

    root.quit()


root = tk.Tk()
root.title('Auto LMS setup')
root.geometry('700x400+400+400')
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.option_add("*Font", ("", 13))
host_frame = tk.Frame(root, width=450)
host_frame.grid(row=0, sticky="ew")

plugins_frame = tk.Frame(root, width=450)
plugins_frame.grid(row=1, sticky="ew")

butions_frame = tk.Frame(root, width=450)
butions_frame.grid(row=2, sticky="ew")


lb_lms_domain = tk.Label(host_frame, text='LMS Domain:')
lb_lms_domain.grid(row=1, column=0)
txt_lms_domain = tk.Entry(host_frame)
txt_lms_domain.grid(row=1, column=1)

lb_lms_cversion = tk.Label(host_frame, text='LMS Current Version:')
lb_lms_cversion.grid(row=2, column=0)
txt_lms_cversion = tk.Entry(host_frame)
txt_lms_cversion.grid(row=2, column=1)

lb_lms_nversion = tk.Label(host_frame, text='LMS New Version:')
lb_lms_nversion.grid(row=3, column=0)
txt_lms_nversion = tk.Entry(host_frame)
txt_lms_nversion.grid(row=3, column=1)

lb_server_addr = tk.Label(host_frame, text='Server address:')
lb_server_addr.grid(row=5, column=0)
txt_server_addr = tk.Entry(host_frame)
txt_server_addr.grid(row=5, column=1)

lb_lms_user = tk.Label(host_frame, text='LMS User:')
lb_lms_user.grid(row=6, column=0)
txt_lms_user = tk.Entry(host_frame)
txt_lms_user.grid(row=6, column=1)

lb_lms_pass = tk.Label(host_frame, text='LMS Pass:')
lb_lms_pass.grid(row=7, column=0)
txt_lms_pass = tk.Entry(host_frame, show="*")
txt_lms_pass.grid(row=7, column=1)

#Plugins this is hard get back to that i think
lb_lms_plugin_name = tk.Label(plugins_frame, text='Plugin name:')
lb_lms_plugin_name.grid(row=5, column=0)
txt_lms_plugin_name = tk.Entry(plugins_frame)
txt_lms_plugin_name.grid(row=5, column=1)

lb_lms_plugin_ver = tk.Label(plugins_frame, text='Plugin Version:')
lb_lms_plugin_ver.grid(row=5, column=2)
txt_lms_plugin_ver = tk.Entry(plugins_frame)
txt_lms_plugin_ver.grid(row=5, column=3)
tk.Button(plugins_frame, text="Add", command=addplug, state='normal').grid(column=4, row=5)

Lb1 = tk.Listbox(plugins_frame, width=60)
Lb1.grid(row=6, columnspan=6)
tk.Button(butions_frame, text="Setup", command=supg, state='normal').grid(column=0, row=99)


if __name__ == "__main__":
#allows to update config info
    if os.path.isfile(spath + '/upgrade.json'):
        configpath = spath + '/upgrade.json'
    if os.path.isfile(spath + '/config.json'):
        configpath = spath + '/config.json'
    if configpath !="":
        f = open(configpath,)
        data = json.load(f)
        if 'lmsaddress' in data:
            txt_lms_domain.insert(0, data['lmsaddress'])
        if 'lmscurrentversion' in data:
            txt_lms_cversion.insert(0, data['lmscurrentversion'])
        if 'lmsupgardeversion' in data:
            txt_lms_nversion.insert(0, data['lmsupgardeversion'])
        if 'lmsserver_address' in data:
            txt_server_addr.insert(0, data['lmsserver_address'])
        if 'plugins' in data:
            for plugindata in data['plugins']:
                txt_lms_plugin_name.insert(0, plugindata['pluginname'])
                txt_lms_plugin_ver.insert(0, plugindata['pluginversion'])
                addplug()
        if 'securekey' in data:
            if data['securekey'] != "":
                key = gpg.dec(data['securekey'])
                encryption_type = Fernet(key)
                dec_username = decryt(data['lmsserver_user'])
                txt_lms_user.insert(0, dec_username)
                dec_password = decryt(data['lmsserver_pass'])
                txt_lms_pass.insert(0, dec_password)
#starts the form up
    root.mainloop()
