#!/bin/bash

# Check if an argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <param_path> <batch_size>"
    echo "<param_path> is the path of the parameter file. Can be absolute or relative to the path of this script"
    echo "<batch_size> indicates how many HITs you want to create. 
    Iteration of the batch_size will be used as a seed value when drawing images."
    exit 1
fi

# Get command line argument
param_path=$1
batch_size=$2

# Check if the input is a valid number
if ! [[ "$batch_size" =~ ^[0-9]+$ ]]; then
    echo "Invalid input. Please enter a valid number."
    exit 1
fi

# Execution
echo "Publishing HITs ... "
cd /home/$(whoami)/tot-data
for ((i=1; i<=$batch_size; i++)); do
    python e2e_create.py $param_path $i
done
