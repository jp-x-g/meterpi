#!/usr/bin/env python3
import cv2
import numpy as np
import sys

def cvify(frame, templ):

	fg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	tg = cv2.cvtColor(templ, cv2.COLOR_BGR2GRAY)

	# Optional: match on edges to be less sensitive to lighting
	fg = cv2.Canny(fg, 60, 160)
	tg = cv2.Canny(tg, 60, 160)

	res = cv2.matchTemplate(fg, tg, cv2.TM_CCOEFF_NORMED)
	minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)

	print("match score:", maxVal, "at:", maxLoc)
	if maxVal < 0.45:
	    #raise SystemExit("Template match too weak; adjust template or thresholds")
	    print("Template match too weak; adjust template or thresholds")

	return cv2.minMaxLoc(res)


def get(img_path, out_path, tmp_path, btm_path, debug=True):
	duds = ["data/*.JPG", "data/*.jpg", "data/*.JPEG", "data/*.jpeg"]
	if img_path in duds:
		print(f"This isn't legit bro: {img_path}")
		sys.exit()

	frame = cv2.imread(img_path)
	templ = cv2.imread(tmp_path)
	bottm = cv2.imread(btm_path)

	minVal, maxVal, minLoc, maxLoc = cvify(frame, templ)

	th, tw = templ.shape[:2]          # template height/width
	fh, fw = frame.shape[:2]          # frame height/width
	x0, y0 = maxLoc                   # template top-left from matchTemplate

	x1 = max(0, x0)
	x2 = min(fw, x0 + tw)
	y1 = max(0,  y0 + th)
	y2 = fh

	if x2 <= x1 or y2 <= y1:
	    raise SystemExit("ROI ended up empty (bad match or out of bounds).")

	roi = frame[y1:y2, x1:x2]

	# cv2.imwrite(f"{out_path}half.jpg", roi)
	# Uncomment to debug halfway ones


	## Now we remove the bottom part.

	minVal, maxVal, minLoc, maxLoc = cvify(roi, bottm)
	bx, by = maxLoc  # bottom-template top-left within roi
	th, tw = bottm.shape[:2]

	# keep everything ABOVE where the bottom template begins
	roi2 = roi[:by, :]

	dbg = frame.copy()
	cv2.rectangle(dbg, (x0, y0), (x0 + templ.shape[1], y0 + templ.shape[0]), (0,255,0), 2)

	cv2.rectangle(dbg, (x1, y1), (x2, y2), (0,0,255), 2)
	# For bottom.
	cv2.rectangle(dbg, (x1+bx, y1+by),  (x1+bx+tw, y1+by+th), (255, 0, 255), 2)
	cv2.imwrite("data/debug_boxes_00.jpg", dbg)

	cv2.imwrite(out_path, roi2)
if __name__ == "__main__":
	img_path = sys.argv[1]
	if len(sys.argv) > 2:
		out_path = sys.argv[2]
	else:
		out_path = "data/output.jpg"
	if len(sys.argv) > 3:
		tmp_path = sys.argv[3]
	else:
		tmp_path = "cfg/template.jpg"
	if len(sys.argv) > 4:
		btm_path = sys.argv[4]
	else:
		btm_path = "cfg/template-bottom.jpg"

	print(f"Trimming to ROI: {img_path}, {out_path}, {tmp_path}, {btm_path}")

	get(img_path, out_path, tmp_path, btm_path)