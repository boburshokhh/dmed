"""Конвертация DOCX в PDF через LibreOffice"""
import os
import sys
import uuid
import subprocess
import tempfile
from storage import storage_manager

# Проверка доступности LibreOffice
LIBREOFFICE_AVAILABLE = False
LIBREOFFICE_ERROR = None
LIBREOFFICE_CMD = None

# Определяем команду для запуска LibreOffice в зависимости от ОС
if sys.platform == 'win32':
    possible_paths = [
        r'C:\Program Files\LibreOffice\program\soffice.exe',
        r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
        os.path.join(os.environ.get('ProgramFiles', ''), 'LibreOffice', 'program', 'soffice.exe'),
        os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'LibreOffice', 'program', 'soffice.exe'),
    ]
    
    if 'LOCALAPPDATA' in os.environ:
        possible_paths.append(os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'LibreOffice', 'program', 'soffice.exe'))
    if 'APPDATA' in os.environ:
        possible_paths.append(os.path.join(os.environ.get('APPDATA', ''), 'Programs', 'LibreOffice', 'program', 'soffice.exe'))
    
    possible_paths.extend([
        r'C:\LibreOffice\program\soffice.exe',
        r'D:\LibreOffice\program\soffice.exe',
    ])
    
    libreoffice_found = False
    for path in possible_paths:
        if path and os.path.exists(path):
            LIBREOFFICE_CMD = path
            libreoffice_found = True
            break
    
    if not libreoffice_found:
        try:
            import shutil
            soffice_path = shutil.which('soffice')
            if soffice_path:
                LIBREOFFICE_CMD = 'soffice'
                libreoffice_found = True
        except:
            pass
    
    if libreoffice_found:
        if LIBREOFFICE_CMD == 'soffice':
            LIBREOFFICE_AVAILABLE = True
        elif os.path.exists(LIBREOFFICE_CMD) and os.path.isfile(LIBREOFFICE_CMD):
            LIBREOFFICE_AVAILABLE = True
        else:
            LIBREOFFICE_ERROR = f"LibreOffice найден по пути, но файл недоступен: {LIBREOFFICE_CMD}"
    else:
        LIBREOFFICE_ERROR = "LibreOffice не найден. Установите LibreOffice с https://www.libreoffice.org/download/"
else:
    try:
        import shutil
        libreoffice_path = shutil.which('libreoffice')
        if libreoffice_path:
            LIBREOFFICE_AVAILABLE = True
            LIBREOFFICE_CMD = 'libreoffice'
        else:
            LIBREOFFICE_ERROR = "libreoffice не установлен. Установите: sudo apt-get install libreoffice libreoffice-writer"
    except Exception as e:
        LIBREOFFICE_ERROR = f"Ошибка при проверке LibreOffice: {e}"


