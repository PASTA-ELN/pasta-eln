#!/bin/sh
coverage run --omit="*/test*" -m pytest . && coverage html -i -d htmlcov