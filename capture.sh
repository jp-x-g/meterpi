fn="$(date +'%F%H:%M:%S').jpg"

mkdir data

sudo fswebcam -d /dev/video0 -S 20 --flip h data/"$fn"

# When there's a script to actually CV them, that would be nice to have.





IFS=: read -r u p < auth.txt 
curl -T data/"$fn" -u "$(cat auth.txt)" "ftp://$(cat site.txt)"