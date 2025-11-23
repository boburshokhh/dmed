"""Генерация DOCX документов"""
import os
import uuid
from docx import Document
from storage import storage_manager
from docx_formatter import setup_a4_page_format
from docx_data_preparer import prepare_replacements
from docx_placeholder_replacer import replace_placeholders_in_document
from docx_qr_handler import add_qr_code_to_docx
from docx_template_creator import create_default_docx_template


def fill_docx_template(document_data, template_path=None, app=None):
    """Заполняет DOCX шаблон данными из формы"""
    try:
        # Определяем путь к шаблону
        if template_path and os.path.exists(template_path):
            doc = Document(template_path)
        else:
            template_folder = app.config.get('TEMPLATE_FOLDER', 'templates/docx_templates') if app else 'templates/docx_templates'
            default_template = os.path.join(template_folder, 'template.docx')
            if os.path.exists(default_template):
                doc = Document(default_template)
            else:
                doc = create_default_docx_template()
        
        # Настраиваем размеры страницы A4 и минимальные отступы
        setup_a4_page_format(doc)
        
        # Подготавливаем данные для замены
        replacements = prepare_replacements(document_data)
        
        # Заменяем плейсхолдеры
        replace_placeholders_in_document(doc, replacements)
        
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
        
        try:
            doc.save(output_path)
            
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
                print(f"[ERROR] Файл не был создан: {output_path}")
                return None
        except Exception as save_error:
            print(f"[ERROR] Ошибка при сохранении документа: {save_error}")
            import traceback
            print(traceback.format_exc())
            return None
        
    except Exception as e:
        import traceback
        error_msg = f"[ERROR] Ошибка при заполнении DOCX шаблона: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return None
