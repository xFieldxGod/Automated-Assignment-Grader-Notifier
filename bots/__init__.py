"""
bots package
------------
3 Bot ที่ประกอบเป็นระบบ:
  • bot1_data_processor  - โหลดคะแนนจาก Excel / Google Sheet
  • bot2_document_builder - สร้างใบสรุปคะแนนเป็น PDF
  • bot3_communicator     - ส่งอีเมลพร้อมแนบ PDF
"""
from . import bot1_data_processor
from . import bot2_document_builder
from . import bot3_communicator
