#!/bin/sh
coverage run -m pytest tests/app-tests/ && coverage html -i