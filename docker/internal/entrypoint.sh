#!/bin/bash
ip route change default via 192.168.1.4

exec "$@"