#!/bin/bash
#
#SBATCH --partion=staging
#
# Archive all images for a given day. 
# Step 1: Download all images for a given day
# Step 2: Insert them into a per experiment archive

# TODO: set correct directory based on user
ARCHIVE_DIR=/archive

while getopts "d:p:" opt; do
   case "$opt" in
       d) DATE_STR=${OPTARG};;
       p) ARCHIVE_DIR=${OPTARG};;
   esac
done

DOWNLOAD_DIR=$(mktemp -d)
TARGET_FILE=$DATE_STR.tar

rclone copy s3:mycostreams "$DOWNLOAD_DIR" --include "*/$DATE_STR*.tar.gz"

if [ "$(ls -A $DOWNLOAD_DIR)" ]; then
    for EXPERIMENT_DIR in ${DOWNLOAD_DIR}/*/; 
    do
        EXPERIMENT_ID=$(basename $EXPERIMENT_DIR)
        TARGET_DIR=$ARCHIVE_DIR/$EXPERIMENT_ID

        mkdir -p "$TARGET_DIR"   
        tar -cf "$TARGET_DIR/$TARGET_FILE" -C "$DOWNLOAD_DIR" "$EXPERIMENT_ID"
    done    
    exit 0
else
    echo "No files downloaded"
    exit 1
fi

trap "rm -rf $DOWNLOAD_DIR" EXIT
