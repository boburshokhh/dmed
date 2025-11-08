# Настройка кодировки для Windows консоли
import sys
import io
if sys.platform == 'win32':
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from flask import Flask, render_template, request, jsonify, send_file, url_for
from datetime import datetime
from io import BytesIO
import os
import uuid
from config import SECRET_KEY, UPLOAD_FOLDER
from storage import storage_manager
from database import db_insert, db_select, db_update
from utils import generate_document_number, generate_pin_code
from document_generator import fill_docx_template
from converter import convert_docx_to_pdf_from_docx

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATE_FOLDER'] = 'templates/docx_templates'

# Создаем директории если их нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['TEMPLATE_FOLDER'], exist_ok=True)


# Маршруты

@app.route('/')
def index():
    """Главная страница с формой"""
    return render_template('index.html')


@app.route('/create-document', methods=['POST'])
def create_document():
    """Создание нового документа"""
    try:
        data = request.get_json()
        
        # Генерируем уникальные идентификаторы
        doc_number = generate_document_number()
        pin_code = generate_pin_code()
        document_uuid = str(uuid.uuid4())
        
        # Обрабатываем даты освобождения
        days_off_from = data.get('days_off_from')
        days_off_to = data.get('days_off_to')
        
        # Обрабатываем дату выдачи документа
        issue_date_input = data.get('issue_date')
        if issue_date_input:
            try:
                date_part = datetime.strptime(issue_date_input, "%Y-%m-%d")
                now = datetime.now()
                issue_date = date_part.replace(hour=now.hour, minute=now.minute, second=now.second).isoformat()
            except:
                issue_date = issue_date_input
        else:
            issue_date = datetime.now().isoformat()
        
        document_data = {
            'doc_number': doc_number,
            'pin_code': pin_code,
            'uuid': document_uuid,
            'patient_name': data.get('patient_name'),
            'gender': data.get('gender'),
            'age': data.get('age'),
            'jshshir': data.get('jshshir'),
            'address': data.get('address'),
            'attached_medical_institution': data.get('attached_medical_institution'),
            'diagnosis': data.get('diagnosis'),
            'diagnosis_icd10_code': data.get('diagnosis_icd10_code'),
            'final_diagnosis': data.get('final_diagnosis'),
            'final_diagnosis_icd10_code': data.get('final_diagnosis_icd10_code'),
            'organization': data.get('organization'),
            'doctor_name': data.get('doctor_name'),
            'doctor_position': data.get('doctor_position'),
            'department_head_name': data.get('department_head_name'),
            'days_off_from': days_off_from if days_off_from else None,
            'days_off_to': days_off_to if days_off_to else None,
            'issue_date': issue_date
        }
        
        # Вставляем документ в БД
        try:
            print(f"DEBUG: Вставка документа в БД...")
            created_document = db_insert('documents', document_data)
            
            if not created_document:
                print("ERROR: db_insert вернул None")
                return jsonify({'success': False, 'error': 'Ошибка создания документа'}), 500
            
            document_id = created_document['id']
            print(f"DEBUG: Документ создан с ID: {document_id}")
        except Exception as db_error:
            print(f"ERROR: Ошибка при создании документа: {db_error}")
            import traceback
            print(traceback.format_exc())
            return jsonify({'success': False, 'error': f'Ошибка создания документа: {str(db_error)}'}), 500
        
        # Генерируем DOCX документ
        docx_path = fill_docx_template(created_document, app=app)
        
        if not docx_path:
            error_detail = "Не удалось создать DOCX документ. Проверьте логи сервера."
            print(f"ОШИБКА: {error_detail}")
            import traceback
            print(traceback.format_exc())
            return jsonify({'success': False, 'error': error_detail}), 500
        
        # Сохраняем путь к DOCX в БД
        try:
            db_update('documents', {'docx_path': docx_path}, 'id = %s', [document_id])
        except Exception as db_error:
            print(f"Предупреждение: Не удалось обновить путь к DOCX в БД: {db_error}")
        
        # Конвертируем DOCX в PDF
        print(f"[INFO] Начинаем конвертацию DOCX->PDF. docx_path={docx_path}")
        pdf_path = convert_docx_to_pdf_from_docx(docx_path, created_document, app=app)
        
        if not pdf_path:
            error_detail = "Не удалось конвертировать DOCX в PDF. Проверьте логи сервера."
            print(f"[ERROR] {error_detail}")
            print(f"[ERROR] docx_path был: {docx_path}")
            print(f"[ERROR] Проверьте, установлены ли библиотеки: mammoth, weasyprint, docx2pdf")
            import traceback
            print(traceback.format_exc())
            return jsonify({'success': False, 'error': error_detail}), 500
        
        print(f"[INFO] Конвертация завершена, pdf_path={pdf_path}")
        
        # Проверяем существование файла
        file_exists = False
        if storage_manager.use_minio:
            file_exists = storage_manager.file_exists(pdf_path)
            print(f"[INFO] Проверка файла в MinIO: {file_exists}")
        else:
            file_exists = os.path.exists(pdf_path)
            print(f"[INFO] Проверка локального файла: {file_exists}, путь: {pdf_path}")
        
        if not file_exists:
            error_detail = f"PDF файл не найден после конвертации: {pdf_path}"
            print(f"[ERROR] {error_detail}")
            return jsonify({'success': False, 'error': error_detail}), 500
        
        # Обновляем путь к PDF в базе данных
        try:
            db_update('documents', {'pdf_path': pdf_path}, 'id = %s', [document_id])
        except Exception as db_error:
            print(f"Предупреждение: Не удалось обновить путь к PDF в БД: {db_error}")
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'doc_number': doc_number,
            'pin_code': pin_code,
            'download_url': url_for('download_document', doc_id=document_id)
        })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/download/<int:doc_id>')
