FROM ubuntu:latest

RUN apt update
RUN apt install -y curl
RUN apt install -y iputils-ping
RUN apt install -y iproute2
RUN apt install -y traceroute

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
