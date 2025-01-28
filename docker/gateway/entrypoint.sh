#!/bin/bash
echo 1 > /proc/sys/net/ipv4/ip_forward

iptables -P FORWARD DROP
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -s 192.168.1.5 -d 192.168.0.5 -j ACCEPT
iptables -A FORWARD -s 192.168.1.6 -d 192.168.0.6 -j ACCEPT

exec "$@"