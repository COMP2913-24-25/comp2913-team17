#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Additional dependencies for PostgreSQL
pip install psycopg2-binary gunicorn 