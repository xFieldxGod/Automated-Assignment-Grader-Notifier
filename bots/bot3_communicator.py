"""
bot3_communicator.py
------------------------------------------
Bot 3 - Communicator
หน้าที่: ส่งอีเมลแจ้งคะแนนให้นักศึกษาแต่ละคน พร้อมแนบไฟล์ PDF

ใช้ไลบรารี: ezgmail (wrapper บน Gmail API ของ Al Sweigart)
  • ต้องทำ OAuth ครั้งแรก: วาง credentials.json ไว้ข้างสคริปต์แล้ว
    รันคำสั่ง python -c "import ezgmail; ezgmail.init()" หนึ่งครั้ง
  • ครั้งต่อ ๆ ไป ezgmail จะอ่าน token.json อัตโนมัติ

เพื่อความปลอดภัย จะเคารพ config.DRY_RUN:
  • True  → แค่ log ว่าจะส่งไปที่ใคร ไม่ส่งจริง (เหมาะกับทดสอบ)
  • False → ส่งจริงผ่าน Gmail
"""
from __future__ import annotations

# เพิ่มโฟลเดอร์แม่เข้า sys.path ให้ `import config` ทำงานได้ตอนรันเดี่ยว
import sys
from pathlib import Path
_PARENT = Path(__file__).resolve().parent.parent
if str(_PARENT) not in sys.path:
    sys.path.insert(0, str(_PARENT))

import logging
import re

import config

log = logging.getLogger("bot3")


# โดเมนสงวนตาม RFC 2606 / RFC 6761 - เอาไว้ทดสอบเท่านั้น ส่งจริงจะเด้งกลับเข้า inbox ผู้ส่ง
_RESERVED_DOMAINS = {
    "example.com", "example.org", "example.net",
    "test.com",
}
_RESERVED_TLDS = (".test", ".invalid", ".localhost", ".example")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _is_fake_email(email: str) -> bool:
    """ตรวจว่าเป็นอีเมลปลอม/โดเมนสงวนสำหรับทดสอบหรือไม่"""
    if not email or "@" not in email:
        return True
    domain = email.rsplit("@", 1)[-1].strip().lower()
    if domain in _RESERVED_DOMAINS:
        return True
    if any(domain.endswith(tld) for tld in _RESERVED_TLDS):
        return True
    if not _EMAIL_RE.match(email):
        return True
    return False


def _render_email(student: dict) -> tuple[str, str]:
    """สร้าง subject + body ของเมลจาก template ใน config"""
    ctx = {
        "name": student["name"],
        "student_id": student["student_id"],
        "email": student["email"],
        "total": student["total"],
        "full_total": student["full_total"],
        "percent": student["percent"],
        "grade": student["grade"],
        "course_code": config.COURSE_CODE,
        "course_name": config.COURSE_NAME,
        "semester": config.SEMESTER,
        "instructor": config.INSTRUCTOR,
    }
    subject = config.EMAIL_SUBJECT.format(**ctx)
    body = config.EMAIL_BODY.format(**ctx)
    return subject, body


def send_one(student: dict, pdf_path: Path, dry_run: bool | None = None) -> bool:
    """
    ส่งอีเมล 1 ฉบับ
    คืน True = ส่งสำเร็จ (หรือ dry-run ผ่าน), False = ส่งไม่สำเร็จ
    """
    dry_run = config.DRY_RUN if dry_run is None else dry_run
    subject, body = _render_email(student)

    # ด่านกรอง: ข้ามอีเมลที่รู้อยู่แล้วว่าส่งจริงแล้วจะเด้งกลับ
    if _is_fake_email(student["email"]):
        log.warning("ข้าม %s (%s): อีเมลไม่ถูกต้อง/เป็นโดเมนสำหรับทดสอบ จะไม่ส่งจริง",
                    student.get("name", ""), student["email"])
        return False

    if dry_run:
        log.info("[DRY-RUN] จะส่งเมลไปยัง %s | subject=%r | attach=%s",
                 student["email"], subject, pdf_path.name)
        return True

    try:
        import ezgmail
    except ImportError:
        log.error("ยังไม่ได้ติดตั้ง ezgmail (pip install ezgmail) - ข้ามการส่ง")
        return False

    try:
        ezgmail.send(
            recipient=student["email"],
            subject=subject,
            body=body,
            attachments=[str(pdf_path)],
        )
        log.info("ส่งเมลสำเร็จ → %s", student["email"])
        return True
    except Exception as e:  # noqa: BLE001
        log.exception("ส่งเมลไม่สำเร็จ → %s (%s)", student["email"], e)
        return False


def send_all(pairs: list[tuple[dict, Path]], dry_run: bool | None = None) -> dict:
    """
    ส่งเมลให้ทุกคน
    รับ list ของ tuple (student_dict, pdf_path)
    คืน dict สรุปผล: {"sent": N, "failed": M, "failed_list": [...]}
    """
    sent = 0
    failed: list[str] = []
    for student, pdf_path in pairs:
        ok = send_one(student, pdf_path, dry_run=dry_run)
        if ok:
            sent += 1
        else:
            failed.append(student["email"])

    summary = {"sent": sent, "failed": len(failed), "failed_list": failed}
    log.info("สรุปการส่งเมล: %s", summary)
    return summary


if __name__ == "__main__":
    # ทดสอบ Bot 3 เดี่ยว ๆ (DRY-RUN เสมอ)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
    demo_student = {
        "student_id": "6400999",
        "name": "Test Student",
        "email": "test@example.com",
        "total": 50,
        "full_total": 100,
        "percent": 50.0,
        "grade": "D",
    }
    send_one(demo_student, Path("dummy.pdf"), dry_run=True)
