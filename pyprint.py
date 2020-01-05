import os
import re
import email
import imaplib

# %% custom exception class
#class SenderNotTrustedError(Exception):
#    pass
#
#class NoAttachmentError(Exception):
#    pass

# %% login
CREDENTIALS = {}
with open('credentials') as fid:
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
    with open('whitelist') as fid:
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
    for part in message.walk():
        content_type = part.get_content_type()
        if ('pdf' in content_type):
            file_name = part.get_filename()
            path = os.path.join(os.path.expanduser('~'), 'Downloads', file_name)
            with open(path, 'wb') as fid:
                fid.write(part.get_payload(decode=True))
            print('Attachment saved: ' + path)
        
    # %% delete mail
    imap.copy(mid,'Deleted')
    # use uid since messages are renumbered after deletion
    # imap.store(mid, '+FLAGS', '\\Deleted')
    imap.uid('STORE', uid , '+FLAGS', '\\Deleted')

# %% close connection
imap.expunge()            
imap.close()