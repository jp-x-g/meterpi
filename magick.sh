#!/bin/bash
cd data
for f in ./*.jpg ./*.JPG ./*.jpeg ./*.JPEG; do
	echo "$f"
	magick "$f" -crop 200x75+177+200 +repage "$f"-c.jpg
	#python3 ocr.py "$f"-c.jpg
done