FROM ubuntu:latest

RUN apt update && apt install -y curl
RUN apt update && apt install -y iputils-ping
RUN apt update && apt install -y iproute2
RUN apt update && apt install -y traceroute
RUN apt update && apt install -y python3
RUN apt update && apt install -y python3-pip
RUN apt update && apt install -y python3-venv

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app
COPY content/requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY content/gatecli /app/gatecli
COPY content/gateway /app/gateway
COPY entrypoint.sh /app/entrypoint.sh
COPY resetdb.sh /app/resetdb.sh
COPY manage.sh /app/manage.sh
COPY init.sh /app/init.sh
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/resetdb.sh
RUN chmod +x /app/manage.sh
RUN chmod +x /app/init.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]
CMD ["sh", "-c", "while true; do sleep 30; done"]
