#!/usr/bin/env python3
import cv2
import sys


def pytesseract(img):
	import pytesseract

	def read1(img, cfg):
		text = pytesseract.image_to_string(img, config=cfg)
		output = f"[{text}]"
		if debug: output += f" {cfg}"
		return output

	def debugStage(stage, img):
		cv2.imwrite(f"temp{stage}.jpg", img)
		text = read1(img, "--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789")
		print(f"stage {stage}: {text}")

	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	if debug: debugStage("1", gray)
	# upscale (OCR likes bigger glyphs)
	gray = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
	if debug: debugStage("2", gray)
	# contrast boost
	clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
	gray = clahe.apply(gray)
	if debug: debugStage("3", gray)
	# denoise a bit
	gray = cv2.GaussianBlur(gray, (3,3), 0)
	if debug: debugStage("4", gray)
	# binarize
	_, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
	if debug: debugStage("5", bw)
	# If digits come out white-on-black vs black-on-white, invert if needed
	# (Tesseract usually prefers black text on white background)
	# Try commenting/uncommenting this depending on your results:

	# thicken segments slightly
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
	bw = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel, iterations=1)
	if debug: debugStage("6", bw)
	bw = 255 - bw
	if debug: debugStage("7", bw)
	config = "--oem 1 --psm 7 -c tessedit_char_whitelist=0123456789"
	text = pytesseract.image_to_string(bw, config=config)
	print(text.strip())

def paddle(img):
	from paddleocr import PaddleOCR

	ocr = PaddleOCR(use_angle_cls=False, lang="en")  # CPU ok

	res = ocr.ocr(img, cls=False)

	# res is a list of [box, (text, conf)]
	texts = []
	for line in res[0] if res and res[0] else []:
	    text, conf = line[1]
	    texts.append((conf, text))

	texts.sort(reverse=True)
	print(texts[:10])

def easyocr(img):
	import easyocr

def ocr(img_path):
	debug = True
	duds = ["data/*.JPG", "data/*.jpg", "data/*.JPEG", "data/*.jpeg"]
	if img_path in duds:
		print(f"This isn't legit bro: {img_path}")
		sys.exit()

	img = cv2.imread(img_path)
	#pytesseract(img)
	# Worked but didn't actually identify the stuff so good.
	
	#paddle(img)
	# Dependency hell

	easyocr(img)

if __name__ == "__main__":
	print("Running ocr.py from terminal")
	img_path = sys.argv[1]
	ocr(img_path)