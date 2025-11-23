"""Форматирование DOCX документов"""
from docx.shared import Cm


def setup_a4_page_format(doc):
    """Настраивает размеры страницы A4 и минимальные отступы для всех документов"""
    sections = doc.sections
    for section in sections:
        section.page_height = Cm(29.7)  # A4 высота
        section.page_width = Cm(21.0)   # A4 ширина
        section.left_margin = Cm(1.0)   # Минимальные отступы
        section.right_margin = Cm(1.0)
        section.top_margin = Cm(1.0)
        section.bottom_margin = Cm(1.0)

