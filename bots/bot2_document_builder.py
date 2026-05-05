"""
bot2_document_builder.py
------------------------------------------
Bot 2 - Document Builder
หน้าที่: รับข้อมูลนักศึกษา 1 คน → สร้างใบสรุปคะแนนเป็นไฟล์ PDF
ดีไซน์: เรียบง่าย ข้อความล้วน (ตามที่ผู้ใช้เลือก)

รองรับ PDF 2 backend:
  • fpdf2    (แนะนำ - รองรับ Unicode/ภาษาไทยดี ใส่ฟอนต์ .ttf ได้ง่าย)
  • reportlab (fallback - ใช้เมื่อยังไม่ได้ติดตั้ง fpdf2)

โค้ดจะพยายาม import fpdf2 ก่อน ถ้าไม่เจอถึงจะใช้ reportlab
"""
from __future__ import annotations

# เพิ่มโฟลเดอร์แม่เข้า sys.path ให้ `import config` ทำงานได้ตอนรันเดี่ยว
import sys
from pathlib import Path
_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

import logging

import config

log = logging.getLogger("bot2")

# fpdf2 เรียกใช้ fontTools ภายใน ซึ่ง verbose เกินไป
# THSarabun มีตาราง AAT (feat/morx) ที่ fontTools subset ไม่เป็น - ใช้ ERROR เพื่อซ่อน WARNING
for _noisy in ("fontTools", "fontTools.subset", "fontTools.ttLib"):
    logging.getLogger(_noisy).setLevel(logging.ERROR)


# ---------------------------------------------------------
# ข้อความที่จะใส่ใน PDF (เหมือนกันทั้งสอง backend)
# ---------------------------------------------------------
def _render_lines(student: dict, class_stats: dict | None = None) -> list[tuple[str, str]]:
    """
    คืน list ของ (style, text)
      style = "title" | "h2" | "body" | "spacer" | "hr"
    class_stats: dict จาก compute_class_stats() (ถ้าไม่ส่ง จะไม่แสดง section สถิติชั้น)
    """
    lines: list[tuple[str, str]] = []
    lines.append(("title", "ใบสรุปคะแนนรายบุคคล"))
    lines.append(("h2", f"รายวิชา {config.COURSE_CODE} - {config.COURSE_NAME}"))
    lines.append(("body", f"ภาคเรียน {config.SEMESTER}   |   ผู้สอน: {config.INSTRUCTOR}"))
    lines.append(("hr", ""))

    lines.append(("body", f"รหัสนักศึกษา : {student['student_id']}"))
    lines.append(("body", f"ชื่อ-สกุล    : {student['name']}"))
    lines.append(("body", f"อีเมล        : {student['email']}"))
    lines.append(("spacer", ""))

    lines.append(("h2", "รายการคะแนน"))
    for item, full in config.ASSIGNMENTS.items():
        got = student["scores"].get(item, 0)
        lines.append(("body", f"  • {item:<20} {got:>6} / {full}"))
    lines.append(("hr", ""))

    lines.append(("h2", "สรุปผล"))
    lines.append(("body", f"คะแนนรวม  : {student['total']} / {student['full_total']}"))
    lines.append(("body", f"เปอร์เซ็นต์ : {student['percent']}%"))
    lines.append(("body", f"เกรด      : {student['grade']}"))
    lines.append(("spacer", ""))

    # ----- Section ใหม่: สถิติของทั้งชั้น -----
    if class_stats:
        lines.append(("hr", ""))
        lines.append(("h2", "สถิติของทั้งชั้น"))
        lines.append(("body", f"จำนวนนักศึกษา  : {class_stats['count']} คน"))
        lines.append(("body", f"คะแนนสูงสุด   : {class_stats['max']} / {student['full_total']}"))
        lines.append(("body", f"คะแนนต่ำสุด   : {class_stats['min']} / {student['full_total']}"))
        lines.append(("body", f"คะแนนเฉลี่ย   : {class_stats['avg']} / {student['full_total']}"))
        lines.append(("body", f"คะแนนมัธยฐาน  : {class_stats['median']} / {student['full_total']}"))

        # ตำแหน่งของนักศึกษาคนนี้
        rank = class_stats["ranks"].get(student["student_id"])
        if rank is not None:
            diff_from_avg = round(student["total"] - class_stats["avg"], 2)
            sign = "+" if diff_from_avg >= 0 else ""
            lines.append(("spacer", ""))
            lines.append(("body", f"อันดับของคุณ  : {rank} จาก {class_stats['count']} คน"))
            lines.append(("body", f"เทียบค่าเฉลี่ย : {sign}{diff_from_avg} คะแนน"))
        lines.append(("spacer", ""))

    lines.append(("body", "* เอกสารฉบับนี้สร้างโดยอัตโนมัติ หากคะแนนไม่ถูกต้อง"))
    lines.append(("body", "  กรุณาตอบกลับอีเมลนี้ภายใน 7 วัน"))
    return lines


