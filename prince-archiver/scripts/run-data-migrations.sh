#! /usr/bin/env bash

set -e
set -x


python prince_archiver/data_migrations/populate_missing_data_archive_entries.py
python prince_archiver/data_migrations/populate_imaging_event_aggregate.py
python prince_archiver/data_migrations/populate_data_archive_aggregate.py
