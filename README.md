# Automated Assignment Grader & Notifier
### ระบบตรวจการบ้านและแจ้งคะแนนอัตโนมัติ

อ่านคะแนนจาก **Excel** หรือ **Google Sheets** → สร้างใบสรุปคะแนน **PDF** รายคน → ส่ง **อีเมล** พร้อมแนบ PDF ให้นักศึกษาทุกคน **ด้วยคำสั่งเดียว**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Course](https://img.shields.io/badge/Course-CSC490-orange)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## สารบัญ

1. [ภาพรวมระบบ](#1-ภาพรวมระบบ)
2. [ฟีเจอร์](#2-ฟีเจอร์)
3. [Quick Start (5 นาที)](#3-quick-start-5-นาที)
4. [สิ่งที่ต้องมีก่อนเริ่ม](#4-สิ่งที่ต้องมีก่อนเริ่ม)
5. [ติดตั้งครั้งแรก](#5-ติดตั้งครั้งแรก)
6. [วิธีใช้งาน](#6-วิธีใช้งาน)
7. [ปรับแต่งสำหรับวิชาของคุณ](#7-ปรับแต่งสำหรับวิชาของคุณ)
8. [โครงสร้างไฟล์](#8-โครงสร้างไฟล์)
9. [แก้ปัญหาที่พบบ่อย](#9-แก้ปัญหาที่พบบ่อย)
10. [License](#10-license)

---

## 1. ภาพรวมระบบ

ระบบแบ่งงานออกเป็น **3 Bot** ต่อกันแบบ pipeline ตามแนวคิด Separation of Concerns:

```
  Excel / Google Sheets
           │
           ▼
  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
  │  Bot 1          │      │  Bot 2          │      │  Bot 3          │
  │ Data Processor  │ ───► │ Document Builder│ ───► │ Communicator    │
  │                 │      │                 │      │                 │
  │ openpyxl /      │      │ fpdf2           │      │ ezgmail         │
  │ gspread         │      │                 │      │ (Gmail API)     │
  └─────────────────┘      └─────────────────┘      └─────────────────┘
       list[dict]              output/*.pdf           Email + PDF แนบ
```

| Bot | หน้าที่ | ไลบรารี |
|---|---|---|
| Bot 1: Data Processor | อ่านข้อมูลจาก Excel / Google Sheets, คำนวณคะแนน/เกรด | openpyxl, gspread |
| Bot 2: Document Builder | สร้าง PDF รายคนพร้อมสถิติทั้งชั้นและอันดับ | fpdf2 |
| Bot 3: Communicator | ส่งอีเมลพร้อมแนบ PDF ผ่าน Gmail API | ezgmail |

---

## 2. ฟีเจอร์

- **อ่านได้หลายแหล่ง** — Excel (`.xlsx`) หรือ Google Sheets เลือกได้ใน `config.py`
- **คำนวณอัตโนมัติ** — คะแนนรวม, เปอร์เซ็นต์, เกรดตามตารางที่กำหนดเอง
- **PDF ภาษาไทย** — ใช้ฟอนต์ THSarabun (มาตรฐานราชการไทย จาก DIP/SIPA) แสดงผลถูกต้อง
- **สถิติทั้งชั้น** — แต่ละ PDF มี max / min / avg / median และอันดับของนักศึกษาคนนั้น
- **Dry-run mode** — สร้าง PDF โดยไม่ส่งเมลจริง ปลอดภัยสำหรับทดสอบ
- **ตั้งค่าที่เดียว** — แก้ไขทุกอย่างใน `config.py` ไฟล์เดียว
- **CLI ยืดหยุ่น** — `--dry-run`, `--send`, `--limit N` ควบคุมการทำงานได้ทันที
- **Audit log** — บันทึก log ทุกครั้งที่รัน เก็บใน `output/run_*.log`

---

## 3. Quick Start (5 นาที)

> ทดสอบ dry-run กับข้อมูล sample ได้ทันที ไม่ต้องตั้ง Gmail API

```bash
# 1. Clone และเข้าโฟลเดอร์
git clone https://github.com/xFieldxGod/Automated-Assignment-Grader-Notifier.git
cd Automated-Assignment-Grader-Notifier

# 2. ติดตั้ง dependencies
py -m pip install -r requirements.txt

# 3. รัน dry-run กับข้อมูล sample 6 คน
py main.py --dry-run
```

PDF จะถูกสร้างในโฟลเดอร์ `output/` ทันที

---

## 4. สิ่งที่ต้องมีก่อนเริ่ม

| สิ่งที่ต้องมี | หมายเหตุ |
|---|---|
| Python 3.10+ | [python.org/downloads](https://www.python.org/downloads/) — ตอน install ติ๊ก **Add Python to PATH** |
| บัญชี Gmail | ใช้เป็นผู้ส่ง (ต้องการสำหรับ `--send` เท่านั้น) |
| `credentials.json` | จาก Google Cloud Console (ดูขั้นตอนในข้อ 5.2) |
| ไฟล์ Excel คะแนน | ดูตัวอย่างที่ `data/sample_scores.xlsx` |

---

## 5. ติดตั้งครั้งแรก

### 5.1 ติดตั้ง Python dependencies

```bash
py -m pip install -r requirements.txt
```

### 5.2 ตั้งค่า Gmail API (สำหรับส่งเมลจริง)

ทำครั้งเดียว ใช้เวลา ~10-15 นาที:

**ขั้นที่ 1 — สร้างโปรเจกต์บน Google Cloud**
1. เข้า [console.cloud.google.com](https://console.cloud.google.com/)
2. มุมบนซ้าย → **Select a project** → **NEW PROJECT** → ตั้งชื่อ → CREATE

**ขั้นที่ 2 — เปิดใช้ Gmail API**
1. เมนูซ้าย: **APIs & Services** → **Library**
2. ค้นหา "Gmail API" → **ENABLE**

**ขั้นที่ 3 — ตั้งค่า OAuth Consent Screen**
1. **APIs & Services** → **OAuth consent screen** → เลือก **External** → CREATE
2. กรอก App name, User support email, Developer contact email
3. **Test users** → **+ ADD USERS** → ใส่ Gmail ที่จะใช้ส่ง → SAVE AND CONTINUE

**ขั้นที่ 4 — สร้าง OAuth Credentials**
1. **APIs & Services** → **Credentials** → **+ CREATE CREDENTIALS** → **OAuth client ID**
2. Application type: **Desktop app** → CREATE
3. ดาวน์โหลด JSON → เปลี่ยนชื่อเป็น `credentials.json` → วางในโฟลเดอร์โปรเจกต์

**ขั้นที่ 5 — Authorize ครั้งแรก**
```bash
py -c "import ezgmail; ezgmail.init()"
```
เบราว์เซอร์จะเปิดขึ้น → เลือกบัญชี Gmail → Allow → จะได้ไฟล์ `token.json` อัตโนมัติ

### 5.3 (ถ้าใช้ Google Sheets แทน Excel)

1. เปิด `config.py` → ตั้ง `SOURCE = "gsheet"`
2. สร้าง Service Account ใน Google Cloud → ดาวน์โหลด key JSON
3. Share Google Sheet ให้ email ของ Service Account (Viewer)
4. กรอก `GSHEET_SPREADSHEET_ID` และ `GSHEET_WORKSHEET_NAME` ใน `config.py`

### 5.4 เตรียมไฟล์ Excel

ดูตัวอย่างที่ `data/sample_scores.xlsx` หัวคอลัมน์ต้องตรงกับค่าใน `config.py`:

| รหัสนักศึกษา | ชื่อ-สกุล | อีเมล | การบ้าน 1 | การบ้าน 2 | Quiz 1 | Midterm | Final Project |
|---|---|---|---|---|---|---|---|

ถ้าชื่อคอลัมน์ต่างออกไป แก้ใน `config.py` ได้ทันที ไม่ต้องแก้โค้ด

---

## 6. วิธีใช้งาน

### คำสั่งทั้งหมด

| คำสั่ง | คำอธิบาย |
|---|---|
| `py main.py --dry-run` | สร้าง PDF ทุกคน แต่ **ไม่ส่งเมล** (แนะนำสำหรับทดสอบ) |
| `py main.py --send` | สร้าง PDF และ **ส่งเมลจริง** ทุกคน |
| `py main.py --send --limit 1` | ส่งเมลเฉพาะคนแรก (ใช้ทดสอบกับอีเมลตัวเอง) |
| `py main.py --send --limit N` | ส่งเมลเฉพาะ N คนแรก |

### ตัวอย่าง Terminal Output

```
2026-04-23 14:41:03 [main] INFO: เริ่มงาน Automated Grader (dry_run=True, source=excel)
2026-04-23 14:41:03 [main] INFO: >>> Bot 1: โหลดข้อมูลนักศึกษา
2026-04-23 14:41:03 [main] INFO: สถิติของทั้งชั้น:
2026-04-23 14:41:03 [main] INFO:   • จำนวน        : 6 คน
2026-04-23 14:41:03 [main] INFO:   • สูงสุด        : 92 / 100
2026-04-23 14:41:03 [main] INFO:   • ต่ำสุด        : 35 / 100
2026-04-23 14:41:03 [main] INFO:   • ค่าเฉลี่ย     : 72.0 / 100
2026-04-23 14:41:03 [main] INFO:   • มัธยฐาน       : 76.5 / 100
2026-04-23 14:41:04 [main] INFO: >>> Bot 2: สร้างใบสรุปคะแนนเป็น PDF
2026-04-23 14:41:05 [main] INFO: >>> Bot 3: ส่งอีเมลแจ้งคะแนน (dry_run=True)
2026-04-23 14:41:05 [main] INFO: สรุปผลรวม:
2026-04-23 14:41:05 [main] INFO:   • นักศึกษาทั้งหมด : 6
2026-04-23 14:41:05 [main] INFO:   • PDF ที่สร้าง    : 6
2026-04-23 14:41:05 [main] INFO:   • ส่งเมลสำเร็จ    : 0 (dry-run)
```

> **หมายเหตุ:** ถ้าใช้ `cmd.exe` ตัวอักษรไทยในเทอร์มินัลอาจแสดงเพี้ยน แต่ไฟล์ log และ PDF ถูกต้องเสมอ แนะนำให้ใช้ **Windows Terminal** หรือ **PowerShell**

---

## 7. ปรับแต่งสำหรับวิชาของคุณ

แก้เพียง **`config.py`** ไฟล์เดียว:

| ตัวแปร | หน้าที่ | ตัวอย่าง |
|---|---|---|
| `SOURCE` | แหล่งข้อมูล | `"excel"` หรือ `"gsheet"` |
| `EXCEL_FILE` | พาธไฟล์ Excel | `DATA_DIR / "scores.xlsx"` |
| `COL_STUDENT_ID` | ชื่อคอลัมน์รหัสนักศึกษา | `"รหัสนักศึกษา"` |
| `COL_NAME` | ชื่อคอลัมน์ชื่อ-สกุล | `"ชื่อ-สกุล"` |
| `COL_EMAIL` | ชื่อคอลัมน์อีเมล | `"อีเมล"` |
| `ASSIGNMENTS` | ชื่องาน → คะแนนเต็ม | `{"การบ้าน 1": 10, "Midterm": 30}` |
| `GRADE_TABLE` | เกณฑ์ตัดเกรด | `[(80, "A"), (70, "B"), ...]` |
| `COURSE_CODE` / `COURSE_NAME` | ข้อมูลวิชา | `"CSC490"` |
| `SEMESTER` / `INSTRUCTOR` | ภาคเรียน / ผู้สอน | `"2/2568"` |
| `EMAIL_SUBJECT` / `EMAIL_BODY` | เทมเพลตอีเมล | ใช้ `{name}`, `{grade}`, `{total}` ฯลฯ |
| `DRY_RUN` | ค่าเริ่มต้น | `True` (ปลอดภัย) |

**Placeholders ที่ใช้ในอีเมลได้:** `{name}`, `{student_id}`, `{email}`, `{total}`, `{full_total}`, `{percent}`, `{grade}`, `{course_code}`, `{course_name}`, `{semester}`, `{instructor}`

---

## 8. โครงสร้างไฟล์

```
Automated-Assignment-Grader-Notifier/
├── main.py                      # ตัวหลัก เรียก Bot 1 → 2 → 3
├── config.py                    # ตั้งค่าทั้งหมดอยู่ที่นี่ (แก้ไฟล์นี้ไฟล์เดียว)
├── requirements.txt
├── .gitignore
│
├── bots/                        # 3 Bot หลักของระบบ
│   ├── bot1_data_processor.py   # อ่าน Excel / Google Sheets + คำนวณเกรด
│   ├── bot2_document_builder.py # สร้าง PDF (fpdf2 + ฟอนต์ไทย)
│   └── bot3_communicator.py     # ส่งอีเมล + PDF แนบ (ezgmail)
│
├── data/
│   ├── make_sample.py           # สร้างไฟล์ Excel ตัวอย่าง 6 คน
│   └── sample_scores.xlsx       # ข้อมูลทดสอบ
│
├── fonts/
│   ├── THSarabun.ttf            # ฟอนต์มาตรฐานราชการไทย (DIP/SIPA)
│   ├── THSarabun-Bold.ttf
│   ├── THSarabun-Italic.ttf
│   ├── THSarabun-BoldItalic.ttf
│   └── DIP_SIPA_Font_License.txt
│
├── docs/
│   ├── README.pdf               # คู่มือฉบับ PDF
│   └── presentation_script.md  # สคริปต์พรีเซนต์
│
└── output/                      # PDF + log ถูกสร้างที่นี่ (ไม่ถูก commit)
    ├── <student_id>_scores.pdf
    └── run_<timestamp>.log
```

> `credentials.json` และ `token.json` (Google OAuth) ไม่ถูก commit โดยอัตโนมัติ (ระบุใน `.gitignore`)

---

## 9. แก้ปัญหาที่พบบ่อย

<details>
<summary><strong>9.1 "Python was not found"</strong></summary>

Windows มี App Execution Alias ที่ redirect `python` ไป Microsoft Store

แก้: ใช้ `py` แทน `python` ทุกที่ หรือปิด alias ใน **Settings → Apps → Advanced app settings → App execution aliases**
</details>

<details>
<summary><strong>9.2 "could not find requirements.txt"</strong></summary>

ต้อง `cd` เข้าโฟลเดอร์โปรเจกต์ก่อน:
```bash
cd path\to\Automated-Assignment-Grader-Notifier
py -m pip install -r requirements.txt
```
</details>

<details>
<summary><strong>9.3 "Access blocked: Authorization Error" ตอน OAuth</strong></summary>

อีเมลที่ใช้ login ยังไม่ได้เพิ่มเป็น Test user

แก้: Google Cloud Console → **OAuth consent screen** → **Test users** → **+ ADD USERS** → ใส่อีเมลตัวเอง
</details>

<details>
<summary><strong>9.4 UnicodeEncodeError / ภาษาไทยในไฟล์ PDF ไม่แสดง</strong></summary>

ไม่พบฟอนต์ THSarabun

แก้: ตรวจว่าไฟล์ `fonts/THSarabun.ttf` และ `fonts/THSarabun-Bold.ttf` มีอยู่ และ path ใน `config.py` ถูกต้อง
</details>

<details>
<summary><strong>9.5 PDF เปิดมาเป็นกล่องทั้งหมด</strong></summary>

โปรแกรม viewer บางตัว (เช่น Edge preview) แสดงผลฟอนต์ผิด

แก้: เปิดด้วย **Adobe Acrobat Reader** หรือ **Google Chrome**
</details>

<details>
<summary><strong>9.6 token.json หมดอายุ</strong></summary>

ใน Testing mode ของ OAuth token จะ expire ใน 7 วัน

แก้: ลบ `token.json` แล้วรัน `py -c "import ezgmail; ezgmail.init()"` ใหม่
</details>

<details>
<summary><strong>9.7 Gmail ไม่ส่ง / rate limit</strong></summary>

Gmail free มี quota ~500 ฉบับ/วัน ถ้านักศึกษาเยอะให้ใช้ `--limit N` แบ่งรันเป็น batch
</details>

<details>
<summary><strong>9.8 เมลตกเข้า Spam</strong></summary>

อย่าใส่ลิงก์ short URL ใน body เยอะเกินไป และทดสอบส่งหาตัวเองก่อนด้วย `--limit 1`
</details>

<details>
<summary><strong>9.9 fontTools warning "feat/morx NOT subset"</strong></summary>

ไม่ใช่ error — THSarabun มีตาราง Apple-style ที่ fontTools ไม่รู้จัก PDF ยังคงถูกต้อง (โค้ดปิดเสียงไว้แล้วเมื่อรันผ่าน `main.py`)
</details>

<details>
<summary><strong>9.10 Excel ไฟล์เปิดไม่ได้ "File is not a zip file"</strong></summary>

OneDrive sync ค้างทำให้ไฟล์พัง

แก้: รัน `py data\make_sample.py` เพื่อสร้างใหม่ หรือปิด OneDrive แล้วลองอีกครั้ง
</details>

<details>
<summary><strong>9.11 ชื่อภาษาไทยในเทอร์มินัลแสดงเพี้ยน</strong></summary>

`cmd.exe` เรนเดอร์ภาษาไทยไม่ดี — ของจริงใน log และ PDF ถูกต้องเสมอ

แก้: เปลี่ยนไปใช้ **Windows Terminal** หรือ **PowerShell**
</details>

---

## 10. License

โค้ด: [MIT License](LICENSE)

ฟอนต์ THSarabun: [DIP&SIPA Font License](fonts/DIP_SIPA_Font_License.txt)
