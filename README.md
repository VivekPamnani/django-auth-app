Note:
* In settings.py, change the value of 'STATICFILE_DIRS' to the path on your computer.
* Run `python manage.py migrate` before `python manage.py runserver`.
* How to deploy static files: https://docs.djangoproject.com/en/4.0/howto/static-files/deployment/
* Login required decorator
* BASE_DIR in settings.py for STATICFILES
* select auth_user.id, username, email, sessions_completed, last_visit, last_email, visit_time_1, visit_time_2, visit_time_3, visit_time_4, visit_time_5, visit_time_6, is_verified, ref from auth_user inner join user_participant on auth_user.id = user_participant.user_id;
* Find a way to set session number in Psytoolkit (1 through 6) such that the output data reflects that.
* Do something about naive datetime.datetime.now()


### To get started (development):
1. Pull the repo
2. `python3 -m venv .venv`
3. `source .venv/bin/activate`
4. `python3 -m pip install -r requirements.txt`
5. `python3 manage.py makemigrations user`
6. `python3 manage.py migrate`
7. `python3 manage.py runserver`
8. Initialize SiteConfiguration

### Initializing SiteConfiguration
1. `python3 maange.py shell`
2. While in shell:
```python
from django.contrib import admin
from solo.admin import SingletonModelAdmin
from config.models import SiteConfiguration
SiteConfiguration.get_solo()
```
3. Exit

*Note that you need Python3.10 for it to work.*

## Crontab
For crontab, make sure the `cron` and `atd` services are running.
1. sudo service cron start
2. sudo service atd start

## Config Instructions
The default mode for study design is 'opt-in'. That is, participants are required to opt-in to the longitudinal study. If you want to change this so it is 'opt-in' by default, set `USER_LONGITUDINAL_OPT_IN` to `False` in `mysite/settings.py`

If you want to set up custom redirects for success/fail events, set the following variables in `mysite/settings.py`:
1. `USER_SCREEN_FAIL_REDIRECT`
1. `USER_QUOTA_FULL_REDIRECT` 
1. `USER_SESSION_COMPLETE_REDIRECT` 

### To do:
1. Ensure the old data is preserved by:
   1. Checking django-migrations table.
   2. Running makemigrations.
2. Mark all old users as inactive.
3. Use send_mass_mail.py and send email to all old users.
