"""
สคริปต์สร้างไฟล์ Excel ตัวอย่าง sample_scores.xlsx สำหรับทดสอบระบบ
รันครั้งเดียว: python data/make_sample.py
"""
from pathlib import Path
from openpyxl import Workbook

HERE = Path(__file__).resolve().parent
OUT = HERE / "sample_scores.xlsx"

HEADERS = [
    "รหัสนักศึกษา", "ชื่อ-สกุล", "อีเมล",
    "การบ้าน 1", "การบ้าน 2", "Quiz 1", "Midterm", "Final Project",
]

ROWS = [
    ("6400001", "สมชาย ใจดี",        "somchai@example.com", 10, 9, 18, 28, 27),
    ("6400002", "สมหญิง รักเรียน",    "somying@example.com",  8, 9, 16, 25, 26),
    ("6400003", "Nattawut P.",       "nattawut@example.com",  9, 10, 20, 30, 29),
    ("6400004", "ปิยะ ขยัน",          "piya@example.com",     6, 7, 14, 20, 22),
    ("6400005", "ธิดา มั่นใจ",        "thida@example.com",    5, 6, 10, 15, 18),
    ("6400006", "John Smith",        "john@example.com",      2, 3, 8,  12, 10),
]


def main():
    wb = Workbook()
    ws = wb.active
    ws.title = "Scores"
    ws.append(HEADERS)
    for row in ROWS:
        ws.append(row)

    # จัดความกว้างคอลัมน์สวย ๆ
    widths = [14, 25, 28, 10, 10, 10, 10, 12]
    for col_idx, w in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + col_idx)].width = w

    wb.save(OUT)
    print(f"สร้างไฟล์ตัวอย่างเรียบร้อย: {OUT}")


if __name__ == "__main__":
    main()
