#!/bin/bash

# Check if an argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <stage>"
    echo "stage is either sandbox or live."
    exit 1
fi

# Get the stage from the command line argument
stage=$1

# Execute retrieval
cd /home/$(whoami)/tot-data
python e2e_retrieve.py $stage
