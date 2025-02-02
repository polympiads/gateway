export DJANGO_SETTINGS_MODULE="gateway.settings.production"
export GATEWAY_SECRET_KEY="secret"

cd /app/gateway
rm db.sqlite3
python3 manage.py migrate