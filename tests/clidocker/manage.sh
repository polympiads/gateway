export DJANGO_SETTINGS_MODULE="gateway.settings.production"
export GATEWAY_SECRET_KEY="secret"

cd /app/gateway
python3 manage.py $@