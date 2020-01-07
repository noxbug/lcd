import os
import re
import email
import imaplib
import subprocess

# %% custom exception class
#class SenderNotTrustedError(Exception):
#    pass
#
#class NoAttachmentError(Exception):
#    pass

# %% get path of current file
dirname = os.path.dirname(os.path.abspath(__file__))

# %% login
CREDENTIALS = {}
with open(os.path.join(dirname, 'credentials')) as fid:
    CREDENTIALS['HOST'] = fid.readline().rstrip()
    CREDENTIALS['USER'] = fid.readline().rstrip()
    CREDENTIALS['PASS'] = fid.readline().rstrip()

imap = imaplib.IMAP4_SSL(CREDENTIALS['HOST'])
imap.login(CREDENTIALS['USER'], CREDENTIALS['PASS'])

# %% open inbox
imap.select('Inbox')
ack, data = imap.search(None, 'ALL')
mid = data[0].split()[-1]  # select last email

# %% message loop
for mid in data[0].split()[-5:]:
    # %% download email header
    ack, raw = imap.fetch(mid, '(RFC822.HEADER UID)')
    mail = raw[0][1].decode()
    uid = re.search('(\d+)', raw[1].decode()).group(1)
    header = email.message_from_string(mail)
    
    # %% validate sender
    sender = re.search(r'<(.+?)>', header.get('From')).group(1)
    with open(os.path.join(dirname, 'whitelist')) as fid:
        whitelist = fid.read()
        if sender in whitelist:
            pass
        else:
            # raise SenderNotTrustedError('Error: ' + sender + 'not in whitelist')
            continue
    
    # %% has attachement
    if header['X-MS-Has-Attach'] == 'yes':
        pass
    else:
        # raise NoAttachmentError('Error: no attachment found')
        continue
    
    # %% download full email
    ack, mail = imap.fetch(mid, 'RFC822')
    mail = mail[0][1].decode()
    message = email.message_from_string(mail)
    
    # %% download email attachment
    file_type = ['pdf', 'jpg', 'png']
    for part in message.walk():
        content_type = part.get_content_type()
        if any([x in content_type for x in file_type]):
            file_name = part.get_filename()
            path = os.path.join(os.path.expanduser('~'), 'Downloads', file_name)
            with open(path, 'wb') as fid:
                fid.write(part.get_payload(decode=True))
            
            # %% print attachment
            print('Attachment saved: ' + path)
            # print attachment
            print(subprocess.check_output(['lp', path]).decode().rstrip())
            
            # %% delete mail
            # use uid since messages are renumbered after deletion
            # imap.copy(mid,'Deleted')
            # imap.store(mid, '+FLAGS', '\\Deleted')
            imap.uid('COPY', uid, 'Deleted')
            imap.uid('STORE', uid , '+FLAGS', '\\Deleted')

# %% close connection
imap.expunge()            
imap.close()