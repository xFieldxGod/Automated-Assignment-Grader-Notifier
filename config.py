"""
config.py
ไฟล์ตั้งค่ากลางสำหรับระบบตรวจการบ้านและแจ้งคะแนนอัตโนมัติ
แก้ค่าในไฟล์นี้ไฟล์เดียวก็พอ ไม่ต้องไปแก้ในบอทแต่ละตัว
"""

from pathlib import Path

# =========================================================
# 1) ที่อยู่ไฟล์ / โฟลเดอร์
# =========================================================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
FONT_DIR = BASE_DIR / "fonts"

# ไฟล์ Excel ตัวอย่าง (ใช้เมื่อเลือก SOURCE = "excel")
EXCEL_FILE = DATA_DIR / "sample_scores.xlsx"

# ไฟล์ฟอนต์ไทย (โหลดเองแล้วใส่ลงโฟลเดอร์ fonts/)
# ถ้าไม่มีจะ fallback ไปใช้ Helvetica (ภาษาอังกฤษ)
# ใช้ THSarabun (ฟอนต์มาตรฐานราชการไทย จาก DIP/SIPA)
THAI_FONT_FILE = FONT_DIR / "THSarabun.ttf"
THAI_FONT_BOLD_FILE = FONT_DIR / "THSarabun-Bold.ttf"

# =========================================================
# 2) แหล่งข้อมูลคะแนน
#    เลือกได้: "excel" หรือ "gsheet"
# =========================================================
SOURCE = "excel"

# ---------- ถ้าเลือก "gsheet" ให้กรอกตรงนี้ ----------
# 1. สร้าง Service Account บน Google Cloud Console
# 2. ดาวน์โหลด credentials.json ไปวางในโฟลเดอร์ auto_grader/
# 3. Share Google Sheet ให้กับ email ของ service account
GSHEET_CREDENTIALS = BASE_DIR / "credentials.json"
GSHEET_SPREADSHEET_ID = "PUT_YOUR_SPREADSHEET_ID_HERE"
GSHEET_WORKSHEET_NAME = "Form Responses 1"

# =========================================================
# 3) โครงสร้างคอลัมน์ที่ Bot 1 จะอ่าน
#    ต้องตรงกับหัวคอลัมน์ในไฟล์ Excel / Google Sheet
# =========================================================
COL_STUDENT_ID = "รหัสนักศึกษา"
COL_NAME = "ชื่อ-สกุล"
COL_EMAIL = "อีเมล"

# คอลัมน์คะแนน: ชื่อหัว => คะแนนเต็ม
ASSIGNMENTS = {
    "การบ้าน 1": 10,
    "การบ้าน 2": 10,
    "Quiz 1": 20,
    "Midterm": 30,
    "Final Project": 30,
}
# คะแนนรวมเต็มคำนวณจากผลรวมของ ASSIGNMENTS โดยอัตโนมัติ

# =========================================================
# 4) ตั้งค่าวิชา / ผู้สอน
# =========================================================
COURSE_CODE = "CSC490"
COURSE_NAME = "Python Programming for Automation"
SEMESTER = "2/2568"
INSTRUCTOR = "อาจารย์ผู้สอน"

# =========================================================
# 5) อีเมลแจ้งคะแนน (Bot 3)
# =========================================================
EMAIL_SUBJECT = "[{course_code}] สรุปคะแนนรายบุคคล - {name}"

# ใช้ {placeholders} ได้ เช่น {name}, {student_id}, {total}, {full_total}, {grade}
EMAIL_BODY = """เรียน คุณ{name}

ขอส่งใบสรุปคะแนนรายวิชา {course_code} {course_name} ภาคเรียน {semester} ให้นักศึกษาทราบ
- คะแนนรวม: {total} / {full_total}
- เกรด (ประเมินเบื้องต้น): {grade}

รายละเอียดแบบเต็มดูได้จากไฟล์ PDF ที่แนบมาพร้อมเมลฉบับนี้ค่ะ/ครับ
หากมีข้อสงสัยหรือต้องการคัดค้านคะแนน กรุณาตอบกลับเมลนี้ภายใน 7 วัน

ขอบคุณครับ/ค่ะ
{instructor}
"""

# Dry-run mode: ถ้า True จะสร้าง PDF อย่างเดียว ไม่ส่งอีเมลจริง
# แนะนำให้เปิด True ตอนทดสอบครั้งแรกเสมอ
DRY_RUN = True

# =========================================================
# 6) ตารางเกรด (ใช้คำนวณเกรดจากเปอร์เซ็นต์)
# =========================================================
GRADE_TABLE = [
    (80, "A"),
    (75, "B+"),
    (70, "B"),
    (65, "C+"),
    (60, "C"),
    (55, "D+"),
    (50, "D"),
    (0,  "F"),
]
