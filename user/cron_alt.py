from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from django.contrib.auth.models import User
from unicodedata import name


# send our email message 'msg' to our boss
def message(subject="Python Notification", text="abcd"):
	
	# build message contents
    msg = MIMEMultipart()
	# Add Subject
    msg['Subject'] = subject
    # msg['To'] = 'vivpamnani19990429@gmail.com'
    # msg['From'] = 'vivek.pamnani.iiit.research@outlook.com'
	# Add text contents
    msg.attach(MIMEText(text))

	# Check if we have anything
	# given in the img parameter
	
	# We do the same for
	# attachments as we did for images
			
    return msg

def auto_email():
    # try:
    smtp = smtplib.SMTP(host='smtp-mail.outlook.com', port=587)
    smtp.ehlo()
    smtp.starttls()

    # Login with your email and password
    smtp.login(user="", password="")

    # Call the message function
    msg = message("Good!", "Hi there!")

    # Make a list of emails, where you wanna send mail
    # to = ["vivpamnani19990429@gmail.com", "vivek.pamnani.iiit.research@outlook.com"]
    # to = ['gameidvivek@gmail.com', 'vivpamnani19990429@gmail.com', 'vivekpamnani04@gmail.com', 'vivek.pamnani@research.iiit.ac.in']
    to = [i.email for i in User.objects.all()]


    # Provide some data to the sendmail function!
    smtp.sendmail("vivek.pamnani.iiit.research@outlook.com", to, msg.as_string())
    # smtp.send_message(msg)
    # Finally, don't forget to close the connection
    smtp.quit()
    # except: 
        # print("Connection Error")
    # Opening a file
    try:
        file1 = open('myfile.txt', 'x')
    except:
        file1 = open('myfile.txt', 'a')
    L = ["This is Delhi \n", "This is Paris \n", "This is London \n"]
    s = "Hello\n"
    file1.write(s)
    file1.close()
    print("Hello There")


if __name__ == "__main__":
     auto_email()