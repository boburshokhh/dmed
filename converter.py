"""Конвертация DOCX в PDF"""
import os
import sys
import uuid
import base64
import subprocess
import tempfile
import warnings
from contextlib import redirect_stderr
from io import StringIO
from storage import storage_manager

# Подавление предупреждений GLib-GIO (только для Linux, где используется WeasyPrint)
if sys.platform != 'win32':
    # Устанавливаем переменные окружения для подавления предупреждений GLib
    os.environ['GIO_USE_VFS'] = 'local'
    os.environ['G_MESSAGES_DEBUG'] = ''
    # Подавляем предупреждения GLib через warnings
    warnings.filterwarnings('ignore', category=UserWarning, module='gi')
    warnings.filterwarnings('ignore', message='.*GLib-GIO.*')

# Попытка импортировать docx2pdf
DOCX2PDF_AVAILABLE = False
DOCX2PDF_ERROR = None
PYWIN32_AVAILABLE = False
if sys.platform == 'win32':
    # Проверяем наличие pywin32 (необходим для docx2pdf на Windows)
    try:
        import pythoncom
        PYWIN32_AVAILABLE = True
    except ImportError:
        PYWIN32_AVAILABLE = False
        print("[WARNING] pywin32 не установлен. Для работы docx2pdf на Windows установите: pip install pywin32")

try:
    from docx2pdf import convert
    if sys.platform == 'win32' and not PYWIN32_AVAILABLE:
        DOCX2PDF_AVAILABLE = False
        DOCX2PDF_ERROR = "pywin32 не установлен. Установите: pip install pywin32"
        print(f"[WARNING] docx2pdf требует pywin32 на Windows: {DOCX2PDF_ERROR}")
    else:
        DOCX2PDF_AVAILABLE = True
except ImportError as e:
    DOCX2PDF_ERROR = str(e)
    print(f"[WARNING] docx2pdf не доступен: {e}")
except Exception as e:
    DOCX2PDF_ERROR = str(e)
    print(f"[WARNING] Ошибка при импорте docx2pdf: {e}")

# Попытка импортировать mammoth и weasyprint (только для Linux, на Windows не используется)
MAMMOTH_AVAILABLE = False
MAMMOTH_ERROR = None
WEASYPRINT_AVAILABLE = False
WEASYPRINT_ERROR = None

if sys.platform != 'win32':
    # На Linux используем WeasyPrint как fallback
    try:
        import mammoth
        MAMMOTH_AVAILABLE = True
    except ImportError as e:
        MAMMOTH_ERROR = str(e)
        print(f"[WARNING] mammoth не доступен: {e}")
    except Exception as e:
        MAMMOTH_ERROR = str(e)
        print(f"[WARNING] Ошибка при импорте mammoth: {e}")

    try:
        from weasyprint import HTML
        WEASYPRINT_AVAILABLE = True
        # Проверяем, что weasyprint действительно работает
        try:
            import tempfile
            test_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            test_file.close()
            # Подавляем предупреждения GLib-GIO при тестировании
            with redirect_stderr(StringIO()):
                HTML(string="<html><body>Test</body></html>").write_pdf(test_file.name)
            if os.path.exists(test_file.name):
                os.remove(test_file.name)
        except Exception as test_error:
            WEASYPRINT_AVAILABLE = False
            WEASYPRINT_ERROR = f"weasyprint импортирован, но не работает: {test_error}"
            print(f"[WARNING] {WEASYPRINT_ERROR}")
    except ImportError as e:
        WEASYPRINT_ERROR = f"weasyprint не установлен: {e}"
        print(f"[WARNING] {WEASYPRINT_ERROR}")
    except OSError as e:
        WEASYPRINT_ERROR = f"weasyprint требует системные библиотеки: {e}"
        print(f"[WARNING] {WEASYPRINT_ERROR}")
    except Exception as e:
        WEASYPRINT_ERROR = f"Ошибка при импорте weasyprint: {e}"
        print(f"[WARNING] {WEASYPRINT_ERROR}")

