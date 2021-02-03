import sys, os, base64, gnupg, getpass

current_user= getpass.getuser()
gpg_email = "nigel.davies@learningnexus.co.uk"
gpg_path="/home/"+current_user+"/.gnupg/"
gpg = gnupg.GPG(gnupghome=gpg_path)
#gpg.use_agent = True


def enc(unencrypted_string):
    #enc the data
    encrypted_data = gpg.encrypt(unencrypted_string)
    encrypted_string = str(encrypted_data)
    message = encrypted_string
    message_bytes = message.encode('ascii')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('ascii')
    #base64 it
    if (encrypted_data.ok == True):
        return base64_message
    else:
        sys.exit("Error Decoding")


def dec(encrypted_string):
    base64_message = encrypted_string
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    encrypted_message = message_bytes.decode('ascii')
    if (gpg.use_agent is False):
        gpgpassword = getpass.getpass(prompt='Enter GPG Password: ')
        decrypted_data = gpg.decrypt(encrypted_message, passphrase=gpgpassword)
    else:
        decrypted_data = gpg.decrypt(encrypted_message)


    if (decrypted_data.ok == True):
        return decrypted_data.data.decode("utf-8")
    else:
        print ('stderr: ', decrypted_data.stderr)
        sys.exit("Error Decoding")
