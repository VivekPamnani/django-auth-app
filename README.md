Note:
* In settings.py, change the value of 'STATICFILE_DIRS' to the path on your computer.
* Run `python manage.py migrate` before `python manage.py runserver`.
* How to deploy static files: https://docs.djangoproject.com/en/4.0/howto/static-files/deployment/
* Login required decorator
* BASE_DIR in settings.py for STATICFILES
* select id, username, sessions_completed, last_visit, last_email, visit_time_1, visit_time_2, visit_time_3, visit_time_4, visit_time_5, visit_time_6, is_verified from auth_user inner join user_participant on auth_user.id = user_participant.user_id;
* Find a way to set session number in Psytoolkit (1 through 6) such that the output data reflects that.
* Do something about naive datetime.datetime.now()


### To get started (development):
1. Pull the repo
2. `python3 -m venv .venv`
3. `source .venv/bin/activate`
4. `python3 -m pip install -r requirements.txt`
5. `python3 manage.py runserver`

*Note that you need Python3.10 for it to work.*


### To do:
1. instructions
2. email verification
3. testing
4. hosting