# Проверка доступности LibreOffice
LIBREOFFICE_AVAILABLE = False
LIBREOFFICE_ERROR = None
try:
    result = subprocess.run(['libreoffice', '--version'], capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        LIBREOFFICE_AVAILABLE = True
        version = result.stdout.strip()
        print(f"[INFO] LibreOffice найден: {version}")
    else:
        LIBREOFFICE_ERROR = f"libreoffice вернул код {result.returncode}"
except FileNotFoundError:
    LIBREOFFICE_ERROR = "libreoffice не установлен. Установите: sudo apt-get install libreoffice libreoffice-writer"
    print(f"[WARNING] {LIBREOFFICE_ERROR}")
except Exception as e:
    LIBREOFFICE_ERROR = f"Ошибка при проверке LibreOffice: {e}"
    print(f"[WARNING] {LIBREOFFICE_ERROR}")


def convert_docx_to_pdf_from_docx(docx_path, document_data, output_path=None, app=None):
    """Конвертирует DOCX файл в PDF"""
    print(f"[INFO] Начало конвертации DOCX->PDF. docx_path={docx_path}")
    
    docx_data = None
    temp_docx_path = None
    
    if docx_path:
        print(f"[INFO] Пытаемся получить DOCX из хранилища: {docx_path}")
        docx_data = storage_manager.get_file(docx_path)
        if docx_data:
            print(f"[INFO] DOCX получен из хранилища, размер: {len(docx_data)} байт")
            upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads/documents') if app else 'uploads/documents'
            temp_docx_path = os.path.join(upload_folder, f'temp_{uuid.uuid4()}.docx')
            os.makedirs(upload_folder, exist_ok=True)
            with open(temp_docx_path, 'wb') as f:
                f.write(docx_data)
            docx_path = temp_docx_path
            print(f"[INFO] DOCX сохранен во временный файл: {temp_docx_path}")
        elif os.path.exists(docx_path):
            print(f"[INFO] DOCX найден локально: {docx_path}")
        else:
            print(f"[ERROR] DOCX не найден ни в хранилище, ни локально: {docx_path}")
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
        
        # Метод 1: docx2pdf (лучший для Windows, приоритет на Windows)
        if sys.platform == 'win32' and DOCX2PDF_AVAILABLE:
            try:
                print(f"[INFO] Используем docx2pdf для конвертации (Windows)...")
                if sys.platform == 'win32':
                    try:
                        import pythoncom
                        try:
                            pythoncom.CoInitialize()
                        except pythoncom.com_error:
                            pass
                    except ImportError:
                        print("[WARNING] pywin32 не установлен")
                
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                convert(docx_path, output_path)
                
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"[OK] DOCX успешно конвертирован в PDF через docx2pdf: {output_path}, размер: {file_size} байт")
                    with open(output_path, 'rb') as f:
                        pdf_data = f.read()
                    
                    pdf_filename = os.path.basename(output_path)
                    stored_path = storage_manager.save_file(pdf_data, pdf_filename, 'application/pdf')
                    
                    if storage_manager.use_minio and os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except:
                            pass
                    
                    if temp_docx_path and os.path.exists(temp_docx_path):
                        try:
                            os.remove(temp_docx_path)
                        except:
                            pass
                    
                    return stored_path
                else:
                    raise Exception(f"PDF файл не был создан: {output_path}")
            except Exception as e:
                error_msg = f"Ошибка при конвертации через docx2pdf: {e}"
                print(f"[ERROR] {error_msg}")
                import traceback
                print(traceback.format_exc())
                print("Пробуем альтернативный метод...")
        
        # Метод 2: LibreOffice (лучший для Linux)
        if LIBREOFFICE_AVAILABLE:
            try:
                print(f"[INFO] Используем LibreOffice для конвертации...")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Подготавливаем директорию для выхода
                temp_output_dir = tempfile.mkdtemp()
                
                # Команда для конвертации
                cmd = [
                    'libreoffice',
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', temp_output_dir,
                    docx_path
                ]
                
                print(f"[INFO] Выполняем команду: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                
                # Получаем имя файла PDF
                pdf_basename = os.path.splitext(os.path.basename(docx_path))[0] + '.pdf'
                temp_pdf_path = os.path.join(temp_output_dir, pdf_basename)
                
                if result.returncode == 0 and os.path.exists(temp_pdf_path):
                    # Копируем PDF на место
                    with open(temp_pdf_path, 'rb') as f:
                        pdf_data = f.read()
                    
                    # Сохраняем в хранилище
                    pdf_filename = os.path.basename(output_path)
                    stored_path = storage_manager.save_file(pdf_data, pdf_filename, 'application/pdf')
                    
                    file_size = len(pdf_data)
                    print(f"[OK] DOCX успешно конвертирован в PDF через LibreOffice: {stored_path}, размер: {file_size} байт")
                    
                    # Очищаем временные файлы
                    try:
                        import shutil
                        shutil.rmtree(temp_output_dir)
                    except:
                        pass
                    
                    if temp_docx_path and os.path.exists(temp_docx_path):
                        try:
                            os.remove(temp_docx_path)
                        except:
                            pass
                    
                    return stored_path
                else:
                    error_msg = f"LibreOffice вернул код {result.returncode}. stderr: {result.stderr}"
                    print(f"[ERROR] {error_msg}")
                    # Очищаем временную директорию
                    try:
                        import shutil
                        shutil.rmtree(temp_output_dir)
                    except:
                        pass
                    print("Пробуем альтернативный метод...")
            except subprocess.TimeoutExpired:
                print(f"[ERROR] LibreOffice timeout (>60 сек). Пробуем альтернативный метод...")
            except Exception as e:
                error_msg = f"Ошибка при конвертации через LibreOffice: {e}"
                print(f"[ERROR] {error_msg}")
                import traceback
                print(traceback.format_exc())
                print("Пробуем альтернативный метод...")
        
        # Метод 2: mammoth + weasyprint (только для Linux, на Windows не используется)
        if sys.platform != 'win32' and MAMMOTH_AVAILABLE and WEASYPRINT_AVAILABLE:
            try:
                print(f"[INFO] Используем метод mammoth+weasyprint для конвертации...")
                def convert_image(image):
                    """Конвертирует изображения из DOCX в base64"""
                    with image.open() as image_bytes:
                        image_base64 = base64.b64encode(image_bytes.read()).decode("utf-8")
                        return {"src": f"data:{image.content_type};base64,{image_base64}"}
                
                with open(docx_path, "rb") as docx_file:
                    result = mammoth.convert_to_html(
                        docx_file,
                        convert_image=mammoth.images.img_element(convert_image)
                    )
                    html_content = result.value
                    if result.messages:
                        print(f"[WARNING] Предупреждения mammoth: {result.messages}")
                
                html_with_styles = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        @page {{
                            size: A4;
                            margin: 1.5cm;
                        }}
                        body {{
                            font-family: 'Times New Roman', serif;
                            font-size: 11pt;
                            line-height: 1.4;
                            color: #000;
                        }}
                        p {{
                            margin: 0.5em 0;
                        }}
                        table {{
                            border-collapse: collapse;
                            width: 100%;
                            margin: 1em 0;
                        }}
                        table td, table th {{
                            border: 1px solid #ddd;
                            padding: 8px;
                        }}
                        table th {{
                            background-color: #f2f2f2;
                            font-weight: bold;
                        }}
                        img {{
                            max-width: 100%;
                            height: auto;
                        }}
                        h1, h2, h3, h4, h5, h6 {{
                            margin: 1em 0 0.5em 0;
                            font-weight: bold;
                        }}
                    </style>
                </head>
                <body>
                    {html_content}
                </body>
                </html>
                """
                
                print(f"[INFO] Конвертируем HTML в PDF через weasyprint...")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                # Подавляем предупреждения GLib-GIO
                stderr_buffer = StringIO()
                with redirect_stderr(stderr_buffer):
                    HTML(string=html_with_styles).write_pdf(output_path)
                # Проверяем, были ли реальные ошибки (не предупреждения)
                stderr_content = stderr_buffer.getvalue()
                if stderr_content and 'error' in stderr_content.lower() and 'GLib-GIO-WARNING' not in stderr_content:
                    print(f"[WARNING] WeasyPrint stderr: {stderr_content[:200]}")
                
                if os.path.exists(output_path):
                    file_size = os.path.getsize(output_path)
                    print(f"[OK] DOCX успешно конвертирован в PDF через mammoth+weasyprint: {output_path}, размер: {file_size} байт")
                    with open(output_path, 'rb') as f:
                        pdf_data = f.read()
                    
                    pdf_filename = os.path.basename(output_path)
                    stored_path = storage_manager.save_file(pdf_data, pdf_filename, 'application/pdf')
                    
                    if storage_manager.use_minio and os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except:
                            pass
                    
                    if temp_docx_path and os.path.exists(temp_docx_path):
                        try:
                            os.remove(temp_docx_path)
                        except:
                            pass
                    
                    return stored_path
                else:
                    raise Exception(f"PDF файл не был создан: {output_path}")
            except Exception as e:
                error_msg = f"Ошибка при конвертации через mammoth+weasyprint: {e}"
                print(f"[ERROR] {error_msg}")
                import traceback
                print(traceback.format_exc())
                print("Используем альтернативный метод...")
        
        # Если ни один метод не сработал
        error_details = []
        error_details.append(f"LIBREOFFICE_AVAILABLE={LIBREOFFICE_AVAILABLE}")
        if LIBREOFFICE_ERROR:
            error_details.append(f"LIBREOFFICE_ERROR={LIBREOFFICE_ERROR}")
        error_details.append(f"MAMMOTH_AVAILABLE={MAMMOTH_AVAILABLE}")
        if MAMMOTH_ERROR:
            error_details.append(f"MAMMOTH_ERROR={MAMMOTH_ERROR}")
        error_details.append(f"WEASYPRINT_AVAILABLE={WEASYPRINT_AVAILABLE}")
        if WEASYPRINT_ERROR:
            error_details.append(f"WEASYPRINT_ERROR={WEASYPRINT_ERROR}")
        error_details.append(f"DOCX2PDF_AVAILABLE={DOCX2PDF_AVAILABLE}")
        if DOCX2PDF_ERROR:
            error_details.append(f"DOCX2PDF_ERROR={DOCX2PDF_ERROR}")
        error_details.append(f"OS={sys.platform}")
        
        error_msg = "Все методы конвертации DOCX->PDF не удались. Детали:\n" + "\n".join(error_details)
        print(f"[ERROR] {error_msg}")
        
        # Предлагаем решение
        if sys.platform == 'win32':
            if not DOCX2PDF_AVAILABLE:
                print("[SOLUTION] Для Windows установите docx2pdf и pywin32:")
                print("  pip install docx2pdf pywin32")
                if DOCX2PDF_ERROR:
                    print(f"  Ошибка: {DOCX2PDF_ERROR}")
        else:
            if not LIBREOFFICE_AVAILABLE:
                print("[SOLUTION] Для Linux сервера установите LibreOffice:")
                print("  sudo apt-get install -y libreoffice libreoffice-writer")
        
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
