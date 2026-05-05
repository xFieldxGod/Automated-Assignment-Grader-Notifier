# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
img = Image.new("RGB", (W, H), (13, 17, 28))
draw = ImageDraw.Draw(img)

# Gradient background
for y in range(H):
    t = y / H
    r = int(13 + t * 10)
    g = int(17 + t * 12)
    b = int(28 + t * 20)
    draw.line([(0, y), (W, y)], fill=(r, g, b))

# Grid overlay
for x in range(0, W, 40):
    draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 8))
for y in range(0, H, 40):
    draw.line([(0, y), (W, y)], fill=(255, 255, 255, 8))

try:
    font_th = ImageFont.truetype("C:/Windows/Fonts/LEELAWAD.TTF", 18)
    font_th_sm = ImageFont.truetype("C:/Windows/Fonts/LEELAWAD.TTF", 14)
    font_lg = ImageFont.truetype("C:/Windows/Fonts/Calibrib.ttf", 38)
    font_md = ImageFont.truetype("C:/Windows/Fonts/Calibrib.ttf", 20)
    font_sm = ImageFont.truetype("C:/Windows/Fonts/Calibri.ttf", 15)
    font_xs = ImageFont.truetype("C:/Windows/Fonts/Calibri.ttf", 13)
except Exception:
    font_th = font_th_sm = font_lg = font_md = font_sm = font_xs = ImageFont.load_default()

# ---- Title ----
draw.text((60, 42), "Auto Grader", font=font_lg, fill=(255, 255, 255))
draw.text((60, 90), "ระบบตรวจงานและแจ้งผลอัตโนมัติ", font=font_th, fill=(100, 160, 255))

# Accent line
draw.rectangle([60, 125, 420, 128], fill=(80, 130, 255))

# ---- Pipeline boxes ----
boxes = [
    {
        "x": 60, "y": 165,
        "w": 300, "h": 200,
        "color": (20, 40, 80),
        "border": (60, 100, 200),
        "tag": "BOT 1",
        "tag_color": (60, 120, 255),
        "icon": "📊",
        "title": "Data Processor",
        "lines": ["Google Sheets / Excel", "โหลดข้อมูลนักศึกษา", "คำนวณคะแนนรวม", "สถิติทั้งชั้น"],
    },
    {
        "x": 420, "y": 165,
        "w": 300, "h": 200,
        "color": (30, 20, 70),
        "border": (130, 80, 220),
        "tag": "BOT 2",
        "tag_color": (160, 100, 255),
        "icon": "📄",
        "title": "Document Builder",
        "lines": ["สร้างใบสรุปคะแนน PDF", "ฟอนต์ภาษาไทย", "แสดงสถิติชั้นเรียน", "รายบุคคล"],
    },
    {
        "x": 780, "y": 165,
        "w": 300, "h": 200,
        "color": (20, 50, 35),
        "border": (40, 180, 100),
        "tag": "BOT 3",
        "tag_color": (50, 210, 120),
        "icon": "✉️",
        "title": "Communicator",
        "lines": ["Gmail API", "แนบ PDF อัตโนมัติ", "ส่งถึงนักศึกษาทุกคน", "dry-run / live mode"],
    },
]

for b in boxes:
    x, y, w, h = b["x"], b["y"], b["w"], b["h"]
    # Box fill
    draw.rounded_rectangle([x, y, x+w, y+h], radius=12, fill=b["color"], outline=b["border"], width=2)
    # Tag badge
    draw.rounded_rectangle([x+14, y+14, x+80, y+34], radius=6, fill=b["border"])
    draw.text((x+18, y+16), b["tag"], font=font_xs, fill=(255, 255, 255))
    # Icon + title
    draw.text((x+14, y+44), b["icon"] + "  " + b["title"], font=font_md, fill=(230, 230, 230))
    # Lines
    for i, line in enumerate(b["lines"]):
        draw.text((x+20, y+78 + i*26), "• " + line, font=font_th_sm, fill=(160, 180, 210))

# ---- Arrows between boxes ----
arrow_y = 165 + 100  # middle of boxes
for ax in [370, 730]:
    # Line
    draw.line([(ax, arrow_y), (ax+42, arrow_y)], fill=(120, 140, 180), width=3)
    # Arrowhead
    draw.polygon([(ax+42, arrow_y-7), (ax+42, arrow_y+7), (ax+56, arrow_y)], fill=(120, 140, 180))

