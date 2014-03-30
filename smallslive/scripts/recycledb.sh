set -e
set -x

export PATH=$PATH:/Applications/Postgres93.app/Contents/MacOS/bin/
dropdb smallslive
createdb smallslive
cd ..
./manage.py syncdb
./manage.py migrate
./manage.py migrate_old_data
./manage.py migrate_user_data smallsliveusers.txt
./manage.py createsuperuser
