#!/bin/sh

sqlite3 sqlite3.db < a.db.sql && \
    ( \
        ./tcpdump.py &\
        # (crontab -l; echo "* * * * * `pwd`/measure.py") | crontab -\
        ./measure.py &\
    )