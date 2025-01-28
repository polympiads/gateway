docker build -t polympiads/gateway gateway/
docker build -t polympiads/internet internet/
docker build -t polympiads/internal internal/

docker-compose up -d