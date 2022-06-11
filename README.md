Note:
* In settings.py, change the value of 'STATICFILE_DIRS' to the path on your computer.
* Run `python manage.py migrate` before `python manage.py runserver`.
* How to deploy static files: https://docs.djangoproject.com/en/4.0/howto/static-files/deployment/
* Login required decorator
* BASE_DIR in settings.py for STATICFILES
* select username, sessions_completed, last_visit, visit_time_1, visit_time_2, visit_time_3, visit_time_4, visit_time_5, visit_time_6 from auth_user inner join user_participant on auth_user.id = user_participant.user_id;
* Find a way to set session number in Psytoolkit (1 through 6) such that the output data reflects that.
* Do something about naive datetime.datetime.now()
* 