#!/bin/bash

python /app/azcopy/file_mounter.py
FILE=/mnt/output
if [ -d "$FILE" ]; then
    echo "Output already exists. No need to re create it or any cron jobs"
else
	python /app/azcopy/file_mounter.py
	service cron start
	crontab -l > dailyforecastcron
	echo "0 12 * * * /bin/bash /app/azcopy/forecast-workflow.sh" >> dailyforecastcron
	crontab dailyforecastcron
fi

/usr/bin/supervisord
