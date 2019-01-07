from django.core import mail

# Handle very simple email generation
class Email(object):

    @classmethod
    def sendKeys(cls, shares, owners ) :
        #connection = mail.get_connection()   # Use default email connection
        #messages=[]
        #for share in shares:
        #    filename = share[-1]
        #    for i in range(0,-1):
        #connection.send_messages(messages)
        #connection.close()
        print(shares)
        print(owners)