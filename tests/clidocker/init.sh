export DJANGO_SETTINGS_MODULE="gateway.settings.init"
export GATEWAY_SECRET_KEY="secret"

cd /app/gateway
python3 manage.py $@