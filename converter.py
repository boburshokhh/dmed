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
    # На Windows LibreOffice обычно находится в Program Files
    # Проверяем все возможные пути установки
    possible_paths = [
        r'C:\Program Files\LibreOffice\program\soffice.exe',
        r'C:\Program Files (x86)\LibreOffice\program\soffice.exe',
        os.path.join(os.environ.get('ProgramFiles', ''), 'LibreOffice', 'program', 'soffice.exe'),
        os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'LibreOffice', 'program', 'soffice.exe'),
    ]
    
    # Добавляем пути из переменных окружения
    if 'LOCALAPPDATA' in os.environ:
        possible_paths.append(os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs', 'LibreOffice', 'program', 'soffice.exe'))
    if 'APPDATA' in os.environ:
        possible_paths.append(os.path.join(os.environ.get('APPDATA', ''), 'Programs', 'LibreOffice', 'program', 'soffice.exe'))
    
    # Проверяем также в корне диска C:
    possible_paths.extend([
        r'C:\LibreOffice\program\soffice.exe',
        r'D:\LibreOffice\program\soffice.exe',
    ])
    
    # Также проверяем PATH
    libreoffice_found = False
    for path in possible_paths:
        if path and os.path.exists(path):
            LIBREOFFICE_CMD = path
            libreoffice_found = True
            print(f"[INFO] LibreOffice найден по пути: {path}")
            break
    
    # Если не нашли по путям, пробуем через PATH (проверяем только наличие команды, без запуска)
    if not libreoffice_found:
        try:
            # Просто проверяем, есть ли команда в PATH, без запуска
            import shutil
            soffice_path = shutil.which('soffice')
            if soffice_path:
                LIBREOFFICE_CMD = 'soffice'
                libreoffice_found = True
                print(f"[INFO] LibreOffice найден в PATH: {soffice_path}")
        except:
            pass
    
    if libreoffice_found:
        # Проверяем, что файл существует и доступен
        # Не проверяем версию при старте, так как это может быть медленно
        # Вместо этого просто проверяем существование файла или наличие в PATH
        if LIBREOFFICE_CMD == 'soffice':
            # Если команда найдена через PATH, считаем её доступной
            LIBREOFFICE_AVAILABLE = True
            print(f"[INFO] LibreOffice найден и доступен через PATH: {LIBREOFFICE_CMD}")
        elif os.path.exists(LIBREOFFICE_CMD) and os.path.isfile(LIBREOFFICE_CMD):
            LIBREOFFICE_AVAILABLE = True
            print(f"[INFO] LibreOffice найден и доступен: {LIBREOFFICE_CMD}")
        else:
            LIBREOFFICE_ERROR = f"LibreOffice найден по пути, но файл недоступен: {LIBREOFFICE_CMD}"
    else:
        LIBREOFFICE_ERROR = "LibreOffice не найден. Установите LibreOffice с https://www.libreoffice.org/download/"
        print(f"[WARNING] {LIBREOFFICE_ERROR}")
        print("[INFO] Рекомендуемые пути установки на Windows:")
        print("  - C:\\Program Files\\LibreOffice\\program\\soffice.exe")
        print("  - C:\\Program Files (x86)\\LibreOffice\\program\\soffice.exe")
else:
    # На Linux/Mac используем стандартную команду
    # Проверяем только наличие команды в PATH, без запуска
    try:
        import shutil
        libreoffice_path = shutil.which('libreoffice')
        if libreoffice_path:
            LIBREOFFICE_AVAILABLE = True
            LIBREOFFICE_CMD = 'libreoffice'
            print(f"[INFO] LibreOffice найден в PATH: {libreoffice_path}")
        else:
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
        
        # Используем LibreOffice для конвертации (единственный метод)
        if LIBREOFFICE_AVAILABLE and LIBREOFFICE_CMD:
            try:
                print(f"[INFO] Используем LibreOffice для конвертации...")
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                
                # Подготавливаем директорию для выхода
                temp_output_dir = tempfile.mkdtemp()
                # Нормализуем путь к выходной директории
                temp_output_dir = os.path.normpath(os.path.abspath(temp_output_dir))
                print(f"[INFO] Выходная директория для PDF: {temp_output_dir}")
                
                # Преобразуем путь к DOCX в абсолютный путь
                # LibreOffice требует абсолютный путь к файлу
                docx_abs_path = os.path.abspath(docx_path)
                
                # Нормализуем путь (убираем двойные слеши, точки и т.д.)
                docx_abs_path = os.path.normpath(docx_abs_path)
                
                # Проверяем, что файл существует и не пустой
                if not os.path.exists(docx_abs_path):
                    raise Exception(f"DOCX файл не найден: {docx_abs_path}")
                
                file_size = os.path.getsize(docx_abs_path)
                if file_size == 0:
                    raise Exception(f"DOCX файл пустой: {docx_abs_path}")
                
                print(f"[INFO] DOCX файл для конвертации: {docx_abs_path}, размер: {file_size} байт")
                
                # На Windows LibreOffice может требовать путь с прямыми слешами или в формате file://
                # Используем абсолютный путь как есть (Windows обычно принимает оба формата)
                docx_path_for_cmd = docx_abs_path
                
                # Команда для конвертации
                cmd = [
                    LIBREOFFICE_CMD,
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', temp_output_dir,
                    docx_path_for_cmd
                ]
                
                print(f"[INFO] Выполняем команду: {' '.join(cmd)}")
                
                # На Windows может быть проблема с блокировкой, если LibreOffice уже запущен
                # Также используем альтернативную конфигурацию, чтобы обойти повреждённый bootstrap.ini
                if sys.platform == 'win32':
                    # Создаём временную директорию для конфигурации LibreOffice
                    # Это обходит проблему с повреждённым bootstrap.ini
                    temp_config_dir = tempfile.mkdtemp(prefix='LibreOffice_Config_')
                    # Конвертируем путь в формат file:// для Windows
                    config_path = os.path.abspath(temp_config_dir).replace('\\', '/')
                    if not config_path.startswith('/'):
                        config_path = '/' + config_path
                    cmd.extend(['-env:UserInstallation=file://' + config_path])
                    print(f"[INFO] Используем альтернативную конфигурацию LibreOffice: {temp_config_dir}")
                else:
                    temp_config_dir = None
                
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                    
                    # Проверяем stderr на наличие ошибок
                    if result.stderr:
                        stderr_lower = result.stderr.lower()
                        if 'bootstrap.ini' in stderr_lower and ('повреждён' in stderr_lower or 'damaged' in stderr_lower or 'corrupted' in stderr_lower):
                            error_msg = "Файл конфигурации LibreOffice повреждён. Попробуйте переустановить LibreOffice или удалить папку конфигурации."
                            print(f"[ERROR] {error_msg}")
                            print(f"[ERROR] Детали: {result.stderr[:500]}")
                            print(f"[SOLUTION] Удалите папку конфигурации: %APPDATA%\\LibreOffice")
                            raise Exception(error_msg)
                        elif 'document is empty' in stderr_lower or 'source file could not be loaded' in stderr_lower:
                            error_msg = f"LibreOffice не может загрузить файл. Проверьте путь и целостность файла: {docx_abs_path}"
                            print(f"[ERROR] {error_msg}")
                            print(f"[ERROR] Детали: {result.stderr[:500]}")
                            print(f"[INFO] Размер файла: {file_size} байт, существует: {os.path.exists(docx_abs_path)}")
                            raise Exception(error_msg)
                        elif result.returncode != 0:
                            # Другие ошибки в stderr
                            print(f"[WARNING] LibreOffice stderr: {result.stderr[:500]}")
                    
                except subprocess.TimeoutExpired:
                    error_msg = "LibreOffice превысил время ожидания (120 секунд). Возможно, процесс заблокирован."
                    print(f"[ERROR] {error_msg}")
                    # Пробуем убить возможные зависшие процессы LibreOffice
                    if sys.platform == 'win32':
                        try:
                            subprocess.run(['taskkill', '/F', '/IM', 'soffice.exe'], 
                                         capture_output=True, timeout=5)
                            print("[INFO] Попытка завершить зависшие процессы LibreOffice")
                        except:
                            pass
                    raise Exception(error_msg)
                except Exception as run_error:
                    # Проверяем, не связана ли ошибка с повреждённым конфигом
                    error_str = str(run_error).lower()
                    if 'bootstrap.ini' in error_str or 'повреждён' in error_str or 'damaged' in error_str:
                        error_msg = "Файл конфигурации LibreOffice повреждён. Переустановите LibreOffice."
                        print(f"[ERROR] {error_msg}")
                        raise Exception(error_msg)
                    raise
                
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
                        # Очищаем временную конфигурацию LibreOffice, если использовалась
                        if sys.platform == 'win32' and 'temp_config_dir' in locals() and temp_config_dir and os.path.exists(temp_config_dir):
                            try:
                                shutil.rmtree(temp_config_dir)
                                print(f"[INFO] Временная конфигурация LibreOffice удалена: {temp_config_dir}")
                            except Exception as cleanup_error:
                                print(f"[WARNING] Не удалось удалить временную конфигурацию: {cleanup_error}")
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
                    # Очищаем временные файлы
                    try:
                        import shutil
                        shutil.rmtree(temp_output_dir)
                        if sys.platform == 'win32' and 'temp_config_dir' in locals() and temp_config_dir and os.path.exists(temp_config_dir):
                            shutil.rmtree(temp_config_dir)
                    except:
                        pass
            except subprocess.TimeoutExpired:
                print(f"[ERROR] LibreOffice timeout (>120 сек)")
                error_msg = "LibreOffice превысил время ожидания (120 секунд)"
                # Очищаем временные файлы
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
                # Очищаем временные файлы
                try:
                    import shutil
                    if 'temp_output_dir' in locals():
                        shutil.rmtree(temp_output_dir)
                    if sys.platform == 'win32' and 'temp_config_dir' in locals() and temp_config_dir and os.path.exists(temp_config_dir):
                        shutil.rmtree(temp_config_dir)
                except:
                    pass
        
        # Если LibreOffice не сработал или недоступен
        if not (LIBREOFFICE_AVAILABLE and LIBREOFFICE_CMD):
            error_msg = f"LibreOffice недоступен. {LIBREOFFICE_ERROR if LIBREOFFICE_ERROR else 'Не установлен'}"
            print(f"[ERROR] {error_msg}")
            
            # Предлагаем решение
            print("[SOLUTION] Решение проблем с LibreOffice:")
            if sys.platform == 'win32':
                print("  1. Если файл конфигурации повреждён:")
                print("     - Закройте все процессы LibreOffice")
                print("     - Удалите папку: %APPDATA%\\LibreOffice")
                print("     - Или переустановите LibreOffice с https://www.libreoffice.org/download/")
                print("  2. Если LibreOffice не установлен:")
                print("     - Скачайте с https://www.libreoffice.org/download/")
                print("     - Установите в стандартную директорию")
                print("     - Путь должен быть: C:\\Program Files\\LibreOffice\\program\\soffice.exe")
                print("     - После установки перезапустите приложение")
            else:
                print("  1. Установите LibreOffice:")
                print("     sudo apt-get install -y libreoffice libreoffice-writer")
                print("  2. Если конфигурация повреждена:")
                print("     rm -rf ~/.config/libreoffice")
        
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
