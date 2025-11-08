"""Конвертация DOCX в PDF"""
import os
import uuid
import base64
from storage import storage_manager

# Попытка импортировать docx2pdf
try:
    from docx2pdf import convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    DOCX2PDF_AVAILABLE = False
    print("Предупреждение: docx2pdf не доступен. Конвертация DOCX->PDF будет использовать альтернативный метод.")

# Попытка импортировать mammoth и weasyprint
try:
    import mammoth
    MAMMOTH_AVAILABLE = True
except ImportError:
    MAMMOTH_AVAILABLE = False
    print("Предупреждение: mammoth не доступен. Установите: pip install mammoth")

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError) as e:
    WEASYPRINT_AVAILABLE = False
    print(f"Предупреждение: weasyprint не доступен ({type(e).__name__}). Будет использован альтернативный метод конвертации.")


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
            upload_folder = app.config.get('UPLOAD_FOLDER', 'static/generated_documents') if app else 'static/generated_documents'
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
            upload_folder = app.config.get('UPLOAD_FOLDER', 'static/generated_documents') if app else 'static/generated_documents'
            output_path = os.path.join(upload_folder, f"{document_uuid}.pdf")
        
        # Метод 1: docx2pdf (приоритетный, так как более надежный и не требует GTK+)
        if DOCX2PDF_AVAILABLE:
            try:
                print(f"[INFO] Пытаемся конвертировать через docx2pdf (приоритетный метод)...")
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
            except Exception as e:
                print(f"[WARNING] Ошибка при конвертации через docx2pdf: {e}")
                import traceback
                print(traceback.format_exc())
                print("Примечание: docx2pdf требует установленного LibreOffice или Microsoft Word.")
                print("Пробуем альтернативный метод...")
        
        # Метод 2: mammoth + weasyprint
        if MAMMOTH_AVAILABLE and WEASYPRINT_AVAILABLE:
            try:
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
                            margin: 2cm;
                        }}
                        body {{
                            font-family: 'Times New Roman', serif;
                            font-size: 12pt;
                            line-height: 1.5;
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
                HTML(string=html_with_styles).write_pdf(output_path)
                
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
            except Exception as e:
                print(f"[WARNING] Ошибка при конвертации через mammoth+weasyprint: {e}")
                import traceback
                print(traceback.format_exc())
                print("Пробуем альтернативный метод...")
        
        
        # Если ни один метод не сработал
        print(f"[ERROR] Все методы конвертации DOCX->PDF не удались")
        print(f"[ERROR] MAMMOTH_AVAILABLE={MAMMOTH_AVAILABLE}, WEASYPRINT_AVAILABLE={WEASYPRINT_AVAILABLE}")
        print(f"[ERROR] DOCX2PDF_AVAILABLE={DOCX2PDF_AVAILABLE}")
        print(f"[ERROR] docx_path={docx_path}")
        print(f"[ERROR] output_path={output_path}")
        print(f"[ERROR] Проверьте установку библиотек:")
        print(f"[ERROR]   - pip install mammoth weasyprint")
        print(f"[ERROR]   - pip install docx2pdf (требует LibreOffice или Word)")
        
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

