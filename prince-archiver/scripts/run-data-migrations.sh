
#! /usr/bin/env sh
set -e

python /app/prince_archiver/data_migrations/populate_missing_data_archive_entries.py
python /app/prince_archiver/data_migrations/populate_imaging_event_aggregate.py
python /app/prince_archiver/data_migrations/populate_data_archive_aggregate.py

