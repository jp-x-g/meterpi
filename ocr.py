#!/usr/bin/env python3
import cv2
import sys
import re

def loadSlopKey(path="cfg/oai-auth.txt"):
	return pathlib.Path(path).read_text().strip()

def debugStage(stage, img):
	cv2.imwrite(f"temp/{stage}.jpg", img)
	# text = read1(img, "--oem 3 --psm 11 -c tessedit_char_whitelist=0123456789")
	# print(f"stage {stage}: {text}")

def preprocess(img, debug):
	try:
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	except:
		print("Couldn't convert BGR2GRAY")
		gray = img.copy()
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
	return bw


def pytesseract(img, output):
	import pytesseract

	def read1(img, cfg):
		text = pytesseract.image_to_string(img, config=cfg)
		output = f"[{text}]"
		if debug: output += f" {cfg}"
		return output
	config = "--oem 1 --psm 7 -c tessedit_char_whitelist=0123456789"
	bw = preprocess(img)
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


	reader = easyocr.Reader(["en"], gpu=False)

	res = reader.readtext(img, detail=1, paragraph=False)  # NO allowlist yet

	for i,(bbox, text, conf) in enumerate(res):
	    xs = [p[0] for p in bbox]; ys = [p[1] for p in bbox]
	    w = max(xs)-min(xs); h = max(ys)-min(ys)
	    print(i, f"conf={conf:.3f}", f"w={w:.1f}", f"h={h:.1f}", repr(text))



    ##########
	try:
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	except:
		print("Couldn't convert BGR2GRAY")
		gray = img.copy()
	gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
	gray = cv2.GaussianBlur(gray, (3, 3), 0)

	# Try both polarities; segment LCDs vary with lighting
	inv = 255 - gray

	# Debug dumps so you can see what OCR saw
	cv2.imwrite("temp/temp_easy_gray.jpg", gray)
	cv2.imwrite("temp/temp_easy_inv.jpg", inv)

	reader = easyocr.Reader(["en"], gpu=False)

	def run(im):
	    # detail=1 gives (bbox, text, conf)
	    return reader.readtext(im,
	    	detail=1,
	    	paragraph=False,
	        text_threshold=0.2,
	        low_text=0.15,
	        link_threshold=0.2
	        )

	res1 = run(gray)
	res2 = run(inv)

	def best(res):
	    if not res:
	        return None
	    # each item: (bbox, text, conf)
	    return max(res, key=lambda x: x[2])

	b1 = best(res1)
	b2 = best(res2)

	best_hit = None
	if b1 and b2:
	    best_hit = b1 if b1[2] >= b2[2] else b2
	else:
	    best_hit = b1 or b2

	if not best_hit:
	    print("NO_TEXT")
	    sys.exit(0)

	bbox, text, conf = best_hit
	print(f"RAW: {text!r}  conf={conf:.3f}")

	# If you only care about numbers like 000.064 etc:
	clean = re.sub(r"[^0-9.]", "", text)
	print(f"CLEAN: {clean!r}")

	return f"{text!r}"

def slopenai(
    img
    model="gpt-5",
    auth_path="cfg/oai-auth.txt",
):

	from openai import OpenAI
    client = OpenAI(api_key=load_key(auth_path))

    img_bytes = pathlib.Path(image_path).read_bytes()
    img_b64 = base64.b64encode(img_bytes).decode("ascii")

    prompt = (
        "Read the eight digits from the numeric LCD value in this image. Return ONLY the number (digits and decimal point). No words, no explanation."
    )

    resp = client.responses.create(
        model=model,
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {
                    "type": "input_image",
                    "image_base64": img_b64,
                },
            ],
        }],
    )

    text = resp.output_text.strip()
    return text

def ocr(img_path, output):
	debug = True
	duds = ["data/*.JPG", "data/*.jpg", "data/*.JPEG", "data/*.jpeg"]
	if img_path in duds:
		print(f"This isn't legit bro: {img_path}")
		sys.exit()


	text = slopenai(img_path)

	###

	#img = cv2.imread(img_path)
	#pytesseract(img)
	# Worked but didn't actually identify the stuff so good.
	
	#paddle(img)
	# Dependency hell

	#img = preprocess(img, debug)
	#text = easyocr(img)

	try:
		with open(output, 'a') as file:
			file.write(f"\n{img_path},{text}")
		print(f"\n{img_path},{text}")
	except IOError as e:
		print(f"Couldn't save to {output}")

if __name__ == "__main__":
	print("Running ocr.py from terminal")
	img_path = sys.argv[1]
	output = "data/output.txt"
	if len(sys.argv) > 2:
		output = sys.argv[2]
	ocr(img_path, output)