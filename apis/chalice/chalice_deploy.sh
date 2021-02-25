#!/usr/bin/sh

# Overwrite storage.py with latest version.
cp -r ../../lib/bbprop/storage.py chalicelib/storage.py

echo "Deploying Chalice app..."
chalice deploy --connection-timeout 360