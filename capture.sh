fn="$(date +'%F%H:%M:%S').jpg"

mkdir data

sudo fswebcam -d /dev/video0 -S 20 --flip h data/"$fn"
IFS=: read -r u p < auth.txt 
curl -T "$fn" -u "$(cat auth.txt)" "ftp://phoeni.city/"

