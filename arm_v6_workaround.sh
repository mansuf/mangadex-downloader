# Workaround to install rust for building Dockerfile.optional in ARM v6 machine CI
export ARCHITECTURE=$(lscpu | grep Architecture | sed -e 's/Architecture:\s//g')
echo $ARCHITECTURE
if [ $ARCHITECTURE = "armv7l" ]; then 
    export QEMU_LD_PREFIX=/usr/arm-linux-gnueabi
else 
    raise_error_lol_command_not_found; 
fi