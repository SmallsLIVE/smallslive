# SmallsLIVE instructions

https://www.codeship.io/projects/fa4ca030-7922-0130-982f-123138094421/status

1. Install pip: `easy_install pip`
2. Install virtualenv: `pip install virtualenv`
3. Create a new virtualenv: `virtualenv /home/<user_name>/.virtualenvs/smallslive`
4. Activate virtualenv: `source /home/<user_name>/.virtualenvs/smallslive/bin/activate`
5. Clone the repo: `git clone git@github.com:SmallsLIVE/smallslive.git /home/<user_name>/projects/smallslive`
6. Go to the project folder: `cd /home/<user_name>/projects/smallslive`
7. Install the project requirements: `pip install -r requirements.txt`
8. Edit the `smallslive/smallslive/settings.py` with the correct DB settings for local development
9. Run the django server: `python smallslive/manage.py runserver` and access it at [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
