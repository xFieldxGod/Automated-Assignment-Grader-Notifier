"""
main.py
------------------------------------------
ตัวประสานงาน 3 บอท: Bot1 → Bot2 → Bot3

การใช้งาน:
  python main.py                # ทำงานตาม config.DRY_RUN
  python main.py --send         # บังคับให้ส่งเมลจริง (override DRY_RUN)
  python main.py --dry-run      # บังคับไม่ส่งเมล (override DRY_RUN)
  python main.py --limit 3      # ทำแค่ 3 คนแรก (ใช้ทดสอบ)
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime

import config
from bots import bot1_data_processor as bot1
from bots import bot2_document_builder as bot2
from bots import bot3_communicator as bot3


def _setup_logging() -> None:
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    log_file = config.OUTPUT_DIR / f"run_{datetime.now():%Y%m%d_%H%M%S}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    # ปิดเสียง logger ของไลบรารีภายนอกที่ verbose เกินไป
    # THSarabun มีตาราง AAT (feat/morx) ที่ fontTools subset ไม่เป็น - ดัน ERROR เพื่อซ่อน WARNING
    for noisy in ("fontTools", "fontTools.subset", "fontTools.ttLib",
                  "PIL", "urllib3", "googleapiclient"):
        logging.getLogger(noisy).setLevel(logging.ERROR)
    logging.getLogger().info("บันทึก log ที่: %s", log_file)


def parse_args():
    p = argparse.ArgumentParser(description="Automated Assignment Grader & Notifier")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--send", action="store_true", help="ส่งเมลจริง (override DRY_RUN)")
    g.add_argument("--dry-run", action="store_true", help="ไม่ส่งเมล (override DRY_RUN)")
    p.add_argument("--limit", type=int, default=0,
                   help="ทำแค่ N คนแรก (0 = ทั้งหมด)")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    _setup_logging()
    log = logging.getLogger("main")

    # ตัดสินใจ dry-run
    if args.send:
        dry_run = False
    elif args.dry_run:
        dry_run = True
    else:
        dry_run = config.DRY_RUN

    log.info("=" * 60)
    log.info("เริ่มงาน Automated Grader (dry_run=%s, source=%s)", dry_run, config.SOURCE)
    log.info("=" * 60)

    # ----- Bot 1: Data Processor -----
    log.info(">>> Bot 1: โหลดข้อมูลนักศึกษา")
    students = bot1.load_students()
    if args.limit > 0:
        students = students[: args.limit]
        log.info("จำกัดจำนวนนักศึกษาที่ประมวลผล: %d คน", len(students))

    if not students:
        log.error("ไม่พบข้อมูลนักศึกษา - ยกเลิกการทำงาน")
        return 1

    # ----- คำนวณสถิติของทั้งชั้นก่อน (แสดงใน log + ฝังใน PDF รายคน) -----
    class_stats = bot2.compute_class_stats(students)
    full_total = students[0]["full_total"] if students else 0
    log.info("สถิติของทั้งชั้น:")
    log.info("  • จำนวน        : %d คน", class_stats["count"])
    log.info("  • สูงสุด        : %s / %s", class_stats["max"], full_total)
    log.info("  • ต่ำสุด        : %s / %s", class_stats["min"], full_total)
    log.info("  • ค่าเฉลี่ย     : %s / %s", class_stats["avg"], full_total)
    log.info("  • มัธยฐาน       : %s / %s", class_stats["median"], full_total)

    # ----- Bot 2: Document Builder -----
    log.info(">>> Bot 2: สร้างใบสรุปคะแนนเป็น PDF")
    pairs: list[tuple[dict, "object"]] = []
    for s in students:
        pdf_path = bot2.build_pdf(s, class_stats=class_stats)
        pairs.append((s, pdf_path))

    # ----- Bot 3: Communicator -----
    log.info(">>> Bot 3: ส่งอีเมลแจ้งคะแนน (dry_run=%s)", dry_run)
    summary = bot3.send_all(pairs, dry_run=dry_run)

    # ----- Summary -----
    log.info("=" * 60)
    log.info("สรุปผลรวม:")
    log.info("  • นักศึกษาทั้งหมด : %d", len(students))
    log.info("  • PDF ที่สร้าง    : %d", len(pairs))
    log.info("  • ส่งเมลสำเร็จ    : %d", summary["sent"])
    log.info("  • ส่งเมลไม่สำเร็จ : %d", summary["failed"])
    if summary["failed_list"]:
        log.info("  • รายชื่อที่ส่งไม่ผ่าน: %s", summary["failed_list"])
    log.info("=" * 60)
    return 0 if summary["failed"] == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
