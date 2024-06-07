#!/bin/bash

# Workaround to install rust for building Dockerfile.optional in ARM v6 machine CI
echo $(lscpu)
export ARCHITECTURE=$(lscpu | grep Architecture | sed -e 's/Architecture:\s//g')
export CPU_FLAGS=$(lscpu | grep Flags | sed -e 's/Flags:\s//g')
echo $ARCHITECTURE
echo $CPU_FLAGS

# https://stackoverflow.com/a/52832543
# Thank you stackoverflow
apt-get update
apt-get install libc6-armhf-cross
ln -s /usr/arm-linux-gnueabihf/lib/ld-linux-armhf.so.3 /lib/ld-linux-armhf.so.3

# https://askubuntu.com/a/574174
# apt-get install gcc-multilib

# https://github.com/zabbix/zabbix-docker/issues/1086
apt-get install libgcc-12-dev


# export LD_LIBRARY_PATH=/usr/arm-linux-gnueabihf/lib
# export QEMU_LD_PREFIX=/usr/arm-linux-gnueabi
# if [ $ARCHITECTURE = "armv7l" ] && ! [[ $CPU_FLAGS =~ "v_vmsave_vmlo" ]]; then 
#     apt install libc6-armhf-cross
#     export LD_LIBRARY_PATH=/usr/arm-linux-gnueabihf/lib
#     ln -s /usr/arm-linux-gnueabihf/lib/ld-linux-armhf.so.3 /lib/ld-linux-armhf.so.3
# fi