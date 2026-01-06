fn="$(date +'%F%H:%M:%S').jpg"

sudo fswebcam -d /dev/video0 -S 20 --flip h "$fn"
