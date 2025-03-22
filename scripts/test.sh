export DJANGO_SETTINGS_MODULE="gateway.settings.test"
python3 -m coverage run --source=. gateway/manage.py test gateway --parallel 1 -v 2
python3 -m coverage report --fail-under=100