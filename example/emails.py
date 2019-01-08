from django.core import mail
from django.core.mail import EmailMessage

# Handle very simple email generation
class Email(object):

    @classmethod
    def sendKeys(cls, owners ) :
        connection = mail.get_connection()   # Use default email connection
        messages = []
        for user,key_list in owners.items():
            messages.append(EmailMessage(
                'Files were shared with you!',
                cls.generateBody(user,key_list),
                'noreply@nasapp.be',
                [user.email],
                [],#bbc
            ))
        connection.send_messages(messages)
        connection.close()

    @classmethod
    def generateBody(cls,user, key_list):
        message="________NAS Application_______\n\n"
        message+="Hello %s,\n File(s) have been shared with you and can be found in the sharedfile part of the application.\n" % (user.username)
        message+="To access or delete the file a set amount of users has to use a secret key. If enough users provide their keys then read access or delete access will be granted.\n "
        message+="Here is the list of yours secret keys by file:\n"
        for filename, key in  cls.grouped(key_list,2):
            message+="%s : %s\n" % (filename,key)
        message+="\n Warning: if you loose the key you might not be able to ever recover the file, be sure to keep it safely stored!"
        return message

    @classmethod
    def grouped(cls,iterable, n):
        "s -> (s0,s1,s2,...sn-1), (sn,sn+1,sn+2,...s2n-1), (s2n,s2n+1,s2n+2,...s3n-1), ..."
        return zip(*[iter(iterable)]*n)