# ---- Stats bar at bottom ----
draw.rectangle([60, 410, W-60, 412], fill=(50, 65, 100))

stats = [
    ("Google Sheets API", (100, 160, 255)),
    ("Gmail API", (50, 210, 120)),
    ("ReportLab / fpdf2", (200, 140, 255)),
    ("Python 3.x", (255, 200, 60)),
]
sx = 60
for label, color in stats:
    bb = draw.textbbox((0, 0), label, font=font_sm)
    tw = bb[2] - bb[0] + 20
    draw.rounded_rectangle([sx, 425, sx+tw, 455], radius=6, fill=(25, 35, 60), outline=color)
    draw.text((sx+10, 430), label, font=font_sm, fill=color)
    sx += tw + 12

# ---- Sample output card ----
cx, cy = 60, 480
draw.rounded_rectangle([cx, cy, cx+560, cy+190], radius=10,
                        fill=(18, 28, 50), outline=(50, 80, 140), width=1)
draw.text((cx+16, cy+12), "ตัวอย่างผลลัพธ์", font=font_th, fill=(180, 200, 255))
draw.line([(cx+16, cy+40), (cx+544, cy+40)], fill=(40, 60, 100), width=1)

rows = [
    ("6601234567", "นายทดสอบ ระบบ",    "42/50", "A",  (80, 220, 120)),
    ("6601234568", "นางสาวตัวอย่าง ข้อมูล", "38/50", "B+", (100, 180, 255)),
    ("6601234569", "นายตัวอย่าง สาม",   "30/50", "C+", (255, 200, 80)),
]
headers = ["รหัสนักศึกษา", "ชื่อ-สกุล", "คะแนน", "เกรด"]
hx = [cx+16, cx+130, cx+370, cx+470]
for i, h in enumerate(headers):
    draw.text((hx[i], cy+50), h, font=font_xs, fill=(120, 140, 170))
for ri, (sid, name, score, grade, gc) in enumerate(rows):
    ry = cy + 72 + ri * 32
    if ri % 2 == 0:
        draw.rectangle([cx+8, ry-4, cx+552, ry+22], fill=(25, 38, 65))
    draw.text((hx[0], ry), sid,   font=font_xs, fill=(200, 210, 230))
    draw.text((hx[1], ry), name,  font=font_th_sm, fill=(200, 210, 230))
    draw.text((hx[2], ry), score, font=font_xs, fill=(200, 210, 230))
    draw.rounded_rectangle([hx[3]-2, ry-3, hx[3]+34, ry+19], radius=4, fill=gc)
    draw.text((hx[3]+2, ry), grade, font=font_xs, fill=(10, 10, 10))

# ---- Email preview card ----
ex, ey = 660, 480
draw.rounded_rectangle([ex, ey, ex+560, ey+190], radius=10,
                        fill=(18, 28, 50), outline=(40, 160, 90), width=1)
draw.text((ex+16, ey+12), "ตัวอย่างอีเมลที่ส่ง", font=font_th, fill=(80, 220, 150))
draw.line([(ex+16, ey+40), (ex+544, ey+40)], fill=(30, 70, 50), width=1)

mail_lines = [
    ("To:",       "student@university.ac.th",          (120, 140, 170), (160, 200, 255)),
    ("Subject:",  "[คะแนน] วิชา CS101 ภาคเรียน 2/2567", (120, 140, 170), (230, 230, 230)),
    ("Attach:",   "score_6601234567.pdf",               (120, 140, 170), (200, 160, 255)),
    ("Status:",   "✅ ส่งสำเร็จ (3/3 คน)",              (120, 140, 170), (80, 220, 120)),
]
for i, (label, value, lc, vc) in enumerate(mail_lines):
    my = ey + 52 + i * 32
    draw.text((ex+16, my), label, font=font_sm, fill=lc)
    draw.text((ex+90, my), value, font=font_th_sm, fill=vc)

# Progress bar
draw.text((ex+16, ey+184), "Sent", font=font_xs, fill=(80, 220, 120))
draw.rectangle([ex+55, ey+189, ex+540, ey+197], fill=(30, 50, 40))
draw.rounded_rectangle([ex+55, ey+189, ex+540, ey+197], radius=3, fill=(40, 170, 90))

img.save("auto-grader-thumb.png")
print("Saved: auto-grader-thumb.png")
