cd clidocker
mkdir -p content

cp ../../requirements.txt content
cp -r ../../gateway content
cp -r ../../gatecli content

docker build -t polympiads/gateway-cli-tests-docker .
docker-compose up --exit-code-from container