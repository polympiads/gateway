#!/bin/bash

cd /app/gatecli
python3 -m coverage run --source=. -m pytest
python3 -m coverage report --fail-under=100
