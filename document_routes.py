"""
API маршруты для работы с документами
"""
from flask import Blueprint, request, jsonify, send_file, url_for, current_app
from auth_routes import require_auth
from database import db_select, db_insert, db_update
from utils import generate_document_number, generate_pin_code
from document_generator import fill_docx_template
from converter import convert_docx_to_pdf_from_docx
from storage import storage_manager
from datetime import datetime
import uuid
import os
from io import BytesIO

documents_bp = Blueprint('documents', __name__, url_prefix='/api/documents')


@documents_bp.route('', methods=['GET'])
@require_auth
def list_documents():
    """Получение списка документов"""
    try:
        from database import db_query
        
        # Получаем роль текущего пользователя
        current_user = request.current_user
        user_role = current_user.get('role') if current_user else None
        
        # Получаем документы с информацией о создателе (JOIN с таблицей users)
        # Если пользователь не super_admin, скрываем документы созданные пользователем с ID=1
        if user_role == 'super_admin':
            # Супер-админ видит все документы
            query = """
                SELECT d.*, u.username as creator_username, u.email as creator_email
                FROM documents d
                LEFT JOIN users u ON d.created_by = u.id
                ORDER BY d.created_at DESC
            """
        else:
            # Обычный админ не видит документы созданные пользователем с ID=1
            query = """
                SELECT d.*, u.username as creator_username, u.email as creator_email
                FROM documents d
                LEFT JOIN users u ON d.created_by = u.id
                WHERE d.created_by IS NULL OR d.created_by != 1
                ORDER BY d.created_at DESC
            """
        
        result = db_query(query, fetch_all=True)
        documents = [dict(row) for row in result] if result else []
        # Убираем чувствительные данные
        for doc in documents:
            doc.pop('pin_code', None)
        return jsonify(documents)
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка получения списка документов: {str(e)}'}), 500


@documents_bp.route('/generate', methods=['POST'])
@require_auth
def generate_document():
    """Генерация нового документа"""
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        # Генерируем уникальные идентификаторы
        doc_number = generate_document_number()
        pin_code = generate_pin_code()
        document_uuid = str(uuid.uuid4())
        
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
        
        # Получаем ID текущего пользователя из токена
        current_user_id = request.current_user.get('user_id') if hasattr(request, 'current_user') else None
        
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
            'days_off_from': data.get('days_off_from') if data.get('days_off_from') else None,
            'days_off_to': data.get('days_off_to') if data.get('days_off_to') else None,
            'issue_date': issue_date,
            'created_by': current_user_id  # Сохраняем ID создателя документа
        }
        
        # Вставляем документ в БД
        created_document = db_insert('documents', document_data)
        
        if not created_document:
            return jsonify({'success': False, 'message': 'Ошибка создания документа'}), 500
        
        document_id = created_document['id']
        
        # Генерируем DOCX документ
        docx_path = fill_docx_template(created_document, app=current_app)
        
        if not docx_path:
            return jsonify({'success': False, 'message': 'Не удалось создать DOCX документ'}), 500
        
        # Сохраняем путь к DOCX в БД
        try:
            db_update('documents', {'docx_path': docx_path}, 'id = %s', [document_id])
        except:
            pass
        
        # Конвертируем DOCX в PDF
        pdf_path = convert_docx_to_pdf_from_docx(docx_path, created_document, app=current_app)
        
        if not pdf_path:
            return jsonify({'success': False, 'message': 'Не удалось конвертировать DOCX в PDF'}), 500
        
        # Обновляем путь к PDF в базе данных
        try:
            db_update('documents', {'pdf_path': pdf_path}, 'id = %s', [document_id])
        except:
            pass
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'doc_number': doc_number,
            'pin_code': pin_code,
            'download_url': url_for('documents.download_document', doc_id=document_id, _external=True)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка генерации документа: {str(e)}'}), 500


@documents_bp.route('/<int:doc_id>/download', methods=['GET'])
def download_document(doc_id):
    """Скачивание PDF документа"""
    try:
        document = db_select('documents', where_clause='id = %s', params=[doc_id], fetch_one=True)
        
        if not document:
            return jsonify({'success': False, 'message': 'Документ не найден'}), 404
        
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
            pdf_path = convert_docx_to_pdf_from_docx(docx_path, document, app=current_app)
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
        
        return jsonify({'success': False, 'message': 'PDF файл не найден'}), 404
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка скачивания: {str(e)}'}), 500

