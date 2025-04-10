#!/usr/bin/env bash
# exit on error
set -o errexit

# Install pre-built packages
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
