# launch our autostart apps (if we are on the correct tty)
if [ "`tty`" = "/dev/tty1" ]; then
    # Turn off LED
    /home/pi/turn_off.sh

    # Home Automation
    python /home/pi/echo_fauxmo/MY_fauxmo.py &

    # KODI Control
    foreman start --root=/home/pi/echo_fauxmo &

    # Launch KODI and Retro Pie
    while :
    do
        kodi-standalone #auto
        emulationstation #auto
    done
fi
