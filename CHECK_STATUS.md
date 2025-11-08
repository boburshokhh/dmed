# Проверка статуса после установки зависимостей

## Текущая ситуация

✅ `weasyprint` переустановлен (версия 66.0)  
✅ Сервис `dmed` перезапущен  
⚠️ Системные зависимости еще не установлены (apt заблокирован)

## Что делать дальше

### 1. Дождитесь завершения процесса apt

```bash
# Проверьте, завершился ли процесс apt
ps aux | grep apt

# Если процесс еще работает, подождите 1-2 минуты и попробуйте снова
```

### 2. Установите системные зависимости

После того как apt освободится:

```bash
sudo apt-get update
sudo apt-get install -y python3-cffi python3-brotli libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

### 3. Проверьте работу weasyprint

```bash
# Активируйте виртуальное окружение
source .venv/bin/activate

# Проверьте импорт и работу weasyprint
python3 -c "from weasyprint import HTML; HTML(string='<html><body>Test</body></html>').write_pdf('/tmp/test.pdf'); print('OK: weasyprint работает!')"
```

Если команда выполнилась без ошибок и создался файл `/tmp/test.pdf` - все готово!

### 4. Проверьте логи приложения

```bash
# Просмотр логов в реальном времени
sudo journalctl -u dmed -f

# Или последние 50 строк
sudo journalctl -u dmed -n 50 --no-pager
```

### 5. Проверьте работу через веб-интерфейс

1. Откройте https://dmed.gubkin.uz/
2. Заполните форму и создайте документ
3. Если конвертация работает, вы увидите успешное сообщение и сможете скачать PDF

### 6. Если проблема сохраняется

Проверьте логи на наличие ошибок:

```bash
# Ищите ошибки конвертации
sudo journalctl -u dmed | grep -i "error\|weasyprint\|mammoth\|конверт"

# Проверьте доступность библиотек
python3 -c "
from converter import MAMMOTH_AVAILABLE, WEASYPRINT_AVAILABLE, DOCX2PDF_AVAILABLE
print(f'MAMMOTH: {MAMMOTH_AVAILABLE}')
print(f'WEASYPRINT: {WEASYPRINT_AVAILABLE}')
print(f'DOCX2PDF: {DOCX2PDF_AVAILABLE}')
"
```

## Ожидаемый результат

После установки системных зависимостей в логах должно появиться:
```
[OK] DOCX успешно конвертирован в PDF через mammoth+weasyprint
```

А не:
```
[ERROR] Все методы конвертации DOCX->PDF не удались
```