# ---------------------------------------------------------
# ฟังก์ชันคำนวณสถิติทั้งชั้น (เรียกครั้งเดียวใน main.py)
# ---------------------------------------------------------
def compute_class_stats(students: list[dict]) -> dict:
    """คำนวณ max/min/avg/median/ranks ของคะแนนรวมทั้งชั้น"""
    if not students:
        return {"count": 0, "max": 0, "min": 0, "avg": 0, "median": 0, "ranks": {}}

    totals = [s["total"] for s in students]
    sorted_totals = sorted(totals)
    n = len(totals)

    # median
    if n % 2:
        median = sorted_totals[n // 2]
    else:
        median = (sorted_totals[n // 2 - 1] + sorted_totals[n // 2]) / 2

    # จัดอันดับ (คะแนนสูงสุด = อันดับ 1) ใช้ dense ranking
    # ถ้าคะแนนเท่ากัน ได้อันดับเท่ากัน
    ranked = sorted(students, key=lambda s: s["total"], reverse=True)
    ranks: dict[str, int] = {}
    prev_total = None
    current_rank = 0
    for idx, s in enumerate(ranked, start=1):
        if s["total"] != prev_total:
            current_rank = idx
            prev_total = s["total"]
        ranks[s["student_id"]] = current_rank

    return {
        "count": n,
        "max": max(totals),
        "min": min(totals),
        "avg": round(sum(totals) / n, 2),
        "median": round(median, 2),
        "ranks": ranks,
    }


# ---------------------------------------------------------
# Backend 1: fpdf2 (ถ้ามี)
# ---------------------------------------------------------
def _build_with_fpdf2(student: dict, out_path: Path, class_stats: dict | None = None) -> None:
    from fpdf import FPDF

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_margins(20, 20, 20)

    # ลงทะเบียนฟอนต์ไทย ถ้ามีไฟล์จริง
    use_thai = config.THAI_FONT_FILE.exists()
    if use_thai:
        pdf.add_font("THSarabun", "", str(config.THAI_FONT_FILE))
        if config.THAI_FONT_BOLD_FILE.exists():
            pdf.add_font("THSarabun", "B", str(config.THAI_FONT_BOLD_FILE))
        font_name = "THSarabun"
    else:
        log.warning("ไม่พบฟอนต์ไทย จะใช้ Helvetica แทน (ภาษาไทยอาจไม่แสดง)")
        font_name = "Helvetica"

    for style, text in _render_lines(student, class_stats):
        if style == "title":
            pdf.set_font(font_name, "B", 20)
            pdf.cell(0, 12, text, align="C", new_x="LMARGIN", new_y="NEXT")
        elif style == "h2":
            pdf.set_font(font_name, "B", 14)
            pdf.cell(0, 10, text, new_x="LMARGIN", new_y="NEXT")
        elif style == "body":
            pdf.set_font(font_name, "", 12)
            pdf.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        elif style == "spacer":
            pdf.ln(3)
        elif style == "hr":
            pdf.ln(1)
            y = pdf.get_y()
            pdf.line(20, y, 190, y)
            pdf.ln(3)

    pdf.output(str(out_path))


# ---------------------------------------------------------
# Backend 2: reportlab (fallback)
# ---------------------------------------------------------
def _build_with_reportlab(student: dict, out_path: Path, class_stats: dict | None = None) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    use_thai = config.THAI_FONT_FILE.exists()
    font_regular = "Helvetica"
    font_bold = "Helvetica-Bold"
    if use_thai:
        pdfmetrics.registerFont(TTFont("THSarabun", str(config.THAI_FONT_FILE)))
        font_regular = "THSarabun"
        if config.THAI_FONT_BOLD_FILE.exists():
            pdfmetrics.registerFont(TTFont("THSarabun-Bold", str(config.THAI_FONT_BOLD_FILE)))
            font_bold = "THSarabun-Bold"
        else:
            font_bold = "THSarabun"
    else:
        log.warning("ไม่พบฟอนต์ไทย จะใช้ Helvetica แทน (ภาษาไทยอาจไม่แสดง)")

    c = canvas.Canvas(str(out_path), pagesize=A4)
    width, height = A4
    x = 20 * mm
    y = height - 20 * mm

    for style, text in _render_lines(student, class_stats):
        if style == "title":
            c.setFont(font_bold, 20)
            tw = c.stringWidth(text, font_bold, 20)
            c.drawString((width - tw) / 2, y, text)
            y -= 12 * mm
        elif style == "h2":
            c.setFont(font_bold, 14)
            c.drawString(x, y, text)
            y -= 8 * mm
        elif style == "body":
            c.setFont(font_regular, 12)
            c.drawString(x, y, text)
            y -= 6 * mm
        elif style == "spacer":
            y -= 3 * mm
        elif style == "hr":
            c.setLineWidth(0.5)
            c.line(x, y, width - 20 * mm, y)
            y -= 5 * mm

    c.showPage()
    c.save()


# ---------------------------------------------------------
# จุดเข้าใช้งานหลัก
# ---------------------------------------------------------
def build_pdf(student: dict, output_dir: Path | None = None,
              class_stats: dict | None = None) -> Path:
    """สร้าง PDF สำหรับนักศึกษา 1 คน คืน Path ของไฟล์ที่สร้าง"""
    output_dir = output_dir or config.OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    # ตั้งชื่อไฟล์แบบปลอดภัย (ไม่ให้มีอักขระที่ FS ไม่ชอบ)
    safe_id = "".join(ch for ch in student["student_id"] if ch.isalnum() or ch in "-_")
    out_path = output_dir / f"{safe_id}_scores.pdf"

    try:
        import fpdf  # noqa: F401
        _build_with_fpdf2(student, out_path, class_stats)
        backend = "fpdf2"
    except ImportError:
        _build_with_reportlab(student, out_path, class_stats)
        backend = "reportlab"

    log.info("สร้าง PDF [%s]: %s", backend, out_path.name)
    return out_path


def build_all(students: list[dict], output_dir: Path | None = None,
              class_stats: dict | None = None) -> list[Path]:
    """สร้าง PDF ให้ทุกคนในลิสต์ คืน list ของ Path"""
    if class_stats is None:
        class_stats = compute_class_stats(students)
    return [build_pdf(s, output_dir, class_stats) for s in students]


if __name__ == "__main__":
    # ทดสอบเดี่ยว: python bot2_document_builder.py
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    demo = {
        "student_id": "6400999",
        "name": "Test Student",
        "email": "test@example.com",
        "scores": {k: v // 2 for k, v in config.ASSIGNMENTS.items()},
        "total": sum(config.ASSIGNMENTS.values()) // 2,
        "full_total": sum(config.ASSIGNMENTS.values()),
        "percent": 50.0,
        "grade": "D",
    }
    p = build_pdf(demo)
    print(f"สร้างไฟล์ทดสอบเรียบร้อย: {p}")
