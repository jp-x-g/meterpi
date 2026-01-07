#!/usr/bin/env python3
import cv2
import pytesseract
import sys

img_path = sys.argv[1]

debug = True

def debugStage(stage, img):
	cv2.imwrite(f"temp{stage}.jpg", img)
	config = "--oem 1 --psm 7 -c tessedit_char_whitelist=0123456789"
	text = pytesseract.image_to_string(bw, config=config)
	print(f"[{text}]")




img = cv2.imread(img_path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
debug && debugStage(gray, "1")
# upscale (OCR likes bigger glyphs)
gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
debug && debugStage(gray, "2")
# contrast boost
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
gray = clahe.apply(gray)
debug && debugStage(gray, "3")
# denoise a bit
gray = cv2.GaussianBlur(gray, (3,3), 0)
debug && debugStage(gray, "4")
# binarize
_, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
debug && debugStage(bw, "5")
# If digits come out white-on-black vs black-on-white, invert if needed
# (Tesseract usually prefers black text on white background)
# Try commenting/uncommenting this depending on your results:

# thicken segments slightly
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel, iterations=1)
debug && debugStage(bw, "6")
bw = 255 - bw
debug && debugStage(bw, "7")
config = "--oem 1 --psm 7 -c tessedit_char_whitelist=0123456789"
text = pytesseract.image_to_string(bw, config=config)
print(text.strip())