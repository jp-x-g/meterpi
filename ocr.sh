#!/bin/bash
for f in data/*.jpg data/*.JPG data/*.jpeg data/*.JPEG; do
	echo "$f"
	# magick "$f" -crop 200x75+177+200 +repage "$f"-c.jpg
	#python3 ocr.py "$f"-c.jpg
	#python3 ocr.py "$f"
	python3 locate.py "$f" "$f"roi.jpg
done