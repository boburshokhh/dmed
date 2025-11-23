"""Подготовка данных для замены плейсхолдеров в DOCX"""
from datetime import datetime


def prepare_replacements(document_data):
    """Подготавливает словарь замены плейсхолдеров из данных документа"""
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
    
    return replacements

