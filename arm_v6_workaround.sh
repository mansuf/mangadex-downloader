# Workaround to install rust for building Dockerfile.optional in ARM v6 machine CI
echo $(lscpu)
export ARCHITECTURE=$(lscpu | grep Architecture | sed -e 's/Architecture:\s//g')
export CPU_FLAGS=$(lscpu | grep Flags | sed -e 's/Flags:\s//g')
echo $ARCHITECTURE
echo $CPU_FLAGS

echo $ARCHITECTURE
if [ $ARCHITECTURE = "armv7l" ] && ! [[ $CPU_FLAGS =~ "v_vmsave_vmlo" ]]; then 
    apt install libc6-armhf-cross
    export LD_LIBRARY_PATH=/usr/arm-linux-gnueabihf/lib
    ln -s /usr/arm-linux-gnueabihf/lib/ld-linux-armhf.so.3 /lib/ld-linux-armhf.so.3
else 
    raise_error_lol_command_not_found; 
fi