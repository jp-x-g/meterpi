import csv, html, sys

def bake(dainput, daoutput):
    rows = list(csv.reader(open(dainput, encoding="utf-8")))
    print(rows)
    with open(daoutput, "w", encoding="utf-8") as f:
        f.write("<!doctype html><meta charset=utf-8><body style=\"font-family:monospace;\">\n")
        for entry in rows:
            path, text = entry[0], entry[1]
            f.write(f'<div><img src="{html.escape(path)}" style="max-width:600px"><br>'
                    f'{html.escape(text)}</div><hr>\n')
        f.write("</body>")

if __name__ == "__main__":
    print("Running makepage.py from terminal")
    dainput = "data/output.txt"
    if len(sys.argv) > 1:
        dainput = sys.argv[1]
    daoutput = "test.html"
    if len(sys.argv) > 2:
        daoutput = sys.argv[2]
    bake(dainput, daoutput)