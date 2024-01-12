import os
import uuid
import imghdr
import requests

from rest_framework.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.contrib.auth import password_validation
from django.core.mail import EmailMultiAlternatives
from django.core import exceptions

MEDIA_AVATAR = 'avatars'
MEDIA_TERAPIE = 'therapies'
MEDIA_EVENTI = 'events'

def handle_upload(field, upload, directory):
    pos = upload.tell()
    upload.seek(0)
    fmt = imghdr.what(upload)
    if fmt is None:
        raise ValidationError('Unsupported image')

    upload.seek(pos)

    oldfile = field.path if field else None
    u = str(uuid.uuid4())
    filename = '%s/%s/%s.%s' % (directory, u[0], u, fmt)
    field.save(filename, upload)

    if oldfile is None or directory=='documents':
        return

    try:
        os.unlink(oldfile)
    except OSError:
        pass

def handle_upload_document(field, upload, directory):
    pos = upload.tell()
    upload.seek(0)
    '''fmt = imghdr.what(upload)
    if fmt is None:
        raise ValidationError('Unsupported image')'''

    upload.seek(pos)

    oldfile = field.path if field else None
    u = str(uuid.uuid4())
    filename = '%s/%s/%s.%s' % (directory, u[0], u, 'pdf')
    field.save(filename, upload)

    if oldfile is None or directory=='documents':
        return

    try:
        os.unlink(oldfile)
    except OSError:
        pass

def download_remote_file(field, url, directory):
    if url is None:
        return

    try:
        r = requests.get(url)
        if r.status_code == 200:
            return handle_upload(field, ContentFile(r.content), directory)
    except requests.exceptions.RequestException as e:
        print e

    raise ValueError('Download error')

def validate_password(password, user=None):
    try:
        password_validation.validate_password(password, user)
    except exceptions.ValidationError as e:
        raise ValidationError({'detail': '\n'.join(e.messages)})

'''def send_mail(self, subject, context, to_email):
    print 'SEND_MAIL'
    subject = loader.render_to_string(subject, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    body = loader.render_to_string(self.email_template_name, context)

    email_message = EmailMultiAlternatives(subject, body, None, [to_email])
    email_message.send()'''

def textsEmail(self, user, mail_type, email, obj):
    if mail_type == 'CREATE_GROUP':
        subject = 'MYMEDBOOK Nuovo gruppo'
        body = 'L\'utente %s %s ha creato e condiviso con te il gruppo %s. \n Accedi subito a www.mymedbook.it' %(user.first_name, user.last_name, obj.name)
    if mail_type == 'EDIT_GROUP':
        subject = 'MYMEDBOOK Modifica gruppo'
        body = 'L\'utente %s %s ha modificato il gruppo di cui fai parte %s. \n Accedi subito a www.mymedbook.it' %(user.first_name, user.last_name, obj.name)
    if mail_type == 'DELETE_GROUP':
        subject = 'MYMEDBOOK Eliminazione di un gruppo'
        body = 'L\'utente %s %s ha eliminato il gruppo di cui fai parte %s. \n Accedi subito a www.mymedbook.it' %(user.first_name, user.last_name, obj.name)
    self.send_mail(subject, body, email)