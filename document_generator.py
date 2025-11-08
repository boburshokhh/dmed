"""Генерация DOCX документов"""
import os
import uuid
import re
from datetime import datetime
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from config import DOCX_FONT_NAME
from storage import storage_manager
from utils import generate_qr_code


def fill_docx_template(document_data, template_path=None, app=None):
    """Заполняет DOCX шаблон данными из формы"""
    try:
        # Определяем путь к шаблону
        if template_path and os.path.exists(template_path):
            doc = Document(template_path)
        else:
            # Используем стандартный шаблон или создаем новый
            template_folder = app.config.get('TEMPLATE_FOLDER', 'templates/docx_templates') if app else 'templates/docx_templates'
            default_template = os.path.join(template_folder, 'template.docx')
            if os.path.exists(default_template):
                doc = Document(default_template)
            else:
                # Создаем новый документ если шаблона нет
                doc = create_default_docx_template()
        
        # Подготавливаем данные для замены
        replacements = {
            '{{doc_number}}': document_data.get('doc_number', ''),
            '{{pin_code}}': document_data.get('pin_code', ''),
            '{{uuid}}': document_data.get('uuid', ''),
            '{{patient_name}}': document_data.get('patient_name', ''),
            '{{gender}}': document_data.get('gender', ''),
            '{{age}}': document_data.get('age', ''),
            '{{jshshir}}': document_data.get('jshshir', ''),
            '{{address}}': document_data.get('address', ''),
            '{{attached_medical_institution}}': document_data.get('attached_medical_institution', ''),
            '{{diagnosis}}': document_data.get('diagnosis', ''),
            '{{diagnosis_icd10_code}}': document_data.get('diagnosis_icd10_code', ''),
            '{{final_diagnosis}}': document_data.get('final_diagnosis', ''),
            '{{final_diagnosis_icd10_code}}': document_data.get('final_diagnosis_icd10_code', ''),
            '{{organization}}': document_data.get('organization', ''),
            '{{doctor_name}}': document_data.get('doctor_name', ''),
            '{{doctor_position}}': document_data.get('doctor_position', ''),
            '{{department_head_name}}': document_data.get('department_head_name', ''),
        }
        
        # Форматируем даты освобождения
        days_off_from = document_data.get('days_off_from')
        days_off_to = document_data.get('days_off_to')
        
        if days_off_from:
            if isinstance(days_off_from, str):
                try:
                    dt = datetime.fromisoformat(days_off_from.replace('Z', '+00:00'))
                    replacements['{{days_off_from}}'] = dt.strftime("%d.%m.%Y")
                except:
                    replacements['{{days_off_from}}'] = days_off_from[:10] if len(days_off_from) >= 10 else days_off_from
            else:
                replacements['{{days_off_from}}'] = days_off_from.strftime("%d.%m.%Y")
        else:
            replacements['{{days_off_from}}'] = ''
        
        if days_off_to:
            if isinstance(days_off_to, str):
                try:
                    dt = datetime.fromisoformat(days_off_to.replace('Z', '+00:00'))
                    replacements['{{days_off_to}}'] = dt.strftime("%d.%m.%Y")
                except:
                    replacements['{{days_off_to}}'] = days_off_to[:10] if len(days_off_to) >= 10 else days_off_to
            else:
                replacements['{{days_off_to}}'] = days_off_to.strftime("%d.%m.%Y")
        else:
            replacements['{{days_off_to}}'] = ''
        
        # Формируем строку периода освобождения
        if replacements['{{days_off_from}}'] and replacements['{{days_off_to}}']:
            replacements['{{days_off_period}}'] = f"{replacements['{{days_off_from}}']} - {replacements['{{days_off_to}}']}"
        elif replacements['{{days_off_from}}']:
            replacements['{{days_off_period}}'] = replacements['{{days_off_from}}']
        else:
            replacements['{{days_off_period}}'] = ''
        
        # Форматируем дату выдачи документа (с временем)
        issue_date = document_data.get('issue_date')
        if issue_date:
            if isinstance(issue_date, str):
                try:
                    dt = datetime.fromisoformat(issue_date.replace('Z', '+00:00'))
                    date_str = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    try:
                        dt = datetime.strptime(issue_date[:16], "%Y-%m-%dT%H:%M")
                        date_str = dt.strftime("%d.%m.%Y %H:%M")
                    except:
                        date_str = issue_date[:10] if len(issue_date) >= 10 else issue_date
            else:
                date_str = issue_date.strftime("%d.%m.%Y %H:%M")
        else:
            date_str = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        replacements['{{issue_date}}'] = date_str
        replacements['{{current_date}}'] = datetime.now().strftime("%d.%m.%Y %H:%M")
        
        # Флаг для отслеживания первого вхождения {{pin_code}}
        pin_code_first_occurrence = {'found': False}
        
        # Функция для замены плейсхолдеров с сохранением форматирования
        def replace_placeholders_with_font(paragraph, replacements, font_name=DOCX_FONT_NAME):
            """Заменяет плейсхолдеры в параграфе, устанавливая шрифт Times New Roman для замененных значений."""
            try:
                full_text = paragraph.text
                
                # Проверяем, есть ли плейсхолдеры
                has_placeholder = False
                for key in replacements.keys():
                    if key in full_text:
                        has_placeholder = True
                        break
                
                if not has_placeholder:
                    return
                
                # Сохраняем выравнивание и стиль параграфа
                alignment = paragraph.alignment
                original_font_size = None
                if paragraph.runs:
                    try:
                        original_font_size = paragraph.runs[0].font.size
                    except:
                        pass
                
                # Очищаем параграф
                paragraph.clear()
                if alignment:
                    paragraph.alignment = alignment
                
                # Разбиваем текст на части и обрабатываем каждый плейсхолдер отдельно
                pattern = '|'.join(re.escape(key) for key in replacements.keys())
                parts = re.split(f'({pattern})', full_text)
                
                for part in parts:
                    if not part:
                        continue
                    
                    if part in replacements:
                        value = str(replacements[part])
                        run = paragraph.add_run(value)
                        
                        # Специальная обработка для {{pin_code}}
                        if part == '{{pin_code}}':
                            if not pin_code_first_occurrence['found']:
                                try:
                                    run.font.name = font_name
                                except:
                                    try:
                                        run.font.name = 'Times New Roman'
                                    except:
                                        pass
                                if original_font_size:
                                    try:
                                        run.font.size = original_font_size
                                    except:
                                        pass
                                pin_code_first_occurrence['found'] = True
                            else:
                                run.font.size = Pt(24)
                                run.font.name = 'Calibri'
                                run.bold = True
                        else:
                            try:
                                run.font.name = font_name
                            except:
                                try:
                                    run.font.name = 'Times New Roman'
                                except:
                                    pass
                            if original_font_size:
                                try:
                                    run.font.size = original_font_size
                                except:
                                    pass
                    else:
                        run = paragraph.add_run(part)
                        try:
                            run.font.name = font_name
                        except:
                            try:
                                run.font.name = 'Times New Roman'
                            except:
                                pass
                        if original_font_size:
                            try:
                                run.font.size = original_font_size
                            except:
                                pass
            except Exception as e:
                print(f"Ошибка при замене плейсхолдеров в параграфе: {e}")
                import traceback
                print(traceback.format_exc())
                try:
                    simple_text = full_text
                    for key, value in replacements.items():
                        simple_text = simple_text.replace(key, str(value))
                    paragraph.text = simple_text
                except Exception as fallback_error:
                    print(f"Ошибка при fallback замене: {fallback_error}")
        
        # Заменяем плейсхолдеры в параграфах
        for paragraph in doc.paragraphs:
            replace_placeholders_with_font(paragraph, replacements)
        
        # Заменяем плейсхолдеры в таблицах
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_placeholders_with_font(paragraph, replacements)
        
        # Заменяем плейсхолдеры в колонтитулах
        for section in doc.sections:
            if section.header:
                for paragraph in section.header.paragraphs:
                    replace_placeholders_with_font(paragraph, replacements)
                for table in section.header.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                replace_placeholders_with_font(paragraph, replacements)
            
            if section.footer:
                for paragraph in section.footer.paragraphs:
                    replace_placeholders_with_font(paragraph, replacements)
                for table in section.footer.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for paragraph in cell.paragraphs:
                                replace_placeholders_with_font(paragraph, replacements)
        
        # Добавляем QR-код
        add_qr_code_to_docx(doc, document_data.get('pin_code', ''), app, document_data.get('uuid', ''))
        
        # Сохраняем заполненный документ
        upload_folder = app.config.get('UPLOAD_FOLDER', 'static/generated_documents') if app else 'static/generated_documents'
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder, exist_ok=True)
        
        document_uuid = document_data.get('uuid', '')
        if not document_uuid:
            document_uuid = str(uuid.uuid4())
        output_path = os.path.join(upload_folder, f"{document_uuid}.docx")
        
        print(f"Сохраняем документ: {output_path}")
        try:
            doc.save(output_path)
            print(f"Документ успешно сохранен: {output_path}")
            
            if os.path.exists(output_path):
                with open(output_path, 'rb') as f:
                    docx_data = f.read()
                
                docx_filename = f"{document_uuid}.docx"
                stored_path = storage_manager.save_file(docx_data, docx_filename, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                
                if storage_manager.use_minio and os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except:
                        pass
                
                return stored_path
            else:
                print(f"ОШИБКА: Файл не был создан: {output_path}")
                return None
        except Exception as save_error:
            print(f"ОШИБКА при сохранении документа: {save_error}")
            import traceback
            print(traceback.format_exc())
            return None
        
    except Exception as e:
        import traceback
        error_msg = f"Ошибка при заполнении DOCX шаблона: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return None


def create_default_docx_template():
    """Создает стандартный DOCX шаблон если его нет"""
    doc = Document()
    
    try:
        title = doc.add_heading("Ta'lim olayotgan shaxslar uchun mehnatga layoqatsizlik ma'lumotnomasi", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    except:
        title = doc.add_paragraph("Ta'lim olayotgan shaxslar uchun mehnatga layoqatsizlik ma'lumotnomasi")
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if title.runs:
            title.runs[0].font.bold = True
            title.runs[0].font.name = DOCX_FONT_NAME
    
    org_para = doc.add_paragraph("O'zbekiston Respublikasi Sog'liqni saqlash vazirligi")
    org_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    org_para = doc.add_paragraph("4 - sonli oilaviy poliklinika")
    org_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph(f"Ro'yhatga olingan sana: {{issue_date}}")
    doc.add_paragraph(f"No {{doc_number}}")
    
    try:
        doc.add_heading('Vaqtincha mehnatga layoqatsiz fuqaro haqidagi ma\'lumotlar:', 1)
    except:
        para = doc.add_paragraph('Vaqtincha mehnatga layoqatsiz fuqaro haqidagi ma\'lumotlar:')
        para.runs[0].font.bold = True
        para.runs[0].font.name = DOCX_FONT_NAME
    
    doc.add_paragraph(f"FISH: {{patient_name}}")
    doc.add_paragraph(f"Jinsi: {{gender}}")
    doc.add_paragraph(f"JShShIR: {{jshshir}}")
    doc.add_paragraph(f"Yoshi: {{age}}")
    doc.add_paragraph(f"Yashash manzili: {{address}}")
    doc.add_paragraph(f"Biriktirilgan tibbiy muassasa: {{attached_medical_institution}}")
    doc.add_paragraph(f"Tashxis (KXT-10 kodi va Nomi): {{diagnosis_icd10_code}}: {{diagnosis}}")
    doc.add_paragraph(f"Yakuniy tashxis (Nomi va KXT-10 kodi): {{final_diagnosis_icd10_code}}: {{final_diagnosis}}")
    doc.add_paragraph(f"Ro'yhatga olingan sana: {{issue_date}}")
    doc.add_paragraph(f"No: {{doc_number}}")
    doc.add_paragraph(f"Davolovchi shifokor FISH: {{doctor_name}}")
    doc.add_paragraph(f"Bo'lim boshlig'i (mas'ul shaxs) FISH: {{department_head_name}}")
    doc.add_paragraph(f"Ishdan ozod etilgan kunlar: {{days_off_period}}")
    
    try:
        doc.add_heading('Shifokor ma\'lumotlari:', 1)
    except:
        para = doc.add_paragraph('Shifokor ma\'lumotlari:')
        if para.runs:
            para.runs[0].font.bold = True
            para.runs[0].font.name = DOCX_FONT_NAME
        else:
            run = para.add_run('Shifokor ma\'lumotlari:')
            run.font.bold = True
            run.font.name = DOCX_FONT_NAME
    
    doc.add_paragraph(f"FISH: {{doctor_name}}")
    doc.add_paragraph(f"Lavozim: {{doctor_position}}")
    doc.add_paragraph(f"PIN-kod: {{pin_code}}")
    
    return doc


def add_qr_code_to_docx(doc, pin_code, app=None, document_uuid=None):
    """Добавляет QR-код в DOCX документ"""
    try:
        # Генерируем URL для QR-кода: dmed.netlify.app/access/{{uuid}}
        if document_uuid:
            qr_url = f"https://dmed.netlify.app/access/{document_uuid}"
        else:
            # Fallback на старый способ, если UUID не передан
            try:
                from flask import url_for
                qr_url = url_for('verify_document', _external=True)
            except RuntimeError:
                qr_url = '/verify'
        
        qr_img = generate_qr_code(qr_url)
        
        upload_folder = app.config.get('UPLOAD_FOLDER', 'static/generated_documents') if app else 'static/generated_documents'
        qr_temp_path = os.path.join(upload_folder, f'qr_temp_{pin_code}.png')
        if not os.path.exists(os.path.dirname(qr_temp_path)):
            os.makedirs(os.path.dirname(qr_temp_path), exist_ok=True)
        
        with open(qr_temp_path, 'wb') as f:
            qr_img.save(f, 'PNG')
        
        qr_placeholder_found = False
        
        def replace_qr_placeholder(paragraph):
            nonlocal qr_placeholder_found
            if '{{qr_code}}' in paragraph.text:
                qr_placeholder_found = True
                alignment = paragraph.alignment
                paragraph.clear()
                if alignment:
                    paragraph.alignment = alignment
                run = paragraph.add_run()
                run.add_picture(qr_temp_path, width=Inches(1.5))
                return True
            return False
        
        for paragraph in doc.paragraphs:
            if replace_qr_placeholder(paragraph):
                break
        
        if not qr_placeholder_found:
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        for paragraph in cell.paragraphs:
                            if replace_qr_placeholder(paragraph):
                                qr_placeholder_found = True
                                break
                        if qr_placeholder_found:
                            break
                    if qr_placeholder_found:
                        break
                if qr_placeholder_found:
                    break
        
        if not qr_placeholder_found:
            for section in doc.sections:
                if section.header:
                    for paragraph in section.header.paragraphs:
                        if replace_qr_placeholder(paragraph):
                            qr_placeholder_found = True
                            break
                    if not qr_placeholder_found:
                        for table in section.header.tables:
                            for row in table.rows:
                                for cell in row.cells:
                                    for paragraph in cell.paragraphs:
                                        if replace_qr_placeholder(paragraph):
                                            qr_placeholder_found = True
                                            break
                                    if qr_placeholder_found:
                                        break
                                if qr_placeholder_found:
                                    break
                            if qr_placeholder_found:
                                break
                
                if qr_placeholder_found:
                    break
                
                if section.footer:
                    for paragraph in section.footer.paragraphs:
                        if replace_qr_placeholder(paragraph):
                            qr_placeholder_found = True
                            break
                    if not qr_placeholder_found:
                        for table in section.footer.tables:
                            for row in table.rows:
                                for cell in row.cells:
                                    for paragraph in cell.paragraphs:
                                        if replace_qr_placeholder(paragraph):
                                            qr_placeholder_found = True
                                            break
                                    if qr_placeholder_found:
                                        break
                                if qr_placeholder_found:
                                    break
                            if qr_placeholder_found:
                                break
                
                if qr_placeholder_found:
                    break
        
        if not qr_placeholder_found:
            last_para = doc.add_paragraph()
            last_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = last_para.add_run()
            run.add_picture(qr_temp_path, width=Inches(1.5))
        
        if os.path.exists(qr_temp_path):
            os.remove(qr_temp_path)
            
    except Exception as e:
        print(f"Ошибка при добавлении QR-кода: {e}")
        import traceback
        print(traceback.format_exc())

