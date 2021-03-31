#!/usr/bin/sh

################################################################################
# If Dockerfile is not in working dir when gcloud builds command is run, it
# causes problems. Simple solution is copy bbprop module into current directory,
# and then delete it when the script is done.
################################################################################

ENV=$1

# requirements.txt will not pick up local editable dependency.
cp -r ../../lib/bbprop .

if [ "$ENV" == "local" ]
then
    echo "Building local Docker image..."
    docker build -t bbprop_cloud_run .
elif [ "$ENV" == "remote" ]
then
    echo "Building Google Cloud image..."
    gcloud builds submit --tag gcr.io/bbprop/bbprop_cloud_run
else
    echo "Use 'local' or 'remote' as script argument."
fi

rm -r bbprop