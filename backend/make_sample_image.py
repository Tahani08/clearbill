from PIL import Image, ImageDraw, ImageFont

ROWS = [
    ("09/14/2026", "99284", "Emergency room visit", "$1,850.00"),
    ("09/14/2026", "80048", "Basic metabolic panel", "$210.00"),
    ("09/14/2026", "82947", "Glucose test", "$45.00"),
    ("09/14/2026", "36415", "Blood draw", "$30.00"),
    ("09/14/2026", "36415", "Blood draw", "$30.00"),
    ("09/14/2026", "71046", "Chest X-ray", "$400.00"),
]

img = Image.new("RGB", (1100, 620), "white")
d = ImageDraw.Draw(img)
title = ImageFont.load_default(size=34)
body = ImageFont.load_default(size=26)

d.text((40, 30), "RIVERSIDE GENERAL HOSPITAL", font=title, fill="black")
d.text((40, 80), "Itemized statement (SAMPLE, fake data)", font=body, fill="black")

cols = [40, 240, 400, 900]
for i, header in enumerate(["Date", "Code", "Description", "Amount"]):
    d.text((cols[i], 150), header, font=body, fill="black")

y = 200
for row in ROWS:
    for i, text in enumerate(row):
        d.text((cols[i], y), text, font=body, fill="black")
    y += 50

d.text((40, y + 30), "TOTAL DUE: $3,000.00", font=title, fill="black")
img.save("sample_bill.png")
print("Saved sample_bill.png")