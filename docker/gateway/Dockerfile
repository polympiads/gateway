FROM ubuntu:latest

RUN apt update
RUN apt install -y curl
RUN apt install -y iptables
RUN apt install -y sudo

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]
