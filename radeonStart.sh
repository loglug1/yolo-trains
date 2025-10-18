#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script's directory
cd "$SCRIPT_DIR"

#Activate conda environment
eval "$(conda shell.bash hook)"
conda activate trains

#Start server
IPADDR="$(ip addr show tailscale0 | grep "inet" | head -n 1 | awk '/inet/ {print $2}' | cut -d'/' -f1)"
HSA_OVERRIDE_GFX_VERSION=10.3.0 PYTORCH_ROCM_ARCH="gfx1036" HIP_VISIBLE_DEVICES=0 ROCM_PATH=/opt/rocm ROD_HOSTNAME=localhost ROD_PORT=5000 ROD_UPLOADS=uploads REDIS_HOST=localhost REDIS_PORT=6379 python -X faulthandler app.py --address $IPADDR
