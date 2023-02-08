# To use this script, you must first activate the virtual environment.
# Then, run the script like any Python script.
# Input the list of codes that you would like to mark as paid.
# Once you're done, enter 'x' or 'X' to tell that you're done inputting codes. 


import os
import django
import environ

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 
'mysite.settings')
django.setup()


from django.core.mail import send_mail
import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from user.models import codes
from django import db
db.connections.close_all()
db.close_old_connections()

env = environ.Env()

def mark_paid(paid_codes):
    allcodes = codes.objects.all()
    for code in paid_codes:
        try:
            c = codes.objects.get(otp=code)
        except ObjectDoesNotExist:
            print("Error: " + code + "; Code not found.")
        except: 
            print("Error: " + code + "; Something else went wrong.")
        else:
            c.is_paid = 1
            c.save()


    #     print(c)
    # for code in allcodes:
        # print(type(code.otp))

if __name__ == "__main__":
    # print(codes.objects.get())
    # mark_paid(
    #     [
    #         '75bjUuokzJZo', 
    #         '5JzAAoFVsYBY', 
    #         '3sce3ohafZYs', 
    #         '4CyoxwMEtkSH', 
    #         '5FRcSZyn3Wdr', 
    #         '6scsgn4zEXFr', 
    #         '6zgjyandisJ4', 
    #         '666Ppzg3f3Zu', 
    #         '4nwVGdYnBrBa', 
    #         '7Eo8VQu5jEuz', 
    #         '5hk7KM3yJBpz', 
    #         '87dH9NL9JwiC', 
    #         '5VUS5wGAVQme', 
    #         '4FD2mWUkZ8x6', 
    #         '7QcK7SrmrPVG', 
    #         '4qwHU8vxL8D6', 
    #         'HcdEohAtd6a3', 
    #         '6ZDC6gpZPZc7', 
    #         '4ujPWRmqhcLR', 
    #         '5CuAKXj8SdN6', 
    #         '3vYVeZ5ogBWe', 
    #         'kW4r97YguycV', 
    #         '5rPNbN2gCBoL', 
    #         '7raZtiGcBVqq', 
    #         '6YXCcfvdtYDv'
    #     ]
    # )
    tobePaid = []
    while True:
        inp = input()
        if(inp == 'x' or inp == 'X'):
            break
        if(len(inp)!=12):
            continue
        tobePaid.append(inp)
    mark_paid(tobePaid)