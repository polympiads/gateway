#!/bin/bash

cd /app/gatecli
python3 -m coverage run --source=gatecli -m pytest
python3 -m coverage report --fail-under=100
