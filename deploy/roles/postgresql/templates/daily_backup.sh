#!/usr/bin/env bash
NOW="$(date +"%Y-%m-%d")"
FILENAME="{{backups_dir}}/{{app_name}}.$NOW.tar"
su postgres -c "pg_dump -F tar -f $FILENAME {{app_name}}"
gzip $FILENAME
s3cmd -c /etc/s3cfg put $FILENAME.gz s3://{{s3_backup_bucket}}
