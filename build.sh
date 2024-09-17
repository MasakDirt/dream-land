#!/usr/bin/env bash

set -o orrexit

pip install -r requirements.txt

python manage.py collectstatis --no-input
python manage.py migrate
