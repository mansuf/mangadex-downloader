# Workaround to install rust for building Dockerfile.optional in ARM v6 machine CI
echo $(lscpu)
export ARCHITECTURE=$(lscpu | grep Architecture | sed -e 's/Architecture:\s//g')
echo $ARCHITECTURE
if [ $ARCHITECTURE = "armv7l" ]; then 
    apt install libc6-armhf-cross
    export LD_LIBRARY_PATH=/usr/arm-linux-gnueabihf/lib
    ln -s /usr/arm-linux-gnueabihf/lib/ld-linux-armhf.so.3 /lib/ld-linux-armhf.so.3
    # ln -s /usr/arm-linux-gnueabihf/lib/ld-linux-armhf.so.3 /usr/lib/ld-linux-armhf.so.3
    # export QEMU_LD_PREFIX=/usr/arm-linux-gnueabi
else 
    raise_error_lol_command_not_found; 
fi