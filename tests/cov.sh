#!/bin/sh
coverage run --branch --include="*flock/*" --omit="*tests*,*migrations*" ./manage.py test testapp
coverage html