def download_document(doc_id):
    """Скачивание PDF документа"""
    try:
        document = db_select('documents', 'id = %s', [doc_id], fetch_one=True)
        
        if not document:
            return "Документ не найден", 404
        
        document_uuid = document.get('uuid', '')
        if not document_uuid:
            document_uuid = str(uuid.uuid4())
        
        pdf_path = document.get('pdf_path')
        filename = f'{document_uuid}.pdf'
        
        # Пытаемся получить файл из хранилища
        if pdf_path:
            file_data = storage_manager.get_file(pdf_path)
            if file_data:
                return send_file(
                    BytesIO(file_data),
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/pdf'
                )
            
            if os.path.exists(pdf_path):
                return send_file(
                    pdf_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/pdf'
                )
        
        # Если PDF не существует, пытаемся переконвертировать из DOCX
        docx_path = document.get('docx_path')
        if docx_path:
            print(f"[INFO] PDF не найден, переконвертируем из DOCX: {docx_path}")
            pdf_path = convert_docx_to_pdf_from_docx(docx_path, document, app=app)
            if pdf_path:
                db_update('documents', {'pdf_path': pdf_path}, 'id = %s', [doc_id])
                file_data = storage_manager.get_file(pdf_path)
                if file_data:
                    return send_file(
                        BytesIO(file_data),
                        as_attachment=True,
                        download_name=filename,
                        mimetype='application/pdf'
                    )
                if os.path.exists(pdf_path):
                    return send_file(
                        pdf_path,
                        as_attachment=True,
                        download_name=filename,
                        mimetype='application/pdf'
                    )
        
        return "PDF файл не найден и не удалось переконвертировать из DOCX", 404
    except Exception as e:
        return f"Ошибка: {str(e)}", 500


@app.route('/download-by-uuid/<uuid>')
def download_by_uuid(uuid):
    """Скачивание PDF документа по UUID (для QR-кода)"""
    try:
        document = db_select('documents', 'uuid = %s', [uuid], fetch_one=True)
        
        if not document:
            return "Документ не найден", 404
        
        pdf_path = document.get('pdf_path')
        filename = f'{uuid}.pdf'
        
        if pdf_path:
            file_data = storage_manager.get_file(pdf_path)
            if file_data:
                return send_file(
                    BytesIO(file_data),
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/pdf'
                )
            
            if os.path.exists(pdf_path):
                return send_file(
                    pdf_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/pdf'
                )
        
        # Если PDF не существует, пытаемся переконвертировать из DOCX
        docx_path = document.get('docx_path')
        if docx_path:
            print(f"[INFO] PDF не найден, переконвертируем из DOCX: {docx_path}")
            pdf_path = convert_docx_to_pdf_from_docx(docx_path, document, app=app)
            if pdf_path:
                db_update('documents', {'pdf_path': pdf_path}, 'uuid = %s', [uuid])
                file_data = storage_manager.get_file(pdf_path)
                if file_data:
                    return send_file(
                        BytesIO(file_data),
                        as_attachment=True,
                        download_name=filename,
                        mimetype='application/pdf'
                    )
                if os.path.exists(pdf_path):
                    return send_file(
                        pdf_path,
                        as_attachment=True,
                        download_name=filename,
                        mimetype='application/pdf'
                    )
        
        return "PDF файл не найден и не удалось переконвертировать из DOCX", 404
    except Exception as e:
        return f"Ошибка: {str(e)}", 500