def convert_docx_to_pdf_from_docx(docx_path, document_data, output_path=None, app=None):
    """Конвертирует DOCX файл в PDF"""
    docx_data = None
    temp_docx_path = None
    
    if docx_path:
        docx_data = storage_manager.get_file(docx_path)
        if docx_data:
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads/documents') if app else 'uploads/documents'
            temp_docx_path = os.path.join(upload_folder, f'temp_{uuid.uuid4()}.docx')
            os.makedirs(upload_folder, exist_ok=True)
            with open(temp_docx_path, 'wb') as f:
                f.write(docx_data)
            docx_path = temp_docx_path
        elif not os.path.exists(docx_path):
            print(f"[ERROR] DOCX не найден: {docx_path}")
            return None
    
    if not docx_path or not os.path.exists(docx_path):
        print(f"[ERROR] DOCX файл не существует: {docx_path}")
        return None
    
    try:
        if output_path is None:
            document_uuid = document_data.get('uuid', '') if document_data else ''
            if not document_uuid:
                document_uuid = str(uuid.uuid4())
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads/documents') if app else 'uploads/documents'
            output_path = os.path.join(upload_folder, f"{document_uuid}.pdf")
        
        if LIBREOFFICE_AVAILABLE and LIBREOFFICE_CMD:
            try:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                temp_output_dir = tempfile.mkdtemp()
                temp_output_dir = os.path.normpath(os.path.abspath(temp_output_dir))
                
                docx_abs_path = os.path.abspath(docx_path)
                docx_abs_path = os.path.normpath(docx_abs_path)
                
                if not os.path.exists(docx_abs_path):
                    raise Exception(f"DOCX файл не найден: {docx_abs_path}")
                
                file_size = os.path.getsize(docx_abs_path)
                if file_size == 0:
                    raise Exception(f"DOCX файл пустой: {docx_abs_path}")
                
                docx_path_for_cmd = docx_abs_path
                
                cmd = [
                    LIBREOFFICE_CMD,
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', temp_output_dir,
                    docx_path_for_cmd
                ]
                
                if sys.platform == 'win32':
                    temp_config_dir = tempfile.mkdtemp(prefix='LibreOffice_Config_')
                    config_path = os.path.abspath(temp_config_dir).replace('\\', '/')
                    if not config_path.startswith('/'):
                        config_path = '/' + config_path
                    cmd.extend(['-env:UserInstallation=file://' + config_path])
                else:
                    temp_config_dir = None
                
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    
                    if result.stderr:
                        stderr_lower = result.stderr.lower()
                        if 'bootstrap.ini' in stderr_lower and ('повреждён' in stderr_lower or 'damaged' in stderr_lower or 'corrupted' in stderr_lower):
                            error_msg = "Файл конфигурации LibreOffice повреждён."
                            print(f"[ERROR] {error_msg}")
                            raise Exception(error_msg)
                        elif 'document is empty' in stderr_lower or 'source file could not be loaded' in stderr_lower:
                            error_msg = f"LibreOffice не может загрузить файл: {docx_abs_path}"
                            print(f"[ERROR] {error_msg}")
                            raise Exception(error_msg)
                
                except subprocess.TimeoutExpired:
                    error_msg = "LibreOffice превысил время ожидания (120 секунд)."
                    print(f"[ERROR] {error_msg}")
                    if sys.platform == 'win32':
                        try:
                            subprocess.run(['taskkill', '/F', '/IM', 'soffice.exe'], 
                                         capture_output=True, timeout=5)
                        except:
                            pass
                    raise Exception(error_msg)
                except Exception as run_error:
                    error_str = str(run_error).lower()
                    if 'bootstrap.ini' in error_str or 'повреждён' in error_str or 'damaged' in error_str:
                        error_msg = "Файл конфигурации LibreOffice повреждён."
                        print(f"[ERROR] {error_msg}")
                        raise Exception(error_msg)
                    raise
                
                pdf_basename = os.path.splitext(os.path.basename(docx_path))[0] + '.pdf'
                temp_pdf_path = os.path.join(temp_output_dir, pdf_basename)
                
                if result.returncode == 0 and os.path.exists(temp_pdf_path):
                    with open(temp_pdf_path, 'rb') as f:
                        pdf_data = f.read()
                    
                    pdf_filename = os.path.basename(output_path)
                    stored_path = storage_manager.save_file(pdf_data, pdf_filename, 'application/pdf')
                    
                    try:
                        import shutil
                        shutil.rmtree(temp_output_dir)
                        if sys.platform == 'win32' and 'temp_config_dir' in locals() and temp_config_dir and os.path.exists(temp_config_dir):
                            try:
                                shutil.rmtree(temp_config_dir)
                            except:
                                pass
                    except:
                        pass
                    
                    if temp_docx_path and os.path.exists(temp_docx_path):
                        try:
                            os.remove(temp_docx_path)
                        except:
                            pass
                    
                    return stored_path
                else:
                    error_msg = f"LibreOffice вернул код {result.returncode}."
                    print(f"[ERROR] {error_msg}")
                    try:
                        import shutil
                        shutil.rmtree(temp_output_dir)
                        if sys.platform == 'win32' and 'temp_config_dir' in locals() and temp_config_dir and os.path.exists(temp_config_dir):
                            shutil.rmtree(temp_config_dir)
                    except:
                        pass
            except subprocess.TimeoutExpired:
                print(f"[ERROR] LibreOffice timeout (>120 сек)")
                try:
                    import shutil
                    if 'temp_output_dir' in locals():
                        shutil.rmtree(temp_output_dir)
                    if sys.platform == 'win32' and 'temp_config_dir' in locals() and temp_config_dir and os.path.exists(temp_config_dir):
                        shutil.rmtree(temp_config_dir)
                except:
                    pass
            except Exception as e:
                error_msg = f"Ошибка при конвертации через LibreOffice: {e}"
                print(f"[ERROR] {error_msg}")
                import traceback
                print(traceback.format_exc())
                try:
                    import shutil
                    if 'temp_output_dir' in locals():
                        shutil.rmtree(temp_output_dir)
                    if sys.platform == 'win32' and 'temp_config_dir' in locals() and temp_config_dir and os.path.exists(temp_config_dir):
                        shutil.rmtree(temp_config_dir)
                except:
                    pass
        
        if not (LIBREOFFICE_AVAILABLE and LIBREOFFICE_CMD):
            error_msg = f"LibreOffice недоступен. {LIBREOFFICE_ERROR if LIBREOFFICE_ERROR else 'Не установлен'}"
            print(f"[ERROR] {error_msg}")
        
        if temp_docx_path and os.path.exists(temp_docx_path):
            try:
                os.remove(temp_docx_path)
            except:
                pass
        
        return None
        
    except Exception as e:
        print(f"[ERROR] Ошибка при конвертации DOCX в PDF: {e}")
        import traceback
        print(traceback.format_exc())
        if temp_docx_path and os.path.exists(temp_docx_path):
            try:
                os.remove(temp_docx_path)
            except:
                pass
        return None
