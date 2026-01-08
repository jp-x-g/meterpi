#!/bin/bash
echo "" > data/output.txt
for f in data/*.jpg data/*.JPG data/*.jpeg data/*.JPEG; do
	echo "$f"
	# magick "$f" -crop 200x75+177+200 +repage "$f"-c.jpg
	#python3 ocr.py "$f"-c.jpg
	#python3 ocr.py "$f"
	python3 locate.py "$f" "$f"roi.jpg
	python3 ocr.py "$f"roi.jpg data/output.txt
done

python3 makepage.py data/output.txt data/view.html