@app.route('/download-docx/<int:doc_id>')
def download_docx(doc_id):
    """Скачивание DOCX документа"""
    try:
        document = db_select('documents', 'id = %s', [doc_id], fetch_one=True)
        
        if not document:
            return "Документ не найден", 404
        
        docx_path = document.get('docx_path')
        doc_number = document.get('doc_number', 'unknown')
        filename = f'spravka_{doc_number}.docx'
        
        if docx_path:
            file_data = storage_manager.get_file(docx_path)
            if file_data:
                return send_file(
                    BytesIO(file_data),
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
        
        if docx_path and os.path.exists(docx_path):
            return send_file(
                docx_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        
        # Если DOCX не существует, генерируем его заново
        docx_path = fill_docx_template(document, app=app)
        if docx_path:
            db_update('documents', {'docx_path': docx_path}, 'id = %s', [doc_id])
            file_data = storage_manager.get_file(docx_path)
            if file_data:
                return send_file(
                    BytesIO(file_data),
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
            if os.path.exists(docx_path):
                return send_file(
                    docx_path,
                    as_attachment=True,
                    download_name=filename,
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
        
        return "DOCX файл не найден", 404
    except Exception as e:
        return f"Ошибка: {str(e)}", 500


@app.route('/convert-docx-to-pdf/<int:doc_id>')
def convert_docx_to_pdf_route(doc_id):
    """Конвертирует DOCX документ в PDF и возвращает PDF файл"""
    try:
        document = db_select('documents', 'id = %s', [doc_id], fetch_one=True)
        
        if not document:
            return jsonify({'success': False, 'error': 'Документ не найден'}), 404
        
        docx_path = document.get('docx_path')
        
        if not docx_path:
            return jsonify({'success': False, 'error': 'DOCX файл не найден. Невозможно конвертировать в PDF.'}), 404
        
        docx_data = storage_manager.get_file(docx_path)
        if not docx_data and not os.path.exists(docx_path):
            return jsonify({'success': False, 'error': 'DOCX файл не найден в хранилище'}), 404
        
        document_uuid = document.get('uuid', '')
        if not document_uuid:
            document_uuid = str(uuid.uuid4())
        pdf_output_path = os.path.join(
            app.config['UPLOAD_FOLDER'], 
            f"{document_uuid}.pdf"
        )
        
        converted_pdf = convert_docx_to_pdf_from_docx(docx_path, document, pdf_output_path, app=app)
        
        if not converted_pdf:
            error_detail = "Функция конвертации вернула None. Проверьте логи сервера для деталей."
            print(f"[ERROR] {error_detail}")
            return jsonify({'success': False, 'error': error_detail}), 500
        
        print(f"[INFO] Конвертация завершена, путь к PDF: {converted_pdf}")
        
        # Проверяем, существует ли файл (в хранилище или локально)
        file_exists = False
        if storage_manager.use_minio:
            # Для MinIO проверяем через storage_manager
            file_exists = storage_manager.file_exists(converted_pdf)
            print(f"[INFO] Проверка файла в MinIO: {file_exists}")
        else:
            # Для локального хранилища проверяем через os.path.exists
            file_exists = os.path.exists(converted_pdf)
            print(f"[INFO] Проверка локального файла: {file_exists}, путь: {converted_pdf}")
        
        if not file_exists:
            error_detail = f"PDF файл не найден после конвертации: {converted_pdf}"
            print(f"[ERROR] {error_detail}")
            return jsonify({'success': False, 'error': error_detail}), 500
        
        try:
            db_update('documents', {'pdf_path': converted_pdf}, 'id = %s', [doc_id])
        except Exception as db_err:
            print(f"[WARNING] Не удалось обновить путь к PDF в БД: {db_err}")
        
        # Получаем файл из хранилища
        file_data = storage_manager.get_file(converted_pdf)
        if file_data:
            print(f"[OK] PDF получен из хранилища, размер: {len(file_data)} байт")
            return send_file(
                BytesIO(file_data),
                as_attachment=True,
                download_name=f'{document_uuid}.pdf',
                mimetype='application/pdf'
            )
        # Если не получилось из хранилища, пробуем локально
        elif os.path.exists(converted_pdf):
            print(f"[OK] PDF найден локально: {converted_pdf}")
            return send_file(
                converted_pdf,
                as_attachment=True,
                download_name=f'{document_uuid}.pdf',
                mimetype='application/pdf'
            )
        
        error_detail = f"Не удалось получить PDF файл из хранилища или локально: {converted_pdf}"
        print(f"[ERROR] {error_detail}")
        return jsonify({'success': False, 'error': error_detail}), 500
            
    except Exception as e:
        import traceback
        error_msg = f"Ошибка при конвертации: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/verify')
def verify_document():
    """Страница верификации документа"""
    return render_template('verify.html')


@app.route('/verify/<uuid>')
def verify_by_uuid(uuid):
    """Страница верификации документа по UUID (из QR-кода)"""
    try:
        document = db_select('documents', 'uuid = %s', [uuid], fetch_one=True)
        
        if not document:
            return render_template('verify.html', error='Документ не найден')
        
        class DocumentObj:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
            
            def __getitem__(self, key):
                return getattr(self, key, None)
        
        doc_obj = DocumentObj(document)
        return render_template('document_view.html', document=doc_obj, now=datetime.now)
    except Exception as e:
        return render_template('verify.html', error=f'Ошибка: {str(e)}')


@app.route('/verify-pin', methods=['POST'])
def verify_pin():
    """Проверка PIN-кода и возврат документа"""
    try:
        data = request.get_json()
        pin_code = data.get('pin_code')
        
        if not pin_code:
            return jsonify({'success': False, 'error': 'PIN-код не указан'}), 400
        
        document = db_select('documents', 'pin_code = %s', [pin_code], fetch_one=True)
        
        if not document:
            return jsonify({'success': False, 'error': 'Документ не найден'}), 404
        
        # Форматируем дату
        issue_date = document.get('issue_date')
        if issue_date:
            if isinstance(issue_date, str):
                try:
                    dt = datetime.fromisoformat(issue_date.replace('Z', '+00:00'))
                    issue_date_str = dt.strftime("%d.%m.%Y %H:%M")
                except:
                    try:
                        dt = datetime.strptime(issue_date[:16], "%Y-%m-%dT%H:%M")
                        issue_date_str = dt.strftime("%d.%m.%Y %H:%M")
                    except:
                        issue_date_str = issue_date[:10] if len(issue_date) >= 10 else issue_date
            else:
                issue_date_str = issue_date.strftime("%d.%m.%Y %H:%M")
        else:
            issue_date_str = ''
        
        # Форматируем даты освобождения
        days_off_from = document.get('days_off_from')
        days_off_to = document.get('days_off_to')
        days_off_str = ''
        if days_off_from and days_off_to:
            try:
                from_dt = datetime.fromisoformat(days_off_from.replace('Z', '+00:00')) if isinstance(days_off_from, str) else days_off_from
                to_dt = datetime.fromisoformat(days_off_to.replace('Z', '+00:00')) if isinstance(days_off_to, str) else days_off_to
                days_off_str = f"{from_dt.strftime('%d.%m.%Y')} - {to_dt.strftime('%d.%m.%Y')}"
            except:
                days_off_str = f"{days_off_from} - {days_off_to}"
        elif days_off_from:
            try:
                from_dt = datetime.fromisoformat(days_off_from.replace('Z', '+00:00')) if isinstance(days_off_from, str) else days_off_from
                days_off_str = from_dt.strftime('%d.%m.%Y')
            except:
                days_off_str = str(days_off_from)
        
        return jsonify({
            'success': True,
            'document': {
                'id': document.get('id'),
                'doc_number': document.get('doc_number'),
                'patient_name': document.get('patient_name'),
                'gender': document.get('gender'),
                'age': document.get('age'),
                'jshshir': document.get('jshshir'),
                'address': document.get('address'),
                'attached_medical_institution': document.get('attached_medical_institution'),
                'diagnosis': document.get('diagnosis'),
                'diagnosis_icd10_code': document.get('diagnosis_icd10_code'),
                'final_diagnosis': document.get('final_diagnosis'),
                'final_diagnosis_icd10_code': document.get('final_diagnosis_icd10_code'),
                'organization': document.get('organization'),
                'issue_date': issue_date_str,
                'doctor_name': document.get('doctor_name'),
                'doctor_position': document.get('doctor_position'),
                'department_head_name': document.get('department_head_name'),
                'days_off_period': days_off_str,
                'uuid': document.get('uuid', ''),
                'pdf_url': url_for('download_document', doc_id=document.get('id'), _external=True),
                'pdf_url_by_uuid': url_for('download_by_uuid', uuid=document.get('uuid', ''), _external=True) if document.get('uuid') else None
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/document/<int:doc_id>')
def view_document(doc_id):
    """Просмотр документа по ID"""
    try:
        document = db_select('documents', 'id = %s', [doc_id], fetch_one=True)
        
        if not document:
            return "Документ не найден", 404
        
        class DocumentObj:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
            
            def __getitem__(self, key):
                return getattr(self, key, None)
        
        doc_obj = DocumentObj(document)
        return render_template('document_view.html', document=doc_obj, now=datetime.now)
    except Exception as e:
        return f"Ошибка: {str(e)}", 500


@app.route('/document/<string:doc_number>')
def view_document_by_number(doc_number):
    """Просмотр документа по номеру"""
    try:
        document = db_select('documents', 'doc_number = %s', [doc_number], fetch_one=True)
        
        if not document:
            return "Документ не найден", 404
        
        class DocumentObj:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
            
            def __getitem__(self, key):
                return getattr(self, key, None)
        
        doc_obj = DocumentObj(document)
        return render_template('document_view.html', document=doc_obj, now=datetime.now)
    except Exception as e:
        return f"Ошибка: {str(e)}", 500


@app.route('/files')
def files_history():
    """Страница истории файлов"""
    return render_template('files_history.html')


@app.route('/api/files', methods=['GET'])
def list_files():
    """Получение списка всех файлов в хранилище с информацией из БД"""
    try:
        prefix = request.args.get('prefix', '')
        file_type = request.args.get('type', '')
        
        search_prefix = prefix
        
        files = storage_manager.list_files(prefix=search_prefix, recursive=True)
        
        if file_type:
            extension = f'.{file_type.lower()}'
            files = [f for f in files if f['name'].lower().endswith(extension)]
        
        enriched_files = []
        for file_info in files:
            filename = file_info['name']
            uuid_from_filename = filename.replace('.pdf', '').replace('.docx', '')
            
            document = None
            try:
                document = db_select('documents', 'uuid = %s', [uuid_from_filename], fetch_one=True)
            except:
                pass
            
            enriched_file = {
                **file_info,
                'patient_name': document.get('patient_name') if document else None,
                'doc_number': document.get('doc_number') if document else None,
                'issue_date': document.get('issue_date').isoformat() if document and document.get('issue_date') else None,
            }
            
            enriched_files.append(enriched_file)
        
        for file_info in enriched_files:
            if isinstance(file_info.get('last_modified'), datetime):
                file_info['last_modified'] = file_info['last_modified'].isoformat()
        
        return jsonify({
            'success': True,
            'count': len(enriched_files),
            'files': enriched_files,
            'storage_type': 'minio' if storage_manager.use_minio else 'local'
        })
    except Exception as e:
        import traceback
        print(f"Ошибка при получении списка файлов: {e}")
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/files/download/<path:filename>', methods=['GET'])
def download_file_by_name(filename):
    """Скачивание файла по имени из хранилища"""
    try:
        file_data = storage_manager.get_file(filename)
        
        if not file_data:
            return jsonify({'success': False, 'error': 'Файл не найден'}), 404
        
        content_type = 'application/octet-stream'
        if filename.lower().endswith('.pdf'):
            content_type = 'application/pdf'
        elif filename.lower().endswith('.docx'):
            content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        elif filename.lower().endswith('.doc'):
            content_type = 'application/msword'
        
        return send_file(
            BytesIO(file_data),
            as_attachment=True,
            download_name=filename,
            mimetype=content_type
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/files/delete/<path:filename>', methods=['DELETE'])
def delete_file_by_name(filename):
    """Удаление файла по имени из хранилища"""
    try:
        success = storage_manager.delete_file(filename)
        
        if success:
            return jsonify({'success': True, 'message': f'Файл {filename} успешно удален'})
        else:
            return jsonify({'success': False, 'error': 'Файл не найден или не удалось удалить'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True, host='0.0.0.0', port=5000)
