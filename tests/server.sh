cd gateway
export GATEWAY_SECRET_KEY="secret"
export DJANGO_SETTINGS_MODULE="gateway.settings.init"
python3 -m coverage run --source=. manage.py test --parallel 1
python3 -m coverage report --fail-under=100