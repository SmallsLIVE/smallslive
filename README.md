# SmallsLIVE instructions

[ ![Codeship Status for SmallsLIVE/smallslive](https://www.codeship.io/projects/fa4ca030-7922-0130-982f-123138094421/status?branch=master)](https://www.codeship.io/projects/2192)
[![Coverage Status](https://coveralls.io/repos/github/SmallsLIVE/smallslive/badge.svg?branch=HEAD)](https://coveralls.io/github/SmallsLIVE/smallslive?branch=HEAD)

1. Install pip: `easy_install pip`
2. Install virtualenv: `pip install virtualenv`
3. Create a new virtualenv: `virtualenv /home/<user_name>/.virtualenvs/smallslive`
4. Activate virtualenv: `source /home/<user_name>/.virtualenvs/smallslive/bin/activate`
5. Clone the repo: `git clone git@github.com:SmallsLIVE/smallslive.git /home/<user_name>/projects/smallslive`
6. Go to the project folder: `cd /home/<user_name>/projects/smallslive`
7. Install the project requirements: `pip install -r requirements.txt`
8. Edit the `smallslive/smallslive/settings.py` with the correct DB settings for local development.
9. Run the django server: `python smallslive/manage.py runserver` and access it at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

# Troubleshooting

If you get a notice from Heroku that says:

```
Your database postgresql-pointy-2352 standard-0 (GOLD on smallslive-metrics) must undergo maintenance.
```

Take heed! This means that within some time period the DB is going to be automatically updated and it will get a new IP address. You can adjust the maintenance period by running `heroku pg:maintenance:window GOLD "Tuesday 14:30"`

Once the migration is done, you'll get another email like this:

```
Maintenance on your database postgresql-pointy-2352 standard-0 (GOLD on smallslive-metrics) has been completed and your database is now back online.
```

Now you need to go into the `METRICS_DB_URL` in the smallslive app config vars, and change it to the new one:
First, go here and find the `DATABASE_URL` string (you have to click on the "Reveal config vars" button:
https://dashboard.heroku.com/apps/smallslive-metrics/settings

Copy the `DATABASE_URL` string.

Then, go here and find the `METRICS_DB_URL` config var (again, you have to click the "Reveal config vars" button):
https://dashboard.heroku.com/apps/smallslive/settings

Paste the previously copied `DATABASE_URL` string into the `METRICS_DB_URL` field and save the form.

Now the SmallsLIVE app should be pointing to the updated DB, and the site should be operating as normal